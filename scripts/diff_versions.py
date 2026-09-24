"""Diff two CR26 JSON versions at the rule/KSI/definition/CTL level.
Usage: python scripts/diff_versions.py OLD.json NEW.json
Mapping (controls-array) changes have NO `updated` history in the dataset;
this script is the only way to see them.
Exit code: 0 = no mapping change; 2 = a KSI was added/removed or a controls array changed.
"""
import sys
from common import load, ksis, frr_rules, norm_ctrl, class_statement

def index(doc):
    out = {}
    for rid, proc, app, sub, r in frr_rules(doc):
        st = r.get("statement") or {k: v.get("statement") for k, v in r.get("varies_by_class", {}).items()}
        out[f"FRR:{rid}"] = {"statement": st, "force": r.get("force"), "app": app, "sub": sub,
                             "notes": r.get("notes", []), "fi": r.get("following_information", [])}
    for kid, theme, ind in ksis(doc):
        out[f"KSI:{kid}"] = {"statement": {c: class_statement(ind, c) for c in "abcd"},
                             "controls": sorted(norm_ctrl(c) for c in ind.get("controls", []))}
    for fid, d in doc["FRD"]["data"].get("all", {}).items():
        out[f"FRD:{fid}"] = {"term": d["term"], "definition": d["definition"]}
    for fam, ctrls in doc.get("CTL", {}).items():
        for cid, body in ctrls.items():
            out[f"CTL:{cid}"] = body
    return out

def main(old_p, new_p):
    old, new = load(old_p), load(new_p)
    oi, ni = index(old), index(new)
    print(f"# CR26 diff {old['info']['version']} -> {new['info']['version']}\n")
    added = sorted(set(ni) - set(oi)); removed = sorted(set(oi) - set(ni))
    mapping_changed = any(k.startswith("KSI:") for k in added + removed)
    if added: print("## Added\n" + "\n".join(f"- {k}" for k in added) + "\n")
    if removed: print("## Removed\n" + "\n".join(f"- {k}" for k in removed) + "\n")
    print("## Changed")
    n = 0
    for k in sorted(set(oi) & set(ni)):
        a, b = oi[k], ni[k]
        if a == b: continue
        n += 1
        fields = sorted(f for f in set(a) | set(b) if a.get(f) != b.get(f))
        print(f"- {k}: {', '.join(fields)}")
        if k.startswith("KSI:") and a.get("controls") != b.get("controls"):
            mapping_changed = True
            print(f"    controls +{sorted(set(b['controls'])-set(a['controls']))} -{sorted(set(a['controls'])-set(b['controls']))}")
    if not n: print("- (none)")
    return mapping_changed

if __name__ == "__main__":
    sys.exit(2 if main(*sys.argv[1:3]) else 0)
