# Usage

How to run and read this repository. Commands are shown for PowerShell; on
macOS/Linux use `/` paths and `python3`.

## 1. What runs on its own

Two GitHub Actions run without you:

| Workflow | Schedule | What it does |
|---|---|---|
| Watch FedRAMP/rules for CR26 changes | daily, 11:17 UTC | Fetches the upstream dataset. If the version string changed **or** the bytes changed under the same version, it commits the new snapshot to `data/cr26/`, writes `reports/diff.<old>__<new>.md` and a fresh `reports/mapping-stats.<version>.md`, and opens an issue labeled `cr26-change` with the diff as the body. |
| Watch marketplace-fedramp-gov-data | weekly, Monday | Commits a dated snapshot of the Marketplace data under `data/marketplace/<date>/`. Nothing is analyzed; this is raw longitudinal capture. |

Both can be run on demand: Actions tab → pick the workflow → Run workflow.

## 2. When a `cr26-change` issue lands

The issue body is the output of `scripts/diff_versions.py`. Read it top to bottom:

- **Added / Removed** — new or deleted rule, KSI, definition, or CTL IDs.
- **Changed** — one line per ID with the fields that differ (`statement`, `force`, `notes`, `fi` = following_information, `controls`, `parameters`, `guidance`).
- **`controls +[...] -[...]`** under a KSI line — the KSI → SP 800-53 mapping changed. This is the only place that change is visible; the dataset carries no `updated` entry for it.

The header line says `new version X` or `CONTENT CHANGED WITHOUT VERSION BUMP (X)`. The second is worth a note to the PMO: the published version string did not change but the rules did.

Then:

1. Check whether any changed ID appears in a tool you maintain (see §4).
2. If a rule you cite in analysis changed, update the citation and the `updated` date you quote.
3. Close the issue with a one-line note of what, if anything, you did.

## 3. Running the scripts locally

Requires Python 3.10+. No packages beyond the standard library.

```powershell
# Fetch the latest dataset; stores it by version, updates data\cr26\current.json
python scripts\fetch_cr26.py

# Diff two versions
python scripts\diff_versions.py data\cr26\fedramp-consolidated-rules.2026.07.14.01.json data\cr26\current.json

# Mapping statistics (fan-in, fan-out, families absent, CTL parameter counts)
python scripts\mapping_stats.py > reports\mapping-stats.local.md

# Same, with baseline coverage: hand it a file of Moderate-baseline control ids, one per line
python scripts\mapping_stats.py --baseline path\to\moderate-ids.txt

# Everything the daily action does, locally
python scripts\check_upstream.py
```

`fetch_cr26.py` uses the codeload tarball, not the GitHub API, so it is not rate-limited and needs no token.

## 4. Keeping an HTML tool in sync

Any tool that embeds a KSI array (`[{"id":"KSI-...`) can be checked and updated:

```powershell
# Report differences between the embedded array and current.json (Class C by default)
python scripts\sync_workpaper_data.py path\to\tool.html

# Class B instead
python scripts\sync_workpaper_data.py path\to\tool.html --class b

# Rewrite the array in place and stamp const CR26_VERSION="..." at the top of the first <script>
python scripts\sync_workpaper_data.py path\to\tool.html --write
```

The tool file itself belongs in `private/` or outside this repo. `private/` is git-ignored; nothing there is ever pushed.

## 5. Adding a new CR26 version by hand

If the action is down or you want a specific historical version:

1. Save the JSON as `data\cr26\fedramp-consolidated-rules.<version>.json` (the `<version>` is `info.version` inside the file).
2. Copy it over `data\cr26\current.json`.
3. Run `diff_versions.py` against the previous file and save the output to `reports\`.
4. Commit all three.

Do not edit any file under `data\cr26\`. They are byte-exact copies of U.S. Government works; `.gitattributes` marks JSON as `-text` so Git never rewrites them.

## 6. What must never be committed

- Anything under `private/`
- Client identifiers, engagement artifacts, assessor findings
- A CVE tied to a named provider
- `.nessus`, `.xlsx`, or any file matching `client-*`

`.gitignore` enforces the file patterns; the rest is judgment. Run
`git ls-files | Select-String private` before any push if in doubt — it should return nothing.

## 7. Marker discipline in `docs/`

Every claim carries one of:

- `[RULE]` — quoted or ID-cited CR26 text
- `[DATA]` — computed from the JSON by a script in this repo
- `[ANALYSIS]` — author position
- `[UNVERIFIED]` — flagged, not yet sourced

RFCs, `NTC-` notices, and anything under `fedramp.gov/rfcs/`, `/notices/`, or
`/legacy/` are historical and are never cited as current requirements.
