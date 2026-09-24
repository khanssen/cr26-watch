"""Generate a public, facts-only change post for a CR26 release.

Everything the generator writes is [RULE] (CR26 text, quoted or diffed) or [DATA] (computed).
It never writes interpretation. The final "## Analysis" section is left for the author and
the generator never writes into it.

Usage (backfill or local preview):
  python scripts/make_post.py OLD.json NEW.json [--detected YYYY-MM-DD]
Called by check_upstream.py on every detected change.
"""
import datetime as dt, difflib, hashlib, json, re, sys
from pathlib import Path
from common import ROOT, load, utf8_stdout
import diff_versions as dv

POSTS = ROOT / "posts"
ANALYSIS_STUB = ("## Analysis\n\n"
                 "<!-- Author-written. Nothing in this section is generated, and the generator never writes here. "
                 "Mark claims [ANALYSIS]. -->\n\n_No analysis yet._\n")

# ---------- rendering helpers ----------
def md_word_diff(a, b):
    """Full-text word diff: ~~removed~~ **added**."""
    A, B = a.split(), b.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(" ".join(A[i1:i2]))
        else:
            if i2 > i1: out.append("~~" + " ".join(A[i1:i2]) + "~~")
            if j2 > j1: out.append("**" + " ".join(B[j1:j2]) + "**")
    return " ".join(out)

def fmt(v):
    if v is None: return "*(absent)*"
    if isinstance(v, str): return f"`{v}`" if len(v) <= 40 and "\n" not in v else v
    return f"`{json.dumps(v, ensure_ascii=False)}`"

def field_lines(a, b, ignored):
    """Bullets for each changed field between two item bodies."""
    fa, fb = dict(dv.flatten(a)), dict(dv.flatten(b))
    out = []
    for path in sorted(set(fa) | set(fb)):
        if path == "_where": continue
        x, y = fa.get(path), fb.get(path)
        if x == y: continue
        if path == "terms" and isinstance(x, list) and isinstance(y, list) \
                and set(y) <= set(x) and set(x) - set(y) <= ignored:
            continue                                   # derived; summarized elsewhere
        if isinstance(x, str) and isinstance(y, str) and (len(x) > 40 or len(y) > 40):
            tag = " *(whitespace/typo only)*" if dv.cosmetic(x, y) else ""
            out.append(f"- `{path}`{tag}: {md_word_diff(x, y)}")
        elif isinstance(x, list) and isinstance(y, list) and all(isinstance(i, str) for i in x + y):
            add, rem = sorted(set(y) - set(x)), sorted(set(x) - set(y))
            parts = ([f"added {', '.join(f'`{i}`' for i in add)}"] if add else []) + \
                    ([f"removed {', '.join(f'`{i}`' for i in rem)}"] if rem else [])
            out.append(f"- `{path}`: {'; '.join(parts) or 'reordered only'}")
        else:
            out.append(f"- `{path}`: {fmt(x)} → {fmt(y)}")
    return out

def item_title(key, body):
    kind, iid = key.split(":", 1) if ":" in key else ("", key)
    name = body.get("name") or body.get("term") or ""
    return f"`{iid}`" + (f" {name}" if name else "")

def render_added(key, body):
    L = [f"### {item_title(key, body)}", ""]
    if "definition" in body:
        L += [f"> **{body.get('term', '')}**: {body['definition']}", ""]
        if body.get("note"): L += [f"Note: {body['note']}", ""]
    if isinstance(body.get("statement"), str):
        if body.get("force"): L += [f"Force: **{body['force']}**", ""]
        L += [f"> {body['statement']}", ""]
    for cls, cb in (body.get("varies_by_class") or {}).items():
        if isinstance(cb, dict) and cb.get("statement"):
            L += [f"Class {cls.upper()}" + (f" (**{cb['force']}**)" if cb.get("force") else "") + ":", "",
                  f"> {cb['statement']}", ""]
    for fi in body.get("following_information") or []:
        L.append(f"- {fi}")
    if body.get("following_information"): L.append("")
    if body.get("controls"):
        L += [f"Related SP 800-53 controls: {', '.join(f'`{c}`' for c in body['controls'])}", ""]
    shown = {k: v for k, v in body.items() if k != "_where"}
    L += ["<details><summary>All fields</summary>", "", "```json",
          json.dumps(shown, indent=2, ensure_ascii=False), "```", "", "</details>", ""]
    return [l for l in L if l is not None]

