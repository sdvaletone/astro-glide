#!/usr/bin/env python3
"""
Validate that every custom format name referenced in profiles/*.yml exists
in custom_formats/*.yml (exact name match). Reports missing names and
optionally warns on case-only differences.
Run from repository root. Exits 0 if all references are valid.
"""
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_FORMATS_DIR = REPO_ROOT / "custom_formats"
PROFILES_DIR = REPO_ROOT / "profiles"
CF_KEYS = ("custom_formats", "custom_formats_radarr", "custom_formats_sonarr")


def get_custom_format_names() -> set[str]:
    """Collect top-level 'name' from every custom_formats/*.yml."""
    names = set()
    if not CUSTOM_FORMATS_DIR.is_dir():
        return names
    for path in CUSTOM_FORMATS_DIR.glob("*.yml"):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "name" in data:
                names.add(data["name"])
        except Exception as e:
            print(f"{path}: {e}", file=sys.stderr)
    return names


def get_profile_references() -> list[tuple[Path, str, str]]:
    """Yield (profile_path, cf_key, name) for each custom format reference in profiles."""
    if not PROFILES_DIR.is_dir():
        return []
    refs = []
    for path in PROFILES_DIR.glob("*.yml"):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"{path}: {e}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            continue
        for key in CF_KEYS:
            entries = data.get(key)
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if isinstance(entry, dict) and "name" in entry:
                    refs.append((path, key, entry["name"]))
    return refs


def main() -> None:
    cf_names = get_custom_format_names()
    cf_names_lower = {n.lower(): n for n in cf_names}
    refs = get_profile_references()
    missing = []
    case_warnings = []
    for path, key, name in refs:
        if name in cf_names:
            continue
        if name.lower() in cf_names_lower:
            case_warnings.append((path, key, name, cf_names_lower[name.lower()]))
        else:
            missing.append((path, key, name))
    ok = True
    for path, key, name in missing:
        print(f"{path}: in {key}, custom format '{name}' has no matching custom_formats/*.yml", file=sys.stderr)
        ok = False
    for path, key, name, canonical in case_warnings:
        print(f"{path}: in {key}, '{name}' differs by case from custom format '{canonical}'", file=sys.stderr)
        ok = False
    if not ok:
        sys.exit(1)
    print("All profile custom format references are valid.")


if __name__ == "__main__":
    main()
