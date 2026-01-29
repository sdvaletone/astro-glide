# Astro Glide

**TRaSH Guides in Profilarr-compliant format on GitHub.**

This repository turns [TRaSH Guides](https://trash-guides.info/) quality profiles and custom formats into a [Profilarr](https://github.com/Dictionarry-Hub/profilarr)-compliant database you can link from Profilarr and sync to Radarr/Sonarr. Everything is stored as YAML in the [Dictionarry-style layout](https://github.com/Dictionarry-Hub/database/tree/stable) so it works as a single source of truth on GitHub.

## What’s in here

- **Quality profiles** – TRaSH-style profiles (e.g. Sonarr WEB-1080p, WEB-2160p; Radarr HD Bluray + WEB) as Profilarr-compliant YAML in `profiles/`.
- **Custom formats** – TRaSH custom formats converted to the Dictionarry schema (name, description, tags, conditions, tests) in `custom_formats/`.
- **Scripts** – Conversion and validation scripts under `scripts/`, plus SQL from the original TRaSH-based pipeline in `scripts/sql/`.

## Using this database with Profilarr

1. In Profilarr, add a database and point it at this repo (e.g. `https://github.com/<your-org>/astro-glide` or your fork).
2. Use the repo as your Profilarr “database” so it can import/sync the `profiles/` and `custom_formats/` YAML to your Radarr/Sonarr instances.

See [Profilarr documentation](https://github.com/Dictionarry-Hub/profilarr) and [Dictionarry database layout](https://github.com/Dictionarry-Hub/database) for how to link and sync.

## Repository structure

Layout follows [Dictionarry-Hub/database](https://github.com/Dictionarry-Hub/database/tree/stable):

```
├── pcd.json           # Profilarr database manifest
├── custom_formats/    # Custom format definitions (YAML, Dictionarry schema)
├── media_management/  # Media management config (reserved)
├── profiles/          # Quality profile YAMLs
├── regex_patterns/    # Regex patterns (reserved)
├── scripts/           # Conversion scripts and SQL
├── templates/         # Templates (reserved)
└── tweaks/            # Optional overrides
```

## Scripts (from repo root)

Requires Python 3 and PyYAML (`pip install pyyaml`).

| Command | Purpose |
|--------|---------|
| `python3 scripts/validate_yml.py` | Validate all `custom_formats/*.yml` and `profiles/*.yml`. |
| `python3 scripts/convert_custom_formats_to_yml.py` | Regenerate custom format YAML from TRaSH JSON (expects source JSON in `ops/custom_formats/`). |
| `python3 scripts/convert_custom_formats_to_dictionarry_yml.py` | Convert TRaSH-style custom format YAML into Dictionarry schema (name, description, tags, conditions, tests). |

## Documentation

- [Custom formats, profiles, and tweaking](docs/guide.md) – How to create and add custom formats and profiles, and how to tweak profiles.

## References

- [TRaSH Guides](https://trash-guides.info/) – Sonarr/Radarr quality and custom format guides (external reference)
- [Profilarr](https://github.com/Dictionarry-Hub/profilarr) – Import, export, and sync profiles and custom formats
- [Dictionarry database](https://github.com/Dictionarry-Hub/database) – Standard layout and schema for Profilarr databases
- [Profilarr schema](https://github.com/Dictionarry-Hub/schema) – Schema reference for profiles and custom formats
