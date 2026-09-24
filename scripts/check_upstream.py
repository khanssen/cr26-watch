"""Fetch upstream; if the bytes differ from data/cr26/current.json (new version OR same version
with changed content), diff old -> new, write reports, and emit outputs for the CI job.
Exit 0 always. Writes to GITHUB_OUTPUT when set:
  changed=true|false  note=<issue title>  report=<path>  labels=<comma list>
"""
import hashlib, os, re, subprocess, sys, tempfile
from pathlib import Path
from common import DATA, ROOT, load, version, utf8_stdout
import datetime as dt
import fetch_cr26, diff_versions, make_post

# Upstream-derived strings reach git refs, commit messages, and CI outputs. Only this shape passes.
SAFE_NAME = re.compile(r"\d{4}\.\d{2}\.\d{2}\.\d{2}(\.[0-9a-f]{8})?")

def safe(name):
    if not SAFE_NAME.fullmatch(name):
        sys.exit(f"refusing unexpected version/snapshot name {name!r}: expected YYYY.MM.DD.NN[.sha8]")
    return name

def snapshot_name(data: bytes, fallback: str) -> str:
    """The versioned snapshot whose bytes match, as '<version>[.<sha8>]'; else fallback."""
    for p in DATA.glob("fedramp-consolidated-rules.20*.json"):
        if p.read_bytes() == data:
            return p.stem.split(".", 1)[1]
    return fallback

def main():
    utf8_stdout()
    cur = DATA / "current.json"
    old_bytes = cur.read_bytes() if cur.exists() else None
    status, new_path = fetch_cr26.store(*fetch_cr26.fetch())
    changed = status != "unchanged"
    note, report, labels, post = "no change", "", [], ""

    if changed and old_bytes:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as t:
            t.write(old_bytes); old_tmp = t.name
        old_doc, new_doc = load(old_tmp), load(new_path)
        md, s = diff_versions.diff(old_doc, new_doc)
        old_name = safe(snapshot_name(old_bytes, version(old_doc)))
        new_name = safe(new_path.stem.split(".", 1)[1])
        head = ("CONTENT CHANGED WITHOUT VERSION BUMP" if status == "same-version-changed"
                else "new version") + f" {new_name}"
        note = f"{head}: {diff_versions.one_line(s)}"
        rp = ROOT / "reports" / f"diff.{old_name}__{new_name}.md"
        rp.write_text(f"> {note}\n\n" + md, encoding="utf-8")
        report = str(rp.relative_to(ROOT)).replace("\\", "/")
        stats = subprocess.run([sys.executable, str(ROOT / "scripts" / "mapping_stats.py"), str(new_path)],
                               capture_output=True, text=True, encoding="utf-8").stdout
        (ROOT / "reports" / f"mapping-stats.{new_name}.md").write_text(stats, encoding="utf-8")
        pp = make_post.write_post(
            old_doc, new_doc, old_name=old_name, new_name=new_name, status=status,
            old_sha=hashlib.sha256(old_bytes).hexdigest(), new_sha=hashlib.sha256(new_path.read_bytes()).hexdigest(),
            detected=dt.datetime.now(dt.timezone.utc).date().isoformat(), report_rel=report)
        post = pp.relative_to(ROOT).as_posix()
        labels = ["cr26-change"]
        if s["mapping"]: labels.append("cr26-mapping")
        if s["baseline"]: labels.append("cr26-baseline")
        if s["meta"]: labels.append("cr26-ruleset")
        if s["force"]: labels.append("cr26-force")
        if status == "same-version-changed": labels.append("cr26-no-version-bump")
        os.unlink(old_tmp)
    elif changed:
        note = f"initial snapshot {new_path.stem.split('.', 1)[1]}"

    print(note, report)
    go = os.environ.get("GITHUB_OUTPUT")
    if go:
        with open(go, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\nnote={note}\n"
                    f"report={report}\nlabels={','.join(labels)}\npost={post}\n"
                    f"name={safe(new_path.stem.split('.', 1)[1]) if changed else ''}\n")

if __name__ == "__main__":
    main()
