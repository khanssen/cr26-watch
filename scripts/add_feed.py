#!/usr/bin/env python3
r"""
add_feed.py — register a feed file in an engagement's manifest with its hashes.

Usage:
    python scripts\add_feed.py "<engagement dir>" feeds\sdr-2026-08-05.json
    python scripts\add_feed.py "<engagement dir>" feeds\sdr-2026-08-05.json --tool-commit 43b6343

Reads the feed's own `feed` block for kind / published / source hash, computes
SHA-256 of the feed file as it sits on disk, and appends (or replaces, if the
same path is already listed) an entry in engagement.json. Also stamps
`tool` with the tooling-repo commit if --tool-commit is given, or detects it
from `git rev-parse --short HEAD` in the repo this script lives in.

The manifest is written atomically. Never edits the feed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(p: Path, text: str):
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=f".{p.name}.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, p)


def tool_commit() -> str | None:
    try:
        repo = Path(__file__).resolve().parent.parent
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("engagement_dir", type=Path)
    ap.add_argument("feed", type=Path, help="feed path, relative to engagement dir (or absolute)")
    ap.add_argument("--tool-commit", help="tooling repo commit to stamp (default: detect)")
    args = ap.parse_args()

    eng = args.engagement_dir.resolve()
    manifest_path = eng / "engagement.json"
    if not manifest_path.exists():
        sys.exit(f"no engagement.json in {eng}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    feed_path = args.feed if args.feed.is_absolute() else (eng / args.feed)
    feed_path = feed_path.resolve()
    if not feed_path.exists():
        sys.exit(f"feed not found: {feed_path}")
    rel = feed_path.relative_to(eng).as_posix()

    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    fb = feed.get("feed", {})
    entry = {
        "kind": fb.get("kind"),
        "path": rel,
        "published": fb.get("published"),
        "sha256": sha256_file(feed_path),
        "source_file": fb.get("source_file"),
        "source_sha256": fb.get("source_sha256"),
        "published_sha256": fb.get("published_sha256"),
        "parser": fb.get("parser"),
        "registered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    feeds = manifest.setdefault("feeds", [])
    replaced = False
    for i, e in enumerate(feeds):
        if e.get("path") == rel:
            feeds[i] = entry; replaced = True
    if not replaced:
        feeds.append(entry)

    commit = args.tool_commit or tool_commit()
    if commit:
        manifest["tool"] = f"fedramp-20x-eval@{commit}"

    atomic_write(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"{'replaced' if replaced else 'added'} {rel}  kind={entry['kind']}  sha256={entry['sha256'][:12]}…  tool={manifest.get('tool')}")


if __name__ == "__main__":
    main()
