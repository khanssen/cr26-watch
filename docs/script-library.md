# Script Library

Reference for every script in the 20x assessment tooling. Each entry uses the same headings so the web form can deep-link to `#script-name` and render the block as-is.

Two repositories are covered. `cr26-watch` is public (`github.com/khanssen/cr26-watch`) and tracks the rules. The workpaper tooling repo (`fedramp-20x-eval`, private) holds the engagement-side scripts. Nothing in either repo modifies a CR26 snapshot, a feed, or a trust-center source; the only files any script writes are named under **Writes**.

Conventions: `[cr26-watch]` / `[workpaper]` marks the repo. Paths are repo-relative. PowerShell examples assume the repo root as the working directory.

---

## Rules tracking `[cr26-watch]`

### common

**File:** `scripts/common.py`
**Purpose:** Shared loaders for the CR26 consolidated-rules JSON. Not run directly; imported by every other `cr26-watch` script.
**Provides:** `load(path)` (defaults to `data/cr26/current.json`), `version(doc)`, `ksis(doc)` → `(id, theme, indicator)`, `frr_rules(doc)` → `(id, process, applicability, subset, rule)`, `norm_ctrl(s)` (normalizes `AC-02 (03)` / `ac-2.3` / `AC-2(3)` to `ac-2.3`), `class_statement(ind, cls)` (resolves `varies_by_class`).
**Writes:** nothing.
**Notes:** `norm_ctrl` is the single point of truth for control-ID comparison. Any script comparing `controls` arrays must go through it or it will report spurious diffs on formatting.

### fetch_cr26

