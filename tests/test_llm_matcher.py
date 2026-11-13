"""Tests for the LLM plumbing. No API key and no network: the model is replaced by a fake function."""
import json

from dedupe.matchers import LLMMatcher, Prediction, build_prompt, parse_llm_answer


def test_parse_clean_json():
    assert parse_llm_answer('{"duplicate": true, "reason": "same part"}') == Prediction(True, "same part")


def test_parse_json_wrapped_in_text_and_code_fence():
    text = 'Sure!\n```json\n{"duplicate": false, "reason": "size differs"}\n```'
    assert parse_llm_answer(text).duplicate is False


def test_parse_failures_return_none_not_a_guess():
    assert parse_llm_answer("I think they are the same").duplicate is None
    assert parse_llm_answer("{not json}").duplicate is None
    assert parse_llm_answer('{"duplicate": "yes"}').duplicate is None  # a string is not a boolean
    assert parse_llm_answer("").duplicate is None


def test_prompt_v2_states_the_matching_rules_and_v1_does_not():
    assert "SAME item" in build_prompt("v2", "A1", "B1")
    assert "SAME item" not in build_prompt("v1", "A1", "B1")
    assert "A1" in build_prompt("v1", "A1", "B1") and "B1" in build_prompt("v1", "A1", "B1")


def test_answers_are_cached(tmp_path):
    calls = []

    def fake(prompt, model):
        calls.append(prompt)
        return '{"duplicate": true, "reason": "ok"}'

    cache = tmp_path / "c.jsonl"
    m1 = LLMMatcher("m", "v2", call_fn=fake, cache_path=cache)
    m1.predict("X", "Y")
    m1.predict("X", "Y")
    assert len(calls) == 1 and m1.api_calls == 1

    m2 = LLMMatcher("m", "v2", call_fn=fake, cache_path=cache)  # a fresh run reads the file
    assert m2.predict("X", "Y").duplicate is True
    assert len(calls) == 1


def test_cache_is_separate_per_model_and_prompt(tmp_path):
    calls = []
    fake = lambda p, m: calls.append(m) or '{"duplicate": false, "reason": ""}'
    cache = tmp_path / "c.jsonl"
    LLMMatcher("model-a", "v1", call_fn=fake, cache_path=cache).predict("X", "Y")
    LLMMatcher("model-b", "v1", call_fn=fake, cache_path=cache).predict("X", "Y")
    LLMMatcher("model-a", "v2", call_fn=fake, cache_path=cache).predict("X", "Y")
    assert len(calls) == 3


def test_full_run_with_a_fake_model_that_always_says_duplicate(tmp_path):
    from dedupe.dataset import load_pairs
    from dedupe.run import evaluate

    always_yes = LLMMatcher("m", "v2", call_fn=lambda p, m: '{"duplicate": true, "reason": "x"}', cache_path=None)
    _, s = evaluate(always_yes, load_pairs())
    assert s["recall"] == 1.0 and s["precision"] == 0.5  # the metric code catches a model that agrees with everything


def test_unusable_answers_are_counted(tmp_path):
    from dedupe.dataset import load_pairs
    from dedupe.run import evaluate

    broken = LLMMatcher("m", "v2", call_fn=lambda p, m: "no idea", cache_path=None)
    _, s = evaluate(broken, load_pairs())
    assert s["unusable_answers"] == s["pairs"]


def test_cache_file_is_valid_jsonl(tmp_path):
    cache = tmp_path / "c.jsonl"
    LLMMatcher("m", "v1", call_fn=lambda p, m: '{"duplicate": true}', cache_path=cache).predict("X", "Y")
    rec = json.loads(cache.read_text().splitlines()[0])
    assert set(rec) == {"key", "text"}


# ---------------------------------------------------------------- failures and retries
def test_api_error_is_reported_not_raised_and_not_cached(tmp_path):
    def boom(prompt, model):
        raise ConnectionError("network down")

    cache = tmp_path / "c.jsonl"
    m = LLMMatcher("m", "v2", call_fn=boom, cache_path=cache)
    p = m.predict("X", "Y")
    assert p.duplicate is None and "ConnectionError" in p.reason
    assert not cache.exists(), "a failed call must not be saved as if it were an answer"


