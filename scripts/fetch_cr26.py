"""Download the current FedRAMP/rules dataset and store it by version.
Usage: python scripts/fetch_cr26.py
Uses the codeload tarball (no API rate limit). Updates data/cr26/current.json
only if the version is new; prints the version either way.
"""
import io, json, os, tarfile, urllib.request
from common import DATA

URL = "https://codeload.github.com/FedRAMP/rules/tar.gz/main"

def main():
    buf = io.BytesIO(urllib.request.urlopen(URL, timeout=60).read())
    rules = schema = None
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        for m in tar.getmembers():
            if m.name.endswith("/fedramp-consolidated-rules.json"):
                rules = tar.extractfile(m).read()
            elif m.name.endswith("/schemas/fedramp-consolidated-rules.schema.json"):
                schema = tar.extractfile(m).read()
    ver = json.loads(rules)["info"]["version"]
    out = DATA / f"fedramp-consolidated-rules.{ver}.json"
    if out.exists():
        print(f"already have {ver}"); return
    out.write_bytes(rules)
    (DATA / "fedramp-consolidated-rules.schema.json").write_bytes(schema)
    link = DATA / "current.json"
    if link.is_symlink() or link.exists(): link.unlink()
    os.symlink(out.name, link)
    print(f"stored new version {ver}; current.json updated")

if __name__ == "__main__":
    main()