**File:** `scripts/fetch_cr26.py`
**Purpose:** Download the current `FedRAMP/rules` dataset and store it by version.
**Usage:** `python scripts\fetch_cr26.py`
**Reads:** `https://codeload.github.com/FedRAMP/rules/tar.gz/main` (tarball; no API rate limit).
**Writes:** `data/cr26/fedramp-consolidated-rules.<version>.json` (only if that version isn't already stored), `data/cr26/fedramp-consolidated-rules.schema.json`, `data/cr26/current.json` (plain copy, not a symlink — Windows-safe).
**Output:** one line — `already have <version>` or `stored new version <version>; current.json updated`.
**Notes:** Version is read from `info.version` inside the JSON. A re-push with the same version string and different bytes is **not** detected here; that is `check_upstream`'s job.

### diff_versions

**File:** `scripts/diff_versions.py`
**Purpose:** Rule/KSI/definition/CTL-level diff between two CR26 snapshots. Mapping (`controls` array) changes carry no `updated` history in the dataset — this script is the only way to see them.
**Usage:** `python scripts\diff_versions.py data\cr26\fedramp-consolidated-rules.OLD.json data\cr26\fedramp-consolidated-rules.NEW.json`
**Reads:** two snapshot files.
**Writes:** nothing; prints Markdown to stdout.
**Output sections:** `## Added`, `## Removed` (keys of the form `FRR:<id>`, `KSI:<id>`, `FRD:<id>`, `CTL:<id>`), `## Changed` (key plus the changed field names; KSI `controls` changes get an indented `controls +[...] -[...]` line).
**Exit code:** `0` no mapping change; `2` a KSI was added/removed or a `controls` array changed. Callers key on this, not on the text.
**Notes:** Compares KSI statements per class (a–d). Bold markup inside statements is *not* stripped here, so an emphasis-only edit shows as a change. That is intentional for a watch.

### mapping_stats

**File:** `scripts/mapping_stats.py`
**Purpose:** Structural properties of the KSI → SP 800-53 "Related Controls" mapping for one snapshot: fan-out per KSI, fan-in per control, families absent, CTL parameter counts, optional baseline coverage.
**Usage:** `python scripts\mapping_stats.py [path.json] [--baseline moderate-ids.txt]`
**Reads:** a snapshot (default `current.json`); optional text file of baseline control IDs, one per line.
**Writes:** nothing; prints Markdown to stdout. Redirect to `reports/mapping-stats.<version>.md`.
**Notes:** Output feeds `docs/ksi-mapping-instructions.md` §2 `[DATA]`. The mapping is non-normative and not invertible — see that document before using these numbers for anything beyond orientation. Regenerate only when `diff_versions` exits 2; the numbers do not move otherwise.

### check_upstream

**File:** `scripts/check_upstream.py`
**Purpose:** The daily watch. Fetches upstream, detects a new version **or** a content change without a version bump, diffs against the previous snapshot, writes a dated report, regenerates mapping stats if (and only if) the mapping changed, and emits `GITHUB_OUTPUT` variables for CI.
**Usage:** `python scripts\check_upstream.py` (invoked by `.github/workflows/watch-cr26.yml`, daily 11:17 UTC; also `workflow_dispatch`).
**Reads:** upstream via `fetch_cr26`; existing snapshots in `data/cr26/`.
**Writes:** new snapshot (via `fetch_cr26`); on same-version/different-bytes, an extra `fedramp-consolidated-rules.<version>.<sha8>.json` so nothing is lost; `reports/diff.<old>__<new>.md`; `reports/mapping-stats.<version>.md` only when `diff_versions` exited 2.
**Output:** one summary line (`new version …`, `CONTENT CHANGED WITHOUT VERSION BUMP (…)`, or `no change`), suffixed `[mapping changed]` when stats were regenerated. Sets `changed`, `note`, `report` in `GITHUB_OUTPUT`.
**Exit code:** always `0` unless `diff_versions` returns something other than 0/2, in which case it aborts with the stderr.
**Notes:** The CI job commits `data/cr26` and `reports/` and opens a labeled issue when `changed=true`. If you run this locally on the same day the bot would, you will collide with its commit — prefer **Run workflow** in Actions.

### sync_workpaper_data

**File:** `scripts/sync_workpaper_data.py`
**Purpose:** Regenerate the KSI array embedded in a single-file HTML workpaper tool from a CR26 snapshot, and stamp a `CR26_VERSION` constant into the HTML.
**Usage:** `python scripts\sync_workpaper_data.py path\to\classc-workpapers.html [--class c] [--write]`
**Reads:** the HTML file; `current.json`.
**Writes:** the HTML file in place, **only with `--write`**. Without it: reports `ADD` / `REMOVE` / `STATEMENT` / `CONTROLS` differences per KSI and a count.
**Notes:** Statement comparison strips `**bold**` markup, so emphasis-only changes are ignored here (unlike `diff_versions`). The embedded array is located by regex on `[{"id":"KSI-…}]`; if the HTML's array format changes, this script needs updating. Always run without `--write` first and read the diff.

---

## Engagement tooling `[workpaper]`

### serve

**File:** `scripts/serve.py`
**Purpose:** Loopback HTTP server for `classc-workpapers.html`. Serves the tooling repo at `/` and an engagements root at `/engagements/`, with atomic, allow-listed writes so a sync client (OneDrive) never sees a partial file.
**Usage:** `python scripts\serve.py --engagements "C:\Users\khans\OneDrive - Kompleye Attestation LLC\20x" [--root <repo>] [--port 8000]` then open `http://127.0.0.1:8000/tools/classc-workpapers.html?engagement=<CLIENT>`.
**Reads:** anything under either root (GET). A GET on a directory under `/engagements/` returns a JSON listing for the engagement picker.
**Writes:** PUT only under `/engagements/<client>/`, and only to `workpaper.json` or anything under `exports/`. JSON bodies are validated before write. Temp file + `os.replace`, fsynced.
**Notes:** Binds `127.0.0.1` only; nothing is reachable off-box. Path traversal is rejected. `Cache-Control: no-store` on every response. This is the piece that changes when the tool moves to a Kompleye server — see the concurrency note in `engagement.json` docs.

### add_feed

**File:** `scripts/add_feed.py`
**Purpose:** Register a feed file in an engagement's `engagement.json` manifest with its hashes and provenance. Never edits the feed itself.
**Usage:** `python scripts\add_feed.py "<engagement dir>" feeds\<feed>.json [--tool-commit <sha>]`
**Reads:** the feed's own `feed` block (`kind`, `published`, `source_file`, `source_sha256`, `published_sha256`, `parser`); computes SHA-256 of the feed file on disk; detects the tooling-repo commit via `git rev-parse --short HEAD` if `--tool-commit` isn't given.
**Writes:** `engagement.json` atomically — appends a `feeds[]` entry, or replaces the entry with the same `path`; stamps `tool: fedramp-20x-eval@<commit>`.
**Output:** `added|replaced <path> kind=… sha256=… tool=…`.
**Notes:** Every feed must carry a `feed` block or the manifest entry will have nulls. This is the chain-of-custody record for anything the workpaper cites; do not hand-edit the manifest.

### sdr_to_feed

**File:** `scripts/sdr_to_feed.py`
**Purpose:** First per-vendor adapter. Converts a Security Decision Record human-readable export into feed JSON so the HTML stays generic and vendor quirks live in the adapter.
**Usage / Reads / Writes:** `[UNVERIFIED]` — not reviewed in this pass; document from the script's own docstring when it's next touched.
**Notes:** Registry seeding dedups on exact `ksiTests` text. Adapters should emit a stable mechanism ID per test so that a reworded SDR on re-import matches the mechanism already reviewed rather than creating a duplicate.

### Get-TrustCenterInventory

**File:** `scripts/Get-TrustCenterInventory.ps1`
**Purpose:** Enumerate a SharePoint-hosted trust center via PnP.PowerShell and emit a feed-shaped JSON inventory, with an optional coverage diff against a KSI list.
**Usage:** `.\scripts\Get-TrustCenterInventory.ps1 -SiteUrl <url> -LibraryPath "<site-relative path>" -ClientId <entra-app-id> [-OutFile feeds\trustcenter-inventory.json] [-KsiListFile ksis.txt] [-Hash]`
**Reads:** the library, recursively, as the signed-in guest account.
**Writes:** the `-OutFile` JSON: a `run` header (site, library, `retrieved_at`, `retrieved_by`, counts), optional `coverage` (KSIs without a folder, folders without a KSI, empty folders), and `items[]` with `path`, `name`, `type`, `top_level`, `size`, `modified`, `etag`, `sha256`.
**Notes:** `-ClientId` is mandatory in current PnP.PowerShell, and the app must be consented in the **CSP's** tenant — ask them to register it. `-Hash` downloads every file; run without it first. Fallback when PnP isn't possible: SharePoint's **Export to Excel** on a flat (no-folders) view, then convert with the same field set; that path yields no ETags or hashes, and `feed.published` must be set by hand to the export time.

---

## Feed block convention

Every file placed in `feeds\` carries a top-level `feed` object so `add_feed.py` can register it:

```json
{
  "feed": {
    "kind": "sdr | trustcenter-inventory | <adapter name>",
    "published": "<ISO-8601 UTC — when the source was captured>",
    "source_file": "<original file name>",
    "source_sha256": "<hash of the original>",
    "published_sha256": "<hash of the CSP-published artifact, if different>",
    "parser": "<script name and version/date>"
  },
  "...": "payload"
}
```

`published` is the Stopwatch anchor: evidence validity runs from this timestamp, not from when the feed was registered.
