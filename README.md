# Profilarr Database Template

Template for creating your own Profilarr-compliant database (PCD).

## Quick Start

1. Click **"Use this template"** → **"Create a new repository"**
2. Link the repository in Profilarr
3. Edit the manifest to customize your database
4. Start creating profiles and custom formats

## Structure

Layout matches [Dictionarry-Hub/database](https://github.com/Dictionarry-Hub/database/tree/stable):

```
├── pcd.json           # Database manifest
├── custom_formats/    # Custom format definitions (YAML)
├── media_management/  # Media management config
├── profiles/          # Quality profile YAMLs
├── regex_patterns/    # Regex patterns
├── scripts/           # Automation and SQL (e.g. scripts/sql/, conversion script)
├── templates/         # Templates
└── tweaks/            # Optional configuration variants
```

**Build / validate:** From repo root (requires PyYAML: `pip install pyyaml`):

- Validate YAML: `python3 scripts/validate_yml.py`
- Regenerate custom format YAML from JSON (if you have JSON in `ops/custom_formats/`): `python3 scripts/convert_custom_formats_to_yml.py`

## Learn More

- [Profilarr Documentation](https://github.com/Dictionarry-Hub/profilarr)
- [Schema Reference](https://github.com/Dictionarry-Hub/schema)
- [Example Database](https://github.com/Dictionarry-Hub/db)