def test_retry_waits_and_succeeds_after_rate_limit(monkeypatch):
    import requests

    from dedupe.matchers import post_with_retry

    class Resp:
        def __init__(self, code, body=None, headers=None):
            self.status_code, self._body, self.headers = code, body or {}, headers or {}

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(str(self.status_code))

        def json(self):
            return self._body

    replies = [Resp(429, headers={"retry-after": "3"}), Resp(503), Resp(200, {"ok": True})]
    monkeypatch.setattr(requests, "post", lambda *a, **k: replies.pop(0))
    waits = []
    assert post_with_retry("u", {}, {}, sleep=waits.append) == {"ok": True}
    assert waits[0] == 3.0 and len(waits) == 2


def test_retry_gives_up_after_all_tries(monkeypatch):
    import pytest
    import requests

    from dedupe.matchers import post_with_retry

    class Resp:
        status_code, headers = 429, {}

        def raise_for_status(self):
            raise requests.HTTPError("429")

    calls = []
    monkeypatch.setattr(requests, "post", lambda *a, **k: calls.append(1) or Resp())
    with pytest.raises(requests.HTTPError):
        post_with_retry("u", {}, {}, tries=3, sleep=lambda s: None)
    assert len(calls) == 3


def test_client_errors_are_not_retried(monkeypatch):
    import pytest
    import requests

    from dedupe.matchers import post_with_retry

    class Resp:
        status_code, headers = 401, {}

        def raise_for_status(self):
            raise requests.HTTPError("401 bad key")

    calls = []
    monkeypatch.setattr(requests, "post", lambda *a, **k: calls.append(1) or Resp())
    with pytest.raises(requests.HTTPError):
        post_with_retry("u", {}, {}, sleep=lambda s: None)
    assert len(calls) == 1


def test_http_error_keeps_the_provider_message(monkeypatch):
    import pytest
    import requests

    from dedupe.matchers import post_with_retry

    class Resp:
        status_code, headers = 404, {}
        text = '{"error": {"message": "The model `llama-9` does not exist", "code": "model_not_found"}}'

        def raise_for_status(self):
            raise requests.HTTPError("404 Client Error: Not Found")

    monkeypatch.setattr(requests, "post", lambda *a, **k: Resp())
    with pytest.raises(requests.HTTPError) as err:
        post_with_retry("u", {}, {}, sleep=lambda s: None)
    assert "model_not_found" in str(err.value)


def test_report_warns_when_answers_are_unusable(tmp_path):
    from dedupe.dataset import load_pairs
    from dedupe.run import evaluate, write_report

    m = LLMMatcher("m", "v2", call_fn=lambda p, mo: "garbage", cache_path=None)
    rows, s = evaluate(m, load_pairs())
    write_report(tmp_path, m.name, rows, s)
    text = (tmp_path / "report.md").read_text()
    assert "WARNING" in text and "unusable" in text


def test_cli_exits_with_error_when_every_answer_fails(tmp_path, capsys, monkeypatch):
    import pytest

    from dedupe import run as runmod

    def boom(prompt, model):
        raise ConnectionError("down")

    import dedupe.matchers as mm
    monkeypatch.setitem(mm.PROVIDERS, "anthropic", boom)
    with pytest.raises(SystemExit):
        runmod.main(["--matcher", "llm", "--model", "x", "--out", str(tmp_path)])
    assert "NOT meaningful" in capsys.readouterr().out


# ---------------------------------------------------------------- parallel workers
def test_parallel_run_gives_identical_results_and_a_clean_cache(tmp_path):
    import json
    import time

    from dedupe.dataset import load_pairs
    from dedupe.run import evaluate

    def slowish(prompt, model):
        time.sleep(0.005)
        return '{"duplicate": %s, "reason": "x"}' % ("true" if len(prompt) % 2 else "false")

    pairs = load_pairs()
    c1, c2 = tmp_path / "seq.jsonl", tmp_path / "par.jsonl"
    rows_seq, s_seq = evaluate(LLMMatcher("m", "v1", call_fn=slowish, cache_path=c1), pairs, workers=1)
    rows_par, s_par = evaluate(LLMMatcher("m", "v1", call_fn=slowish, cache_path=c2), pairs, workers=8)

    assert [r["pred"] for r in rows_seq] == [r["pred"] for r in rows_par]   # same answers, same order
    assert s_seq == s_par
    lines = c2.read_text().splitlines()
    assert len(lines) == len(pairs)
    assert all(set(json.loads(l)) == {"key", "text"} for l in lines)         # no interleaved or torn lines
