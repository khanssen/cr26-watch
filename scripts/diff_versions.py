"""Diff two CR26 JSON versions.
Usage: python scripts/diff_versions.py OLD.json NEW.json [--out report.md]
Exit code: 0 = no mapping change; 2 = a KSI was added/removed or a KSI controls array changed.
  --out writes UTF-8 directly (use it on Windows PowerShell 5.1, where `>` writes UTF-16).

Compares, per item, the FULL body minus the `updated` changelog:
  INFO:             top-level dataset info (default_artifacts etc.)
  SET:FRR/<id>      ruleset metadata -- status, purpose, effective dates, subsets/applicability
  SET:KSI/<theme>   KSI theme metadata
  SET:FRD           definitions metadata
  FRR:/KSI:/FRD:/CTL: individual items

Each change is classed:
  substantive  -- anything not provably cosmetic
  cosmetic     -- text identical after normalizing whitespace, quote/dash glyphs, and doubled words
  derived      -- `terms` list lost only terms whose definition now carries ignore_in_terms=true
                  (a single definition flag cascades into hundreds of rules; reported once, as a count)
Flags:
  FORCE   the edit adds/removes a normative keyword (MUST, SHOULD, MAY, NOT, UNLESS, REQUIRED, OPTIONAL)
          or "if applicable", or changes a `force` field
  SILENT  the item changed but its `updated` changelog did not (KSI -> 800-53 mapping changes
          always land here; the dataset never logs them)
"""
import difflib, json, re, sys, unicodedata
from common import load, ksis, frr_rules, norm_ctrl, utf8_stdout

FORCE_WORDS = {"MUST", "SHOULD", "MAY", "NOT", "UNLESS", "REQUIRED", "OPTIONAL", "SHALL"}
GLYPHS = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
                        "\u2013": "-", "\u2014": "-", "\u00a0": " "})

# ---------- indexing ----------
def _strip(d, drop=("updated",)):
    return {k: v for k, v in d.items() if k not in drop}

def index(doc):
    """-> {key: (body_without_updated, updated_list)}"""
    out = {}
    out["INFO"] = (_strip(doc["info"], ("version", "last_updated")), None)
    for proc, p in doc["FRR"].items():
        out[f"SET:FRR/{proc}"] = (p.get("info", {}), None)
    for theme, t in doc["KSI"].items():
        out[f"SET:KSI/{theme}"] = (_strip(t, ("indicators",)), None)
    out["SET:FRD"] = (doc["FRD"].get("info", {}), None)
    for rid, proc, app, sub, r in frr_rules(doc):
        out[f"FRR:{rid}"] = (dict(_strip(r), _where=f"{proc}/{app}/{sub}"), r.get("updated"))
    for kid, theme, ind in ksis(doc):
        body = _strip(ind)
        if "controls" in body:
            body["controls"] = sorted(norm_ctrl(c) for c in body["controls"])
        out[f"KSI:{kid}"] = (body, ind.get("updated"))
    for app, defs in doc["FRD"]["data"].items():
        for fid, d in defs.items():
            out[f"FRD:{fid}"] = (dict(_strip(d), _where=app), d.get("updated"))
    for fam, ctrls in doc.get("CTL", {}).items():
        for cid, body in ctrls.items():
            out[f"CTL:{cid}"] = (_strip(body), body.get("updated"))
    return out

# ---------- comparison ----------
def flatten(x, path=""):
    if isinstance(x, dict):
        if not x: yield path, {}
        for k, v in x.items():
            yield from flatten(v, f"{path}.{k}" if path else k)
    else:
        yield path, x          # lists compared whole (controls handled specially)

def norm_text(s):
    s = unicodedata.normalize("NFKC", s).translate(GLYPHS)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\b(\w+)( \1\b)+", r"\1", s, flags=re.I)   # "the the" -> "the"
    return s

