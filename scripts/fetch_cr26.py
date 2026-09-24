"""Download the current FedRAMP/rules dataset and store it.
Usage: python scripts/fetch_cr26.py

Uses the codeload tarball (no API rate limit). Compares BYTES, not just the version
string, against data/cr26/current.json:
  - identical bytes              -> nothing written
  - new version string           -> stored as fedramp-consolidated-rules.<version>.json
  - same version, different bytes -> stored as fedramp-consolidated-rules.<version>.<sha8>.json
current.json is always a plain copy (not a symlink; Windows-safe) of the latest bytes.
"""
import hashlib, io, json, tarfile, urllib.request
from common import DATA

URL = "https://codeload.github.com/FedRAMP/rules/tar.gz/main"

def fetch():
    buf = io.BytesIO(urllib.request.urlopen(URL, timeout=60).read())
    rules = schema = None
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        for m in tar.getmembers():
            if m.name.endswith("/fedramp-consolidated-rules.json"):
                rules = tar.extractfile(m).read()
            elif m.name.endswith("/schemas/fedramp-consolidated-rules.schema.json"):
                schema = tar.extractfile(m).read()
    if rules is None:
        raise SystemExit("fedramp-consolidated-rules.json not found in upstream tarball (layout changed?)")
    return rules, schema

def store(rules, schema=None):
    """Store fetched bytes. Returns (status, path) where status is
    'unchanged' | 'new-version' | 'same-version-changed'."""
    cur = DATA / "current.json"
    if cur.exists() and cur.read_bytes() == rules:
        return "unchanged", cur
    ver = json.loads(rules)["info"]["version"]
    out = DATA / f"fedramp-consolidated-rules.{ver}.json"
    status = "new-version"
    if out.exists():
        if out.read_bytes() == rules:          # current.json was stale/hand-edited; resync only
            cur.write_bytes(rules); return "unchanged", out
        out = DATA / f"fedramp-consolidated-rules.{ver}.{hashlib.sha256(rules).hexdigest()[:8]}.json"
        status = "same-version-changed"
    out.write_bytes(rules)
    if schema: (DATA / "fedramp-consolidated-rules.schema.json").write_bytes(schema)
    cur.write_bytes(rules)
    return status, out

def main():
    status, path = store(*fetch())
    print({"unchanged": "no change",
           "new-version": f"stored new version: {path.name}",
           "same-version-changed": f"CONTENT CHANGED WITHOUT VERSION BUMP: {path.name}"}[status])

if __name__ == "__main__":
    main()
