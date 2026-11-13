"""Text normalisation used by the rule-based baseline.

Deliberately simple: it expands common abbreviations and splits number+unit tokens.
It does NOT convert between unit systems (2 IN vs 50 MM), which is one of the
cases the evaluation is designed to expose.
"""
import re

ABBREV = {
    "BRG": "BEARING", "GSKT": "GASKET", "WND": "WOUND", "SS": "STAINLESS STEEL",
    "CS": "CARBON STEEL", "FLG": "FLANGE", "WN": "WELD NECK", "GALV": "GALVANIZED",
    "CONC": "CONCENTRIC", "BW": "BUTT WELD", "DEG": "DEGREE", "HEXAGON": "HEX",
    "INCH": "IN", "INCHES": "IN", "MILLIMETER": "MM", "MILLIMETRE": "MM",
    "NITRILE": "NBR", "POLE": "P",
}
STOPWORDS = {"OF", "THE", "AND", "TO"}
UNITS = r"(?:MM2|MM|CM|M|IN|A|V|W|KG|P|BAR|MA|VDC|VAC|MICRON|UNC|DEG|CORE)"


def normalize(text: str) -> list[str]:
    t = text.upper().replace('"', " IN ")
    t = re.sub(r"(\d+)#", r"CLASS \1", t)
    t = re.sub(r"\bV[- ]BELT\b", "VBELT", t)
    t = re.sub(r"\bO[- ]RING\b", "ORING", t)
    t = re.sub(r"\bM(\d+)X(\d+)\b", r"M\1 X \2", t)
    t = re.sub(r"(?<=\d)X(?=\d)", " X ", t)
    t = re.sub(r"\b(SS|CS)(\d+)\b", r"\1 \2", t)
    tokens = re.findall(r"[A-Z0-9./]+", t)
    out: list[str] = []
    for tok in tokens:
        m = re.fullmatch(rf"(\d+(?:\.\d+)?)({UNITS})", tok)
        parts = [m.group(1), m.group(2)] if m else [tok]
        for p in parts:
            expanded = ABBREV.get(p, p)
            out.extend(w for w in expanded.split() if w and w not in STOPWORDS)
    return out
