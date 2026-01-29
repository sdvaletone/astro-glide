# Astro Glide: Custom Formats, Profiles, and Tweaking

This guide explains how to create and add custom formats and quality profiles to this database, and how to tweak existing profiles.

## Custom formats and profiles

### How custom formats work

Custom formats are YAML files in `custom_formats/` that follow the [Dictionarry/Profilarr schema](https://github.com/Dictionarry-Hub/schema). Each file defines:

- **name** – Display name (must match exactly when referenced in profiles).
- **description** – Short explanation of what the format matches.
- **tags** – Optional list of tags for organization.
- **conditions** – List of rules that determine when a release matches. Each condition has:
  - **name** – Label for the condition.
  - **type** – e.g. `release_title`, `resolution`, `source`, `release_group`.
  - **pattern** – For `release_title` and similar: regex or string to match.
  - **negate** – If `true`, the condition matches when the pattern does *not* match.
  - **required** – Whether the condition must pass for the format to match.
- **tests** – Optional list of test cases.

Example: `custom_formats/4.0 Sound.yml` uses `type: release_title` with regex patterns to match 4.0-channel audio and exclude mono/stereo. Similarly, `custom_formats/2.0 Stereo.yml` does the same for stereo. Open those files in the repo for reference.

### How to add a new custom format

1. Create a new `.yml` file in `custom_formats/` (e.g. `custom_formats/My Format.yml`).
2. Use the same schema as existing formats: `name`, `description`, `tags`, `conditions`, and optionally `tests`. Copy `custom_formats/4.0 Sound.yml` or `custom_formats/2.0 Stereo.yml` as a template.
3. Run validation from the repo root: `python3 scripts/validate_yml.py`.
4. If you add the format to a profile, reference it by **name** exactly as in the YAML.

### How profiles work

Quality profiles live in `profiles/` as YAML files. Key fields:

- **name**, **description**, **tags** – Identity and metadata.
- **upgradesAllowed** – Whether upgrades are allowed.
- **minCustomFormatScore** – Minimum total custom format score to accept a release.
- **upgradeUntilScore** – Upgrade until this total score is reached.
- **minScoreIncrement** – Minimum score gain for an upgrade to be considered.
- **custom_formats** – List of `name` / `score` entries (shared or default).
- **custom_formats_radarr** / **custom_formats_sonarr** – App-specific scoring when different from `custom_formats`.
- **qualities** – Quality definitions and order (e.g. WEBDL-1080p, Bluray-1080p).
- **upgrade_until** – Quality to upgrade until.
- **language** – e.g. `must_original`.

See `profiles/WEB-1080p.yml` (Sonarr) and `profiles/HD-Bluray-WEB.yml` (Radarr) for full examples.

### How to add a new profile

1. Copy an existing profile from `profiles/` (e.g. `WEB-1080p.yml` or `HD-Bluray-WEB.yml`) and rename it.
2. Edit `name`, `description`, and `tags` to match the new profile.
3. Adjust `custom_formats` (and optionally `custom_formats_radarr` / `custom_formats_sonarr`), `qualities`, and `upgrade_until` as needed.
4. Ensure every custom format **name** in the profile exists as a file in `custom_formats/` (exact name match).
5. Run `python3 scripts/validate_yml.py` from the repo root.

**Note:** Some TRaSH-style profile names (e.g. "Generated Dynamic HDR", "Sing-Along Versions", "MA", "HD Bluray Tier 03", "3D", "BCORE", "CRiT") were removed from `HD-Bluray-WEB.yml` because no matching custom format YAML exists in this repo. To use them, add the corresponding files under `custom_formats/` or re-add the entries once those formats exist.

## Tweaking profiles

### Score semantics

- **Positive scores** – Preferred. Higher = more preferred. Radarr/Sonarr use the sum of matching custom format scores to rank releases and decide upgrades.
- **Negative scores** – Unwanted. A total score below `minCustomFormatScore` (often 0) causes rejection. Common value for hard blocks: `-10000`.
- **Relative ordering** – For upgrades, the app compares total scores and `upgradeUntilScore`; ordering of qualities in the profile also matters (e.g. 1080p above SD).

### Safe tweaks

You can edit profile YAMLs to:

- **Adjust streaming service scores** – e.g. AMZN, NF, HBO. Increase to prefer a source, set to 0 for “name only,” or use a negative score to avoid it.
- **Adjust tier scores** – e.g. WEB Tier 01/02/03, HD Bluray Tier 01/02/03. Raise or lower to change how much preferred encodes are favored.
- **Repack/Proper** – Small positive scores (e.g. 5, 6, 7) for Repack/Proper, Repack2, Repack3 are typical.
- **Add or remove optional custom formats** – Add a `name`/`score` entry for a format in `custom_formats/` (or the app-specific list); ensure the format exists in `custom_formats/`.
- **Change upgrade aggressiveness** – `upgradeUntilScore` and `minCustomFormatScore` control when releases are accepted and when upgrades stop.

### Optional overrides (tweaks/)

The Dictionarry layout reserves `tweaks/` for optional overrides. If your Profilarr setup supports it, you can place overrides there instead of editing profile YAMLs directly. Check Profilarr documentation for how it merges or applies `tweaks/`.

### Using with Profilarr

- **Configuration:** Ensure Profilarr is set to sync this repo as a PCD. The root `pcd.json` manifest (with `profilarr.minimum_version` and `dependencies.schema`) must be valid per the [manifest spec](https://github.com/Dictionarry-Hub/schema/blob/main/docs/manifest.md).
- **Sync order:** Sync custom formats first, then quality profiles. Profilarr (and Dictionarry docs) require that custom formats are imported before syncing any premade profile; otherwise profile custom format scores are not applied correctly.
- **Name matching:** Profile custom format names must match the `name` in `custom_formats/*.yml` exactly (including case). Use `python3 scripts/validate_profile_custom_formats.py` before pushing to catch missing or mismatched names.

### Further reading

For detailed scoring rationale, quality ordering, and per-format explanations, see [TRaSH Guides](https://trash-guides.info/) (Sonarr/Radarr quality profiles and custom formats).