def priority(c):
    k = c["key"]
    return (0 if k.startswith("KSI:") and any("`controls`" in l for l in c["lines"]) else
            1 if k == "FRR:FRC-CSF-BSL" or k.startswith("CTL:") else
            2 if c["force"] else 3, k)

# ---------- post ----------
def build_post(old, new, *, old_name, new_name, status, old_sha, new_sha, detected, report_rel=None):
    oi, ni = dv.index(old), dv.index(new)
    md_unused, s = dv.diff(old, new)
    ign = dv.ignored_terms(new) - dv.ignored_terms(old)
    changes = [dv.compare(k, oi[k][0], ni[k][0], oi[k][1], ni[k][1], ign)
               for k in sorted(set(oi) & set(ni)) if oi[k][0] != ni[k][0]]
    meta = [c for c in changes if c["key"] == "INFO" or c["key"].startswith("SET:")]
    items = [c for c in changes if c not in meta]
    subst = sorted((c for c in items if not c["cosmetic"] and not c["derived"]), key=priority)
    cos = [c for c in items if c["cosmetic"]]
    derived = [c for c in items if c["derived"]]
    added = sorted(set(ni) - set(oi)); removed = sorted(set(oi) - set(ni))
    ver, released = new["info"]["version"], new["info"].get("last_updated", "")

    L = [f"<!-- summary: {dv.one_line(s)} -->",
         f"# CR26 {new_name}: what changed", "",
         f"**Dataset version** `{ver}` · **Dataset last_updated** {released} · "
         f"**Detected by cr26-watch** {detected} · **Compared with** `{old_name}`", "",
         "> Everything above **Analysis** is generated from FedRAMP's machine-readable rules and is marked "
         "`[RULE]` (CR26 text, quoted or diffed) or `[DATA]` (computed). It contains no interpretation. "
         "The authoritative source is `fedramp-consolidated-rules.json` in "
         "[FedRAMP/rules](https://github.com/FedRAMP/rules).", ""]
    if status == "same-version-changed":
        L += ["**The dataset's content changed but its version string did not.** `[DATA]`", ""]
    L += ["## Summary `[DATA]`", "",
          "| New | Removed | Substantive | Ruleset-level | KSI mapping | Rev5 baseline/CTL | Normative keyword | Cosmetic | Mechanical |",
          "|---|---|---|---|---|---|---|---|---|",
          "| {added} | {removed} | {substantive} | {meta} | {mapping} | {baseline} | {force} | {cosmetic} | {derived} |".format(**s), ""]

    if meta:
        L += ["## Ruleset-level changes `[RULE]`", "",
              "Status, effective dates, and applicability are set per ruleset. The dataset keeps no change log for them.", ""]
        for c in meta:
            k = c["key"]
            label = "Dataset information" if k == "INFO" else k.split(":", 1)[1]
            body_new = ni[k][0] if k in ni else {}
            if k.startswith("SET:FRR/") and body_new.get("name"): label += f" ({body_new['name']})"
            L += [f"### {label}", ""] + field_lines(oi[k][0], ni[k][0], set()) + [""]

    if added:
        L += ["## New `[RULE]`", ""]
        for k in added: L += render_added(k, ni[k][0])
    if removed:
        L += ["## Removed `[RULE]`", ""]
        for k in removed: L.append(f"- {item_title(k, oi[k][0])}")
        L.append("")
    if subst:
        L += ["## Changed `[RULE]`", "",
              "Word-level changes: ~~removed~~ **added**. Flags: **KSI mapping**, **Rev5 baseline/CTL**, "
              "**normative keyword** (MUST/SHOULD/MAY/NOT/UNLESS or “if applicable” added or removed), "
              "**no change-log entry** (the item's `updated` log was not updated).", ""]
        for c in subst:
            k = c["key"]; flags = []
            if priority(c)[0] == 0: flags.append("KSI mapping")
            if priority(c)[0] == 1: flags.append("Rev5 baseline/CTL")
            if c["force"]: flags.append("normative keyword")
            if c["silent"]: flags.append("no change-log entry")
            L += [f"### {item_title(k, ni[k][0])}" + (f" · *{', '.join(flags)}*" if flags else ""), ""]
            L += field_lines(oi[k][0], ni[k][0], ign) + [""]

    if cos or derived:
        L += ["## Housekeeping `[DATA]`", ""]
        if cos:
            L.append(f"- Whitespace/typo-only text changes ({len(cos)}): " + ", ".join(f"`{c['key'].split(':',1)[1]}`" for c in cos))
        if derived:
            gone = sorted({t for c in derived for t in set(oi[c["key"]][0].get("terms", [])) - set(ni[c["key"]][0].get("terms", []))})
            L.append(f"- {len(derived)} items changed only in their `terms` lists, which no longer include "
                     f"{', '.join(f'“{t}”' for t in gone)}; those definitions are now flagged `ignore_in_terms`. "
                     "No rule text changed on these items.")
        L.append("")

    logged = [c for c in subst if not c["silent"] and c["key"].split(":")[0] in ("FRR", "KSI", "FRD", "CTL")]
    L += ["## Change-log coverage `[DATA]`", "",
          f"- Substantive item changes: {len(subst)}. Of these, {len(subst) - len(logged)} have no new entry in the item's own `updated` log.",
          f"- Ruleset-level changes: {len(meta)}. The dataset has no change log at that level.", ""]

    L += ["## Sources `[DATA]`", "",
          f"- Previous: `data/cr26/` snapshot `{old_name}`, sha256 `{old_sha}`",
          f"- Current: `data/cr26/` snapshot `{new_name}`, sha256 `{new_sha}`"]
    if report_rel: L.append(f"- Full technical diff: [`{report_rel}`](../{report_rel})")
    L += ["- Upstream: [FedRAMP/rules](https://github.com/FedRAMP/rules)", "", "---", "", ANALYSIS_STUB]
    return "\n".join(L), s

