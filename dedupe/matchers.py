"""Matchers under evaluation.

Every matcher exposes predict(a, b) -> Prediction. The evaluation code does not care
how the answer was produced, so a rule-based baseline and an LLM can be scored the same way.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from .normalize import normalize


@dataclass
class Prediction:
    duplicate: bool | None  # None = the matcher failed to give a usable answer
    reason: str = ""


# ---------------------------------------------------------------- rules baseline
class RulesMatcher:
    """Duplicate if the words overlap enough AND every number-bearing token of one
    description appears in the other. Intentionally basic: it is the baseline to beat."""

    name = "rules"

    def __init__(self, min_word_overlap: float = 0.6):
        self.min_word_overlap = min_word_overlap

    @staticmethod
    def _compact(tokens):
        return re.sub(r"[^A-Z0-9]", "", "".join(tokens))

    def predict(self, a: str, b: str) -> Prediction:
        ta, tb = normalize(a), normalize(b)
        ca, cb = self._compact(ta), self._compact(tb)
        num_a = [re.sub(r"[^A-Z0-9]", "", t) for t in ta if re.search(r"\d", t)]
        num_b = [re.sub(r"[^A-Z0-9]", "", t) for t in tb if re.search(r"\d", t)]
        missing = sorted({n for n in num_a if n and n not in cb} | {n for n in num_b if n and n not in ca})
        words_a = {t for t in ta if not re.search(r"\d", t)}
        words_b = {t for t in tb if not re.search(r"\d", t)}
        union = words_a | words_b
        overlap = len(words_a & words_b) / len(union) if union else 1.0
        if missing:
            return Prediction(False, f"numeric attributes differ: {missing}")
        if overlap < self.min_word_overlap:
            return Prediction(False, f"word overlap {overlap:.2f} < {self.min_word_overlap}")
        return Prediction(True, f"numbers agree, word overlap {overlap:.2f}")


# ---------------------------------------------------------------- LLM matcher
PROMPT_V1 = """Are these two spare-part descriptions the same item?
Reply with JSON only: {{"duplicate": true or false, "reason": "short reason"}}

A: {a}
B: {b}"""

PROMPT_V2 = """You are checking a material master for duplicate records.
Two descriptions are duplicates only if they describe the SAME item: every technical attribute
(type, size, pressure rating, material, grade, voltage, length, part number, manufacturer) must match.
These are NOT differences: word order, abbreviations (SS = stainless steel, CS = carbon steel, FLG = flange),
punctuation, upper/lower case, and unit notation for the same value (2 IN = 50 MM, 1/2" = 1/2 INCH).
If an attribute differs or you are unsure, answer false.
Reply with JSON only: {{"duplicate": true or false, "reason": "short reason"}}

A: {a}
B: {b}"""

PROMPTS = {"v1": PROMPT_V1, "v2": PROMPT_V2}


def build_prompt(version: str, a: str, b: str) -> str:
    return PROMPTS[version].format(a=a, b=b)


def parse_llm_answer(text: str) -> Prediction:
    """Pull {"duplicate": bool, "reason": str} out of a model reply. Never raises."""
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m:
        return Prediction(None, f"no JSON found: {text[:80]!r}")
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return Prediction(None, f"invalid JSON: {text[:80]!r}")
    val = data.get("duplicate")
    if not isinstance(val, bool):
        return Prediction(None, f"'duplicate' missing or not a boolean: {data!r}")
    return Prediction(val, str(data.get("reason", "")))


def _raise_with_body(r):
    """raise_for_status, but keep the provider's own error message (it says WHY: bad model, bad key ...)."""
    import requests

    try:
        r.raise_for_status()
    except requests.HTTPError as exc:
        body = ""
        try:
            body = r.text[:300]
        except Exception:
            pass
        raise requests.HTTPError(f"{exc} | provider says: {body}" if body else str(exc)) from None


def post_with_retry(url, headers, payload, tries=5, sleep=time.sleep):
    """POST JSON, retrying on rate limits (429) and server errors (5xx) with growing waits."""
    import requests

    for attempt in range(tries):
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 429 and r.status_code < 500:
            _raise_with_body(r)
            return r.json()
        if attempt == tries - 1:
            _raise_with_body(r)
        try:
            wait = float(r.headers.get("retry-after", ""))
        except ValueError:
            wait = 2 ** attempt * 2
        sleep(min(wait, 60))


def call_anthropic(prompt: str, model: str) -> str:
    data = post_with_retry(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
         "content-type": "application/json"},
        {"model": model, "max_tokens": 200, "messages": [{"role": "user", "content": prompt}]},
    )
    return data["content"][0]["text"]


def call_groq(prompt: str, model: str) -> str:
    data = post_with_retry(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0},
    )
    return data["choices"][0]["message"]["content"]


PROVIDERS = {"anthropic": call_anthropic, "groq": call_groq}


class LLMMatcher:
    """Asks an LLM. Answers are cached on disk (keyed by model + prompt version + texts),
    so re-running an evaluation is free and reproducible. `call_fn(prompt, model) -> str`
    can be injected, which is how the tests run without any API key."""

    def __init__(self, model: str, prompt_version: str = "v2", provider: str = "anthropic",
                 call_fn=None, cache_path: str | Path | None = ".cache/llm_answers.jsonl"):
        self.model, self.prompt_version, self.provider = model, prompt_version, provider
        self.name = f"llm-{provider}-{model}-{prompt_version}"
        self.call_fn = call_fn or PROVIDERS[provider]
        self.cache_path = Path(cache_path) if cache_path else None
        self.cache: dict[str, str] = {}
        self.api_calls = 0
        self._lock = threading.Lock()
        if self.cache_path and self.cache_path.exists():
            for line in self.cache_path.read_text(encoding="utf-8").splitlines():
                rec = json.loads(line)
                self.cache[rec["key"]] = rec["text"]

    def _key(self, a, b):
        raw = json.dumps([self.provider, self.model, self.prompt_version, a, b])
        return hashlib.sha256(raw.encode()).hexdigest()

    def predict(self, a: str, b: str) -> Prediction:
        key = self._key(a, b)
        if key not in self.cache:
            try:
                text = self.call_fn(build_prompt(self.prompt_version, a, b), self.model)
            except Exception as exc:  # network error, bad key, rate limit after all retries ...
                return Prediction(None, f"API error: {type(exc).__name__}: {str(exc)[:300]}")
            with self._lock:  # several worker threads may finish at once
                self.api_calls += 1
                self.cache[key] = text
                if self.cache_path:
                    self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(self.cache_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps({"key": key, "text": text}) + "\n")
        return parse_llm_answer(self.cache[key])
