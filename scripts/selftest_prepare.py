"""Rewind the LOCAL (runner) baseline so check_upstream.py sees a change on its next run.
Used only by the self-test workflow; nothing it touches is ever committed.
Usage: python scripts/selftest_prepare.py previous-version|synthetic|no-bump

  previous-version  baseline = the prior stored snapshot. Replays the last real release.
  synthetic         baseline = latest snapshot with planted edits: AGU status, one KSI control
                    removed, one MUST -> SHOULD. Exercises every label. Diff reads old -> new,
                    so the report shows those edits being "reverted" by upstream.
  no-bump           same planted edits, but written under the SAME version string, so upstream
                    looks like a content change without a version bump.
"""
import json, sys
from common import DATA

def snapshots():
    return sorted(DATA.glob("fedramp-consolidated-rules.20*.json"))

def plant(doc):
    doc["FRR"]["AGU"]["info"]["status"] = "active" if doc["FRR"]["AGU"]["info"].get("status") != "active" else "placeholder"
    for theme in doc["KSI"].values():
        for kid, ind in theme["indicators"].items():
            if ind.get("controls"):
                ind["controls"] = ind["controls"][1:]; break
        else: continue
        break
    for proc in doc["FRR"].values():
        for subs in proc.get("data", {}).values():
            for rules in subs.values():
                for r in rules.values():
                    if isinstance(r.get("statement"), str) and " MUST " in r["statement"]:
                        r["statement"] = r["statement"].replace(" MUST ", " SHOULD ", 1); return doc
    return doc

def main(mode):
    cur = DATA / "current.json"
    real = cur.read_bytes()
    latest = next((p for p in snapshots() if p.read_bytes() == real), None)
    if latest is None: sys.exit("no stored snapshot matches current.json")
    if mode == "previous-version":
        older = [p for p in snapshots() if p != latest and p.stem < latest.stem]
        if not older: sys.exit("need at least two stored snapshots")
        cur.write_bytes(older[-1].read_bytes()); latest.unlink()
        print(f"baseline rewound to {older[-1].name}; removed {latest.name} (runner only)")
    elif mode in ("synthetic", "no-bump"):
        fake = json.dumps(plant(json.loads(real)), ensure_ascii=False, indent=2).encode("utf-8")
        cur.write_bytes(fake)
        if mode == "synthetic": latest.unlink()
        else: latest.write_bytes(fake)
        print(f"planted edits into baseline ({mode}); runner only")
    else:
        sys.exit(__doc__)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
