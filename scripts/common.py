"""Shared loaders for the CR26 consolidated rules JSON."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cr26"

def load(path=None):
    p = Path(path) if path else DATA / "current.json"
    with open(p) as f:
        return json.load(f)

def version(doc):
    return doc["info"]["version"]

def ksis(doc):
    """Yield (id, theme, indicator) for every KSI."""
    for theme, t in doc["KSI"].items():
        for kid, ind in t["indicators"].items():
            yield kid, theme, ind

def frr_rules(doc):
    """Yield (id, process, applicability, subset, rule)."""
    for proc, p in doc["FRR"].items():
        for app, subs in p.get("data", {}).items():
            for sub, rules in subs.items():
                for rid, r in rules.items():
                    yield rid, proc, app, sub, r

def norm_ctrl(c):
    """Normalize 'AC-02 (03)', 'ac-2.3', 'AC-2(3)' -> 'ac-2.3'."""
    c = c.strip().lower().replace(" (", ".").replace("(", ".").replace(")", "")
    c = re.sub(r"-0(\d)", r"-\1", c)
    c = re.sub(r"\.0(\d)", r".\1", c)
    return c

def class_statement(ind, cls="c"):
    if "varies_by_class" in ind:
        return ind["varies_by_class"].get(cls, {}).get("statement")
    return ind.get("statement")