def post_path(new, new_name):
    return POSTS / f"{new['info'].get('last_updated', 'undated')}-cr26-{new_name}.md"

def write_index():
    rows = []
    for p in sorted(POSTS.glob("*-cr26-*.md"), reverse=True):
        first = p.read_text(encoding="utf-8").split("\n", 2)
        summ = re.match(r"<!-- summary: (.*) -->", first[0]); title = first[1].lstrip("# ").strip()
        rows.append(f"- [{title}]({p.name}): {summ.group(1) if summ else ''}")
    body = ["# CR26 change posts", "",
            "One post per detected change to FedRAMP's Consolidated Rules for 2026. Newest first.",
            "Facts are generated (`[RULE]`/`[DATA]`); analysis, where present, is the author's (`[ANALYSIS]`).", ""] + rows
    (POSTS / "README.md").write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")

def write_post(old, new, **kw):
    POSTS.mkdir(exist_ok=True)
    text, s = build_post(old, new, **kw)
    p = post_path(new, kw["new_name"])
    if p.exists():                                     # never overwrite the author's Analysis
        head, sep, tail = p.read_text(encoding="utf-8").partition("## Analysis")
        if sep: text = text.partition("## Analysis")[0] + sep + tail
    p.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8", newline="\n")
    write_index()
    return p

def main(argv):
    utf8_stdout()
    det = argv[argv.index("--detected") + 1] if "--detected" in argv else dt.datetime.now(dt.timezone.utc).date().isoformat()
    paths = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i-1] != "--detected")]
    if len(paths) != 2: sys.exit(__doc__)
    ob, nb = Path(paths[0]).read_bytes(), Path(paths[1]).read_bytes()
    name = lambda p: Path(p).stem.split(".", 1)[1] if Path(p).stem.startswith("fedramp-consolidated-rules.") else load(p)["info"]["version"]
    on, nn = name(paths[0]), name(paths[1])
    rep = f"reports/diff.{on}__{nn}.md"
    p = write_post(load(paths[0]), load(paths[1]), old_name=on, new_name=nn,
                   status="same-version-changed" if load(paths[0])["info"]["version"] == load(paths[1])["info"]["version"] else "new-version",
                   old_sha=hashlib.sha256(ob).hexdigest(), new_sha=hashlib.sha256(nb).hexdigest(),
                   detected=det, report_rel=rep if (ROOT / rep).exists() else None)
    print("wrote", p.relative_to(ROOT).as_posix())

if __name__ == "__main__":
    main(sys.argv[1:])
