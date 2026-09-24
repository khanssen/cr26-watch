#!/usr/bin/env python3
r"""
serve.py — loopback server for classc-workpapers.

Serves two roots on 127.0.0.1:
    /                → the tooling repo (this file's parent's parent by default)
    /engagements/    → the engagements root (Kompleye OneDrive, a share, a local dir)

Writes are allowed ONLY under /engagements/<client>/ and ONLY to:
    workpaper.json
    exports/<anything>
and are atomic (temp file + os.replace) so a sync client never sees a partial file.

Usage (PowerShell):
    python scripts\serve.py --engagements "C:\Users\khans\OneDrive - Kompleye Attestation LLC\20x"
    # then open:
    #   http://127.0.0.1:8000/tools/classc-workpapers.html?engagement=IVM

Nothing here is reachable off-box; it binds loopback only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import sys
import tempfile
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

def _iso(ts):
    from datetime import datetime, timezone
    dt = datetime.fromtimestamp(ts, timezone.utc) if ts is not None else datetime.now(timezone.utc)
    return dt.isoformat(timespec="seconds")


WRITABLE_FILES = {"workpaper.json", "review.json", "engagement.json"}
WRITABLE_DIRS = {"exports", "feeds"}


class Handler(SimpleHTTPRequestHandler):
    tool_root: Path
    eng_root: Path
    mirror_root: Path | None = None

    # ---- path resolution -------------------------------------------------
    def _resolve(self, url_path: str) -> tuple[Path | None, Path | None, str]:
        """Return (filesystem_path, root, rel) or (None, None, reason)."""
        p = urllib.parse.unquote(urllib.parse.urlsplit(url_path).path)
        p = posixpath.normpath(p)
        if p.startswith("/engagements/") or p == "/engagements":
            rel = p[len("/engagements"):].lstrip("/")
            root = self.eng_root
        else:
            rel = p.lstrip("/")
            root = self.tool_root
        fs = (root / rel).resolve()
        try:
            fs.relative_to(root.resolve())
        except ValueError:
            return None, None, "path escapes root"
        return fs, root, rel

    def translate_path(self, path: str) -> str:  # used by GET/HEAD
        fs, _, _ = self._resolve(path)
        return str(fs) if fs else "/nonexistent"

    # ---- headers ---------------------------------------------------------
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.command, fmt % args))

    # ---- GET: directory listing of engagements root as JSON --------------
    def do_GET(self):
        fs, root, rel = self._resolve(self.path)
        if fs is None:
            return self.send_error(HTTPStatus.FORBIDDEN, root)
        qs = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        if root == self.eng_root and fs.is_dir() and qs.get("inventory"):
            # recursive walk with hashes: the view builds a trustcenter-inventory feed from a mirrored folder
            do_hash = qs.get("hash", ["1"])[0] != "0"
            if qs.get("mirror"):
                # walk the OneDrive replica named in the manifest instead of a folder inside the engagement
                parts = Path(rel).parts
                man = self.eng_root / parts[0] / "engagement.json" if parts else None
                if not (man and man.exists()):
                    return self.send_error(HTTPStatus.NOT_FOUND, "no engagement.json for mirror walk")
                lp = (qs.get("lp") or [None])[0] or json.loads(man.read_text(encoding="utf-8")).get("trust_center", {}).get("local_path")
                if not lp:
                    return self.send_error(HTTPStatus.BAD_REQUEST, "trust_center.local_path not set in engagement.json")
                if self.mirror_root is None:
                    return self.send_error(HTTPStatus.FORBIDDEN, "server started without --mirror-root; mirror walks are off")
                target = Path(lp).expanduser()
                if not target.is_absolute():
                    target = self.mirror_root / target
                target = target.resolve()
                try:
                    target.relative_to(self.mirror_root)
                except ValueError:
                    return self.send_error(HTTPStatus.FORBIDDEN, f"local_path is outside --mirror-root ({self.mirror_root})")
                if not target.is_dir():
                    return self.send_error(HTTPStatus.NOT_FOUND, f"local_path not found: {target}")
                fs = target
            items = []
            for dirpath, dirnames, filenames in os.walk(fs):
                dirnames.sort(); filenames.sort()
                dp = Path(dirpath)
                for d in dirnames:
                    p = dp / d
                    items.append({"path": p.relative_to(fs).as_posix(), "name": d, "type": "folder",
                                  "modified": _iso(p.stat().st_mtime)})
                for fn in filenames:
                    if fn.startswith("~$") or fn.startswith("."): continue
                    p = dp / fn; st = p.stat()
                    rec = {"path": p.relative_to(fs).as_posix(), "name": fn, "type": "file",
                           "size": st.st_size, "modified": _iso(st.st_mtime), "sha256": None}
                    if do_hash:
                        h = hashlib.sha256()
                        with p.open("rb") as f:
                            for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
                        rec["sha256"] = h.hexdigest()
                    items.append(rec)
            body = json.dumps({"path": "/engagements/" + rel, "root": str(fs), "hashed": do_hash,
                               "walked_at": _iso(None), "items": items}).encode()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if root == self.eng_root and fs.is_dir():
            # JSON listing so the HTML can offer an engagement picker
            entries = []
            for child in sorted(fs.iterdir()):
                if child.name.startswith("."):
                    continue
                entries.append({"name": child.name, "dir": child.is_dir(),
                                "size": child.stat().st_size if child.is_file() else None})
            body = json.dumps({"path": "/engagements/" + rel, "entries": entries}).encode()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    # ---- PUT: atomic write, engagement root only, allow-listed targets ---
    def do_PUT(self):
        fs, root, rel = self._resolve(self.path)
        if fs is None or root != self.eng_root:
            return self.send_error(HTTPStatus.FORBIDDEN, "writes only under /engagements/")
        parts = Path(rel).parts
        if len(parts) < 2:
            return self.send_error(HTTPStatus.FORBIDDEN, "target must be /engagements/<client>/...")
        client, sub = parts[0], parts[1:]
        ok = (len(sub) == 1 and sub[0] in WRITABLE_FILES) or (sub[0] in WRITABLE_DIRS and len(sub) >= 2)
        if not ok:
            return self.send_error(HTTPStatus.FORBIDDEN,
                                   f"not writable: {rel} (allowed: {sorted(WRITABLE_FILES)}, {sorted(WRITABLE_DIRS)}/*)")
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length)
        if fs.suffix == ".json":
            try:
                json.loads(data)
            except ValueError as e:
                return self.send_error(HTTPStatus.BAD_REQUEST, f"invalid JSON: {e}")
        fs.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=fs.parent, prefix=f".{fs.name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, fs)          # atomic on NTFS
        except Exception:
            try: os.unlink(tmp)
            except OSError: pass
            raise
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()
        sys.stderr.write(f"PUT {rel} ({length} bytes) ok\n")

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Allow", "GET, HEAD, PUT, OPTIONS")
        self.end_headers()


def main():
    here = Path(__file__).resolve()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=here.parent.parent, help="tooling repo root (default: parent of scripts/)")
    ap.add_argument("--engagements", type=Path, required=True, help="engagements root (folder containing <client>/engagement.json)")
    ap.add_argument("--mirror-root", type=Path, default=None,
                    help="optional root under which engagement manifests may point trust_center.local_path (e.g. your OneDrive root); walks are refused outside it")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    tool_root = args.root.resolve()
    eng_root = args.engagements.resolve()
    for name, p in (("root", tool_root), ("engagements", eng_root)):
        if not p.is_dir():
            sys.exit(f"{name}: not a directory: {p}")

    Handler.tool_root = tool_root
    Handler.eng_root = eng_root
    Handler.mirror_root = args.mirror_root.resolve() if args.mirror_root else None
    Handler.directory = str(tool_root)  # for SimpleHTTPRequestHandler internals

    clients = sorted(d.name for d in eng_root.iterdir() if d.is_dir() and (d / "engagement.json").exists())
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"tool root    : {tool_root}")
    print(f"engagements  : {eng_root}")
    print(f"engagements found: {', '.join(clients) or '(none — no <client>/engagement.json yet)'}")
    for c in clients:
        print(f"  http://127.0.0.1:{args.port}/tools/classc-workpapers.html?engagement={c}")
    print("Ctrl+C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
