#!/usr/bin/env python3
"""
Convert TRaSH-style custom format JSON files to YAML.
Reads from ops/custom_formats/*.json, writes to custom_formats/*.yml (repo root).
Run from repository root.
"""
from pathlib import Path
import json
import sys

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "ops" / "custom_formats"
OUT_DIR = REPO_ROOT / "custom_formats"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SRC_DIR.is_dir():
        print(f"Source directory not found: {SRC_DIR}", file=sys.stderr)
        sys.exit(1)

    count = 0
    for json_path in sorted(SRC_DIR.glob("*.json")):
        base_name = json_path.stem
        yml_path = OUT_DIR / f"{base_name}.yml"
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            yaml_str = yaml.dump(
                data,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,
            )
            yml_path.write_text(yaml_str, encoding="utf-8")
            count += 1
        except Exception as e:
            print(f"Error converting {json_path.name}: {e}", file=sys.stderr)

    print(f"Converted {count} custom format(s) to {OUT_DIR}")


if __name__ == "__main__":
    main()
