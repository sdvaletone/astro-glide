#!/usr/bin/env python3
"""
Validate YAML syntax of custom_formats/*.yml and profiles/*.yml.
Run from repository root. Exits 0 if all load successfully.
"""
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    dirs = [
        REPO_ROOT / "custom_formats",
        REPO_ROOT / "profiles",
    ]
    ok = True
    for d in dirs:
        if not d.is_dir():
            continue
        for path in d.glob("*.yml"):
            try:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"{path}: {e}", file=sys.stderr)
                ok = False
    if not ok:
        sys.exit(1)
    print("All YAML files valid.")


if __name__ == "__main__":
    main()
