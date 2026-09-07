"""Fetch upstream, detect a new version OR a content change without a version bump,
diff against the previous snapshot, write a report, and print a summary line
for the CI job to use. Exit 0 always; sets GITHUB_OUTPUT changed=true|false.
"""
import hashlib, os, subprocess, sys
from pathlib import Path
from common import DATA, ROOT, load, version

def snapshots():
    return sorted(p for p in DATA.glob("fedramp-consolidated-rules.20*.json"))

def main():
    before = snapshots()
    prev = before[-1] if before else None
    prev_hash = hashlib.sha256(prev.read_bytes()).hexdigest() if prev else None
    subprocess.run([sys.executable, ROOT / "scripts/fetch_cr26.py"], check=True)
    after = snapshots()
    cur = DATA / "current.json"
    cur_hash = hashlib.sha256(cur.read_bytes()).hexdigest()
    changed = (len(after) > len(before)) or (cur_hash != prev_hash)
    if changed and prev and len(after) == len(before):
        # same version string, different bytes: store it with a hash suffix so it is not lost
        ver = version(load(cur))
        alt = DATA / f"fedramp-consolidated-rules.{ver}.{cur_hash[:8]}.json"
        alt.write_bytes(cur.read_bytes()); after.append(alt)
        note = f"CONTENT CHANGED WITHOUT VERSION BUMP ({ver})"
    else:
        note = f"new version {version(load(cur))}" if changed else "no change"
    report = ""
    if changed and prev:
        out = subprocess.run([sys.executable, ROOT / "scripts/diff_versions.py", prev, after[-1]],
                             capture_output=True, text=True, check=True).stdout
        rp = ROOT / "reports" / f"diff.{prev.stem.split('.',1)[1]}__{after[-1].stem.split('.',1)[1]}.md"
        rp.write_text(f"> {note}\n\n" + out); report = str(rp.relative_to(ROOT))
        stats = subprocess.run([sys.executable, ROOT / "scripts/mapping_stats.py"], capture_output=True, text=True).stdout
        (ROOT / "reports" / f"mapping-stats.{version(load(cur))}.md").write_text(stats)
    print(note, report)
    go = os.environ.get("GITHUB_OUTPUT")
    if go:
        with open(go, "a") as f:
            f.write(f"changed={'true' if changed else 'false'}\nnote={note}\nreport={report}\n")

if __name__ == "__main__":
    main()
