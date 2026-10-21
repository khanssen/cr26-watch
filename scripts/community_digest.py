"""Daily digest of FedRAMP/community GitHub Discussions: every thread with new activity,
rendered whole (question, then every comment and reply in order) with new posts marked.

Why: GitHub's email notifications carry only the new comment, so the answer arrives without
the question. This puts both on one page.

Usage:
  python scripts/community_digest.py                  # live: needs GH_TOKEN (or GITHUB_TOKEN)
  python scripts/community_digest.py --fixture F.json # offline: render from a saved API response
  Options: --since YYYY-MM-DD (override state), --lookback-days N (first run, default 14),
           --out DIR (digest parts, default $RUNNER_TEMP or ./_digest), --no-state

State (data/community/state.json) holds IDs and timestamps only, never post text.
Writes to GITHUB_OUTPUT when set:  changed=true|false  title=<issue title>  parts=<n>  dir=<path>

Output safety, because this text is re-posted into a public issue:
  - @mentions are broken with a zero-width space so nobody gets pinged by the digest.
  - #123 references are broken the same way so they do not link to this repo's issues.
  - github.com links go through redirect.github.com (the Dependabot convention) so the
    digest does not leave a "mentioned this" backreference on FedRAMP's threads every day.
"""
import argparse, datetime as dt, hashlib, json, os, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = Path(os.environ.get("COMMUNITY_STATE") or ROOT / "data" / "community" / "state.json")
OWNER, NAME = "FedRAMP", "community"
API = "https://api.github.com/graphql"
ISSUE_LIMIT = 60000            # GitHub caps issue bodies at 65,536 chars; leave headroom
MAX_PAGES = 8                  # 8 x 20 discussions; a daily window never needs more
ZW = "​"
PMO = {"OWNER", "MEMBER"}      # authorAssociation relative to FedRAMP/community

# Historical-only sources under the project's source-of-truth rules. Flag, never endorse.
SUPERSEDED = [
    (re.compile(r"fedramp\.gov/(?:rfcs?|updates/rfcs)/?", re.I), "links fedramp.gov RFC page"),
    (re.compile(r"fedramp\.gov/notices/?", re.I), "links fedramp.gov notice page"),
    (re.compile(r"fedramp\.gov/legacy/?", re.I), "links fedramp.gov /legacy/ page"),
    (re.compile(r"\bRFC[- ]?0\d{3}\b", re.I), "cites an RFC"),
    (re.compile(r"\bNTC[- ]?\d{4}\b|\bPublic Notice[- ]?\d{2,4}\b", re.I), "cites a public notice"),
    (re.compile(r"\bBIR[- ]?\d+\b"), "cites a BIR"),
]

Q = """
query($owner:String!, $name:String!, $after:String) {
  repository(owner:$owner, name:$name) {
    discussions(first:20, after:$after, orderBy:{field:UPDATED_AT, direction:DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id number title url createdAt updatedAt closed isAnswered
        category { name }
        author { login } authorAssociation body
        answer { id }
        comments(first:100) {
          totalCount
          nodes {
            id url createdAt updatedAt isAnswer
            author { login } authorAssociation body
            replies(first:50) {
              totalCount
              nodes { id url createdAt updatedAt author { login } authorAssociation body }
            }
          }
        }
      }
    }
  }
}"""

def gql(token, variables):
    req = urllib.request.Request(API, data=json.dumps({"query": Q, "variables": variables}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "cr26-watch"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.load(r)
    if out.get("errors"):
        sys.exit(f"GraphQL error: {out['errors']}")
    return out["data"]["repository"]["discussions"]

def fetch(token, since):
    """Discussions ordered by last update, stopping once a whole page predates the window."""
    found, after = [], None
    for _ in range(MAX_PAGES):
        page = gql(token, {"owner": OWNER, "name": NAME, "after": after})
        nodes = page["nodes"]
        found += nodes
        if not page["pageInfo"]["hasNextPage"] or all(ts(n["updatedAt"]) < since for n in nodes):
            break
        after = page["pageInfo"]["endCursor"]
    return found

def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))

