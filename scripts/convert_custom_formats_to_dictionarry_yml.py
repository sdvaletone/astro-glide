#!/usr/bin/env python3
"""
Convert TRaSH-style custom format YAML to Dictionarry/Profilarr schema:
  name, description, tags, conditions (with type + type-specific fields), tests
Run from repository root. Overwrites custom_formats/*.yml in place.
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

# TRaSH ResolutionSpecification value (int) -> Dictionarry resolution string
RESOLUTION_MAP = {
    360: "360p",
    480: "480p",
    540: "540p",
    576: "576p",
    720: "720p",
    1080: "1080p",
    2160: "2160p",
}

# TRaSH SourceSpecification value (int) -> Dictionarry source string
SOURCE_MAP = {
    1: "cam",
    2: "telesync",
    3: "webdl",
    4: "webrip",
    5: "dvd",
    6: "hdtv",
    7: "bluray",
    8: "remux",
    9: "brdisk",
}


def spec_to_condition(spec: dict) -> dict | None:
    impl = spec.get("implementation")
    name = spec.get("name", "")
    negate = spec.get("negate", False)
    required = spec.get("required", False)
    fields = spec.get("fields") or {}
    value = fields.get("value")

    if impl == "ResolutionSpecification" and value is not None:
        res_str = (
            RESOLUTION_MAP.get(int(value), f"{value}p")
            if isinstance(value, int)
            else str(value)
        )
        return {
            "name": name,
            "negate": negate,
            "required": required,
            "type": "resolution",
            "resolution": res_str,
        }
    if impl == "SourceSpecification" and value is not None:
        src_str = SOURCE_MAP.get(int(value), "unknown") if isinstance(value, int) else str(value)
        return {
            "name": name,
            "negate": negate,
            "required": required,
            "type": "source",
            "source": src_str,
        }
    if impl == "ReleaseGroupSpecification" and value is not None:
        return {
            "name": name,
            "negate": negate,
            "required": required,
            "type": "release_group",
            "pattern": str(value),
        }
    if impl == "ReleaseTitleSpecification" and value is not None:
        return {
            "name": name,
            "negate": negate,
            "required": required,
            "type": "release_title",
            "pattern": str(value),
        }
    # Unknown implementation: keep as generic condition with pattern if possible
    if value is not None:
        return {
            "name": name,
            "negate": negate,
            "required": required,
            "type": "release_title",
            "pattern": str(value),
        }
    return None


def convert_cf(trash_cf: dict) -> dict:
    name = trash_cf.get("name", "Unnamed")
    specifications = trash_cf.get("specifications") or []
    conditions = []
    for spec in specifications:
        cond = spec_to_condition(spec)
        if cond:
            conditions.append(cond)

    description = trash_cf.get("description") or f"Matches release criteria for {name}"
    tags = trash_cf.get("tags")
    if tags is None:
        tags = []

    return {
        "name": name,
        "description": description,
        "tags": tags,
        "conditions": conditions,
        "tests": trash_cf.get("tests", []),
    }


def main() -> None:
    if not CUSTOM_FORMATS_DIR.is_dir():
        print(f"Directory not found: {CUSTOM_FORMATS_DIR}", file=sys.stderr)
        sys.exit(1)

    count = 0
    for yml_path in sorted(CUSTOM_FORMATS_DIR.glob("*.yml")):
        try:
            data = yaml.safe_load(yml_path.read_text(encoding="utf-8"))
            if not data:
                continue
            # Skip if already in Dictionarry format (has top-level "conditions")
            if "conditions" in data and "specifications" not in data:
                continue
            out = convert_cf(data)
            yaml_str = yaml.dump(
                out,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,
            )
            yml_path.write_text(yaml_str, encoding="utf-8")
            count += 1
        except Exception as e:
            print(f"Error converting {yml_path.name}: {e}", file=sys.stderr)

    print(f"Converted {count} custom format(s) to Dictionarry schema.")


if __name__ == "__main__":
    main()
