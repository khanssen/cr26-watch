"""Regenerate the KSI array embedded in a workpaper HTML tool from CR26 JSON.
Usage: python scripts/sync_workpaper_data.py path/to/tool.html [--class c] [--write]
Without --write: reports differences. With --write: replaces the array in place
and stamps a CR26_VERSION constant.
"""
import sys, re, json
from common import load, ksis, class_statement, norm_ctrl, version

def build(doc, cls):
    return [{"id": kid, "name": ind["name"], "family": theme,
             "family_name": doc["KSI"][theme]["name"],
             "statement": class_statement(ind, cls),
             "controls": ind.get("controls", [])}
            for kid, theme, ind in ksis(doc)]

def main(argv):
    path = argv[0]; cls = argv[argv.index("--class")+1] if "--class" in argv else "c"
    html = open(path).read()
    m = re.search(r'\[\{"id":"KSI-.*?\}\](?=\s*[;,\)])', html, re.S)
    if not m: sys.exit("embedded KSI array not found")
    old = json.loads(m.group(0)); doc = load(); new = build(doc, cls)
    om = {e["id"]: e for e in old}; nm = {e["id"]: e for e in new}
    strip = lambda s: re.sub(r"\*\*.*?\*\*\s*", "", s or "").strip()
    diffs = 0
    for k in sorted(set(om) | set(nm)):
        if k not in om: print("ADD", k); diffs += 1; continue
        if k not in nm: print("REMOVE", k); diffs += 1; continue
        if strip(om[k]["statement"]) != strip(nm[k]["statement"]): print("STATEMENT", k); diffs += 1
        if sorted(map(norm_ctrl, om[k]["controls"])) != sorted(map(norm_ctrl, nm[k]["controls"])): print("CONTROLS", k); diffs += 1
    print(f"{diffs} differences vs CR26 {version(doc)}")
    if "--write" in argv:
        html = html[:m.start()] + json.dumps(new, separators=(",", ":")) + html[m.end():]
        stamp = f'const CR26_VERSION="{version(doc)}";'
        html = re.sub(r'const CR26_VERSION="[^"]*";', stamp, html) if "CR26_VERSION=" in html else html.replace("<script>", "<script>\n" + stamp, 1)
        open(path, "w").write(html); print("written")

if __name__ == "__main__":
    main(sys.argv[1:])