def who(node):
    login = (node.get("author") or {}).get("login") or "ghost"
    tag = " · **FedRAMP**" if node.get("authorAssociation") in PMO else ""
    return f"`{login}`{tag}"

def safe(text):
    text = text or ""
    text = re.sub(r"https?://(?:www\.)?github\.com/", "https://redirect.github.com/", text)
    text = re.sub(r"(?<![\w`])@(?=[A-Za-z0-9])", "@" + ZW, text)
    text = re.sub(r"(?<![\w&/])#(?=\d)", "#" + ZW, text)
    return text

def quote(text):
    body = safe(text).strip() or "*(empty)*"
    return "\n".join("> " + line if line else ">" for line in body.splitlines())

def link(url):
    return safe(url)

def flags(text):
    return sorted({label for rx, label in SUPERSEDED if rx.search(text or "")})

def items(d):
    """Every post in thread order: (kind, node, depth)."""
    yield "question", d, 0
    for c in d["comments"]["nodes"]:
        yield "comment", c, 0
        for r in c["replies"]["nodes"]:
            yield "reply", r, 1

def status(node, seen, since):
    prev = seen.get(node["id"])
    if prev is None:
        return "NEW"
    if prev != node["updatedAt"]:
        return "EDITED"
    return ""

def render(d, seen, since):
    """Markdown for one thread, or None if nothing in it is new or edited."""
    rows, any_new, flagged = [], False, []
    head = f"### [{safe(d['title'])}]({link(d['url'])})"
    meta = [d["category"]["name"], "closed" if d["closed"] else "open",
            "answered" if d["isAnswered"] else "unanswered",
            f"{d['comments']['totalCount']} comments"]
    rows.append(head)
    rows.append(f"*{' · '.join(meta)}*")
    if d["comments"]["totalCount"] > len(d["comments"]["nodes"]):
        rows.append(f"*(showing first {len(d['comments']['nodes'])}; open the thread for the rest)*")
    old_block = []
    for kind, n, depth in items(d):
        st = status(n, seen, since)
        if st: any_new = True
        f = flags(n.get("body"))
        if f: flagged.append((n, f))
        label = {"question": "Question", "comment": "Comment", "reply": "↳ Reply"}[kind]
        if kind == "comment" and n.get("isAnswer"):
            label = "✅ Marked answer"
        badge = f" **[{st}]**" if st else ""
        warn = f"\n\n> ⚠️ **Superseded source:** {'; '.join(f)}. Reconcile against CR26 before relying on it." if f else ""
        when = n["createdAt"][:10]
        block = f"**{label}**{badge} — {who(n)}, {when} · [link]({link(n.get('url') or d['url'])})\n\n{quote(n.get('body'))}{warn}"
        if depth:
            block = "\n".join(("> " + l) if l else ">" for l in block.splitlines())
        # Old, unchanged posts after the question fold away so the new ones stand out.
        if not st and kind != "question":
            old_block.append(block)
        else:
            if old_block:
                rows.append(fold(old_block)); old_block = []
            rows.append(block)
    if old_block:
        rows.append(fold(old_block))
    if not any_new:
        return None, []
    return "\n\n".join(rows), flagged

def fold(blocks):
    return (f"<details><summary>{len(blocks)} earlier post(s), unchanged</summary>\n\n"
            + "\n\n---\n\n".join(blocks) + "\n\n</details>")