def cosmetic(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return norm_text(a) == norm_text(b)
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return all(cosmetic(x, y) for x, y in zip(a, b))
    return False

def word_diff(a, b):
    """Inline word diff: [-removed-] {+added+}. Returns (text, removed_tokens, added_tokens)."""
    A, B = a.split(), b.split()
    out, rem, add = [], [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op == "equal":
            seg = A[i1:i2]
            out.append(" ".join(seg) if len(seg) <= 8 else " ".join(seg[:4]) + " … " + " ".join(seg[-4:]))
        else:
            if i2 > i1: out.append("[-" + " ".join(A[i1:i2]) + "-]"); rem += A[i1:i2]
            if j2 > j1: out.append("{+" + " ".join(B[j1:j2]) + "+}"); add += B[j1:j2]
    return " ".join(out), rem, add

def touches_force(tokens):
    t = " ".join(tokens)
    return any(w.strip("(),.;:") in FORCE_WORDS for w in tokens) or "applicable" in t.lower()

def short(v, n=160):
    s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    return s if len(s) <= n else s[:n] + "…"

def ignored_terms(doc):
    return {d.get("term") for defs in doc["FRD"]["data"].values() for d in defs.values() if d.get("ignore_in_terms")}

def compare(key, a, b, ua, ub, ignored=frozenset()):
    """-> dict(key, cosmetic, derived, force, silent, lines)"""
    fa, fb = dict(flatten(a)), dict(flatten(b))
    lines, force, all_cos, all_der, real = [], False, True, True, False
    for path in sorted(set(fa) | set(fb)):
        x, y = fa.get(path, None), fb.get(path, None)
        if x == y: continue
        if path == "terms" and isinstance(x, list) and isinstance(y, list) \
                and set(y) <= set(x) and set(x) - set(y) <= ignored:
            lines.append(f"    - `terms` *(derived)*: -{sorted(set(x)-set(y))}")
            continue
        all_der = False
        cos = path in fa and path in fb and cosmetic(x, y)
        all_cos &= cos; real |= not cos
        tag = " *(cosmetic)*" if cos else ""
        if isinstance(x, list) and isinstance(y, list) and all(isinstance(i, str) for i in x + y) \
                and (path.endswith("controls") or len(x) + len(y) > 6 or set(x) != set(y)):
            add, rem = sorted(set(y) - set(x)), sorted(set(x) - set(y))
            what = f"+{add} -{rem}" if (add or rem) else "reordered only"
            lines.append(f"    - `{path}`{tag}: {what}")
        elif isinstance(x, str) and isinstance(y, str):
            txt, rem, add = word_diff(x, y)
            if not cos and touches_force(rem + add): force = True
            lines.append(f"    - `{path}`{tag}: {txt}")
        else:
            if path.endswith("force"): force = True
            lines.append(f"    - `{path}`{tag}: {short(x)} → {short(y)}")
    silent = ua is not None and ua == ub and real
    return dict(key=key, cosmetic=all_cos and not all_der, derived=all_der, force=force, silent=silent, lines=lines)

# ---------- report ----------
def diff(old, new):
    oi, ni = index(old), index(new)
    added = sorted(set(ni) - set(oi)); removed = sorted(set(oi) - set(ni))
    ign = ignored_terms(new) - ignored_terms(old)
    changes = [compare(k, oi[k][0], ni[k][0], oi[k][1], ni[k][1], ign)
               for k in sorted(set(oi) & set(ni)) if oi[k][0] != ni[k][0]]
    meta = [c for c in changes if c["key"] == "INFO" or c["key"].startswith("SET:")]
    items = [c for c in changes if c not in meta]
    derived = [c for c in items if c["derived"]]
    subst = [c for c in items if not c["cosmetic"] and not c["derived"]]
    cos = [c for c in items if c["cosmetic"]]
    summary = dict(added=len(added), removed=len(removed), substantive=len(subst), cosmetic=len(cos),
                   derived=len(derived),
                   meta=sum(not c["cosmetic"] for c in meta), force=sum(c["force"] for c in changes),
                   silent=sum(c["silent"] for c in items),
                   mapping=sum(c["key"].startswith("KSI:") and any("`controls`" in l for l in c["lines"]) for c in items)
                           + sum(1 for k in added + removed if k.startswith("KSI:")),
                   baseline=sum(1 for c in subst if c["key"] == "FRR:FRC-CSF-BSL" or c["key"].startswith("CTL:"))
                            + sum(1 for k in added + removed if k.startswith("CTL:")))
    L = [f"# CR26 diff {old['info']['version']} -> {new['info']['version']}", "",
         "| added | removed | substantive | ruleset/info | mapping | baseline | force-bearing | silent | cosmetic | derived |",
         "|---|---|---|---|---|---|---|---|---|---|",
         "| {added} | {removed} | {substantive} | {meta} | {mapping} | {baseline} | {force} | {silent} | {cosmetic} | {derived} |".format(**summary), ""]
    def block(title, cs):
        if not cs: return
        L.append(f"## {title}")
        for c in cs:
            flags = " ".join(f for f, on in (("**FORCE**", c["force"]), ("**SILENT**", c["silent"])) if on)
            L.append(f"- {c['key']} {flags}".rstrip()); L.extend(c["lines"])
        L.append("")
    block("Ruleset / dataset metadata", meta)
    if added: L += ["## Added"] + [f"- {k}" for k in added] + [""]
    if removed: L += ["## Removed"] + [f"- {k}" for k in removed] + [""]
    block("Substantive", subst)
    block("Cosmetic (normalized text identical)", cos)
    if derived:
        gone = sorted({t for c in derived for t in set(oi[c["key"]][0].get("terms", [])) - set(ni[c["key"]][0].get("terms", []))})
        L += [f"## Derived", f"- {len(derived)} items: `terms` lost only {gone} "
              f"(definitions now flagged `ignore_in_terms`). No other field changed on these items.", ""]
    if not (changes or added or removed): L.append("No differences.")
    L += ["---", "*FORCE* = normative keyword or `force` changed. *SILENT* = body changed, `updated` log did not."]
    return "\n".join(L) + "\n", summary

def one_line(s):
    parts = [f"{s['substantive']} substantive"]
    for k, lab in (("meta", "ruleset"), ("added", "added"), ("removed", "removed"), ("mapping", "MAPPING"), ("baseline", "BASELINE"),
                   ("force", "force-bearing"), ("silent", "silent"), ("cosmetic", "cosmetic"), ("derived", "derived")):
        if s[k]: parts.append(f"{s[k]} {lab}")
    return ", ".join(parts)

def main(argv):
    utf8_stdout()
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    paths = [a for i, a in enumerate(argv) if a != "--out" and (i == 0 or argv[i-1] != "--out")]
    if len(paths) != 2: sys.exit(__doc__)
    md, s = diff(load(paths[0]), load(paths[1]))
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as f: f.write(md)
        print(f"wrote {out}: {one_line(s)}")
    else:
        sys.stdout.write(md)
    return 2 if s["mapping"] else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
