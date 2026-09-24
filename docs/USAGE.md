# Usage

How to run and read this repository. Commands are shown for PowerShell; on
macOS/Linux use `/` paths and `python3`.

## 1. What runs on its own

Two GitHub Actions run without you:

| Workflow | Schedule | What it does |
|---|---|---|
| Watch FedRAMP/rules for CR26 changes | daily, 11:17 UTC | Fetches the upstream dataset and compares **bytes** against `data/cr26/current.json`. On any difference it stores the snapshot (`<version>.json`, or `<version>.<sha8>.json` if the version string did not change), writes `reports/diff.<old>__<new>.md` and `reports/mapping-stats.<new>.md`, and opens an issue with the diff as the body. |
| Watch marketplace-fedramp-gov-data | weekly, Monday | Commits a dated snapshot of the Marketplace data under `data/marketplace/<date>/`. Nothing is analyzed; this is raw longitudinal capture. |

Both can be run on demand: Actions tab → pick the workflow → Run workflow.

A third workflow, **Self-test the CR26 watcher**, is manual only (Actions → Self-test the CR26 watcher → Run workflow). It rewinds the baseline inside the runner, runs the real pipeline against live upstream, and opens a `[SELF-TEST]` issue labeled `cr26-selftest`. It commits nothing. The run fails loudly if the planted change goes undetected. Scenarios:

| Scenario | Tests |
|---|---|
| `previous-version` | Replays the last real release (baseline = prior snapshot) |
| `synthetic` | Planted AGU status flip, KSI control removal, MUST→SHOULD: exercises mapping/ruleset/force detection |
| `no-bump` | Same edits under the same version string: exercises content-changed-without-version-bump |

Run it after any change to the scripts, and once to confirm you actually get notified. Filter test issues out of real ones with `-label:cr26-selftest`.

## 2. When a `cr26-change` issue lands

The issue title is the summary, e.g. `CR26: new version 2026.09.13.02: 12 substantive, 2 ruleset, 1 force-bearing, 10 silent, 1 cosmetic, 233 derived`. Labels escalate:

| Label | Meaning |
|---|---|
| `cr26-change` | Always present |
| `cr26-mapping` | A KSI `controls` array changed. This is what the repo exists to catch. |
| `cr26-ruleset` | Ruleset metadata changed: `status` (e.g. AGU leaving `placeholder`), purpose, effective/grace dates, subset applicability. None of this has a changelog in the dataset. |
| `cr26-force` | A normative keyword (MUST, SHOULD, MAY, NOT, UNLESS…) or "if applicable" was added/removed, or a `force` field changed |
| `cr26-no-version-bump` | Content changed but `info.version` did not. Worth a note to the PMO. |

The body is `scripts/diff_versions.py` output, in this order:

- **Summary table** of counts.
- **Ruleset / dataset metadata**: changes to ruleset `info` blocks and top-level `info`.
- **Added / Removed**: rule, KSI, definition, or CTL IDs.
- **Substantive**: one entry per changed item, one line per changed field. Text fields show an inline word diff, `[-removed-] {+added+}`; `controls` shows `+[...] -[...]`.
- **Cosmetic**: text identical after normalizing whitespace, quote/dash glyphs, and doubled words ("the the").
- **Derived**: items whose only change is a `terms` list losing terms whose definition was newly flagged `ignore_in_terms`. Reported as a single count; one definition flag can touch hundreds of rules.

Flags on items: **FORCE** as above; **SILENT** means the item's body changed but its `updated` changelog did not.

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
python scripts\diff_versions.py data\cr26\fedramp-consolidated-rules.2026.07.14.01.json data\cr26\current.json --out reports\diff.local.md

# Mapping statistics (fan-in, fan-out, families absent, CTL parameter counts)
python scripts\mapping_stats.py --out reports\mapping-stats.local.md

# Same, with baseline coverage: hand it a file of Moderate-baseline control ids, one per line
python scripts\mapping_stats.py --baseline path\to\moderate-ids.txt

# Everything the daily action does, locally
python scripts\check_upstream.py
```

`fetch_cr26.py` uses the codeload tarball, not the GitHub API, so it is not rate-limited and needs no token. It compares bytes, not the version string, so a content change without a version bump is stored rather than skipped.

All scripts read and write UTF-8 explicitly. Use `--out` rather than `>` when saving reports: Windows PowerShell 5.1 redirection writes UTF-16, which GitHub renders as garbage.

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
3. Run `diff_versions.py` against the previous file with `--out reports\diff.<old>__<new>.md`.
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