def split(sections, header):
    """Pack thread sections into issue-sized parts. A single oversized thread is truncated."""
    parts, cur = [], header
    for s in sections:
        if len(s) > ISSUE_LIMIT - len(header) - 200:
            s = s[:ISSUE_LIMIT - len(header) - 400] + "\n\n*(thread truncated; open it on GitHub)*\n\n</details>"
        if len(cur) + len(s) + 10 > ISSUE_LIMIT:
            parts.append(cur); cur = header
        cur += "\n\n---\n\n" + s
    if cur != header:
        parts.append(cur)
    return parts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture"); ap.add_argument("--since"); ap.add_argument("--out")
    ap.add_argument("--lookback-days", type=int, default=14)
    ap.add_argument("--no-state", action="store_true")
    a = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        try: s.reconfigure(encoding="utf-8")
        except AttributeError: pass

    now = dt.datetime.now(dt.timezone.utc)
    state = {} if a.no_state or not STATE.exists() else json.loads(STATE.read_text(encoding="utf-8"))
    seen = state.get("seen", {})
    if a.since:
        since = dt.datetime.fromisoformat(a.since).replace(tzinfo=dt.timezone.utc)
    elif state.get("last_run"):
        since = ts(state["last_run"]) - dt.timedelta(days=2)   # overlap; `seen` dedupes
    else:
        since = now - dt.timedelta(days=a.lookback_days)
    first_run = not seen

    if a.fixture:
        data = json.loads(Path(a.fixture).read_text(encoding="utf-8"))
        discussions = data.get("nodes", data)
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token: sys.exit("set GH_TOKEN (GraphQL needs auth even for public repos)")
        discussions = fetch(token, since)

    sections, n_threads, n_new, n_pmo, n_flag = [], 0, 0, 0, 0
    for d in sorted(discussions, key=lambda d: d["updatedAt"], reverse=True):
        if ts(d["updatedAt"]) < since and not any(n["id"] not in seen for _, n, _ in items(d)):
            continue
        # On the first run only posts inside the lookback window count as new.
        eff_seen = seen if not first_run else {n["id"]: n["updatedAt"] for _, n, _ in items(d) if ts(n["createdAt"]) < since}
        md, flagged = render(d, eff_seen, since)
        new_posts = [n for _, n, _ in items(d) if status(n, eff_seen, since)]
        for _, n, _ in items(d):
            seen[n["id"]] = n["updatedAt"]
        if not md: continue
        n_threads += 1
        n_new += len(new_posts)
        n_pmo += sum(1 for n in new_posts if n.get("authorAssociation") in PMO)
        n_flag += len([n for n, _ in flagged if n in new_posts])
        sections.append(md)

    day = now.date().isoformat()
    title = (f"FedRAMP community digest {day}: {n_threads} thread(s), {n_new} new/edited post(s)"
             + (f", {n_pmo} from FedRAMP" if n_pmo else "")
             + (f", {n_flag} citing superseded sources" if n_flag else ""))
    header = (f"Activity in [FedRAMP/community discussions](https://redirect.github.com/{OWNER}/{NAME}/discussions)"
              f" since {since.date().isoformat()}. Each thread is shown whole; **[NEW]**/**[EDITED]** mark what changed, "
              f"older posts are folded. **FedRAMP** = member of the FedRAMP org on GitHub. "
              f"Discussion answers are not rules: CR26 is the authority.")
    parts = split(sections, header) if sections else []

    out = Path(a.out or os.environ.get("RUNNER_TEMP") or ROOT / "_digest") / "community-digest"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("part-*.md"): old.unlink()
    for i, p in enumerate(parts, 1):
        (out / f"part-{i}.md").write_text(p, encoding="utf-8")

    if not a.no_state and (not a.fixture or os.environ.get("COMMUNITY_STATE")):
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps({"last_run": now.isoformat(timespec="seconds"), "seen": dict(sorted(seen.items()))},
                                    indent=1) + "\n", encoding="utf-8")

    print(title if parts else "no new community activity", f"({len(parts)} part(s) in {out})")
    go = os.environ.get("GITHUB_OUTPUT")
    if go:
        with open(go, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if parts else 'false'}\ntitle={title}\nparts={len(parts)}\ndir={out}\n")

if __name__ == "__main__":
    main()
