# CR26 Watch — FedRAMP 20x Evaluation Toolkit

Maintained by Archstone Security LLC.

Tooling and analysis for evaluating FedRAMP 20x certifications under the
Consolidated Rules for 2026 (CR26), from the perspective of independent
assessors and federal agencies.

**Authoritative source:** `FedRAMP/rules` → `fedramp-consolidated-rules.json`.
This repository stores versioned snapshots under `data/cr26/` and never modifies them.

| Path | Purpose |
|---|---|
| `data/cr26/` | Versioned CR26 JSON snapshots + schema. `current.json` is a plain copy of the latest. |
| `scripts/fetch_cr26.py` | Pull the latest dataset from GitHub, store by version. |
| `scripts/diff_versions.py` | Full-body diff between two versions: ruleset metadata (status, effective dates, applicability), rules, KSIs, definitions, CTL. Classes each change substantive / cosmetic / derived and flags force-keyword and changelog-less (`SILENT`) edits. Mapping changes have no `updated` history in the dataset; this is the only way to see them. |
| `scripts/mapping_stats.py` | Structural properties of the KSI → SP 800-53 mapping (fan-in, fan-out, coverage). |
| `scripts/sync_workpaper_data.py` | Regenerate the KSI array embedded in an HTML workpaper tool and stamp the CR26 version. |
| `reports/` | Generated, dated reports. |
| `posts/` | Public, facts-only change posts (one per release), published as GitHub Releases on merge. Analysis sections are the author's. |
| `scripts/make_post.py` | Generates a change post; never writes the Analysis section. |
| `docs/` | Analysis and standing positions, with rule-ID citations. Start with `docs/ksi-mapping-analysis.md`. |
| `tools/` | Public tools (none yet). |

## Marker discipline

Every claim in `docs/` is tagged `[RULE]` (cited CR26 text), `[DATA]` (computed from the
JSON by script), `[ANALYSIS]` (author position), or `[UNVERIFIED]`. RFCs, notices, and
`/legacy/` pages are historical and are not cited as current requirements.

## Quick start

```bash
python scripts/fetch_cr26.py
python scripts/mapping_stats.py --out reports/mapping-stats.$(date +%F).md
python scripts/diff_versions.py data/cr26/fedramp-consolidated-rules.OLD.json data/cr26/current.json
```

## License

Apache-2.0 for code, CC-BY-4.0 for `docs/` and `reports/`; CR26 data is public domain. See `LICENSE` and `docs/LICENSING.md`.

See [docs/USAGE.md](docs/USAGE.md) for running the scripts, reading a change issue, and the publication boundary.
