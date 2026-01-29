#!/usr/bin/env python3
"""
Generate missing regex pattern files for Profilarr compatibility.

Profilarr looks up patterns by exact match of the pattern string.
This script extracts all patterns from custom_formats/*.yml and creates
corresponding regex_patterns/*.yml files for any that are missing.

Run from repository root:
    python3 scripts/generate_missing_patterns.py
"""
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_FORMATS_DIR = REPO_ROOT / "custom_formats"
REGEX_PATTERNS_DIR = REPO_ROOT / "regex_patterns"


def sanitize_filename(name: str) -> str:
    """Convert a condition name to a valid filename."""
    # Replace problematic characters
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Replace multiple spaces/underscores with single underscore
    name = re.sub(r'[\s_]+', ' ', name)
    # Trim whitespace
    name = name.strip()
    # Limit length
    if len(name) > 100:
        name = name[:100]
    return name


def infer_tags(condition_name: str, pattern: str, cf_name: str) -> list:
    """Infer appropriate tags based on condition/pattern content."""
    tags = []
    name_lower = condition_name.lower()
    pattern_lower = pattern.lower()
    cf_lower = cf_name.lower()

    # Release group patterns
    if "release_group" in name_lower or pattern.startswith("^(") and pattern.endswith(")$"):
        tags.append("Release Group")

    # Audio-related
    audio_keywords = ["atmos", "dts", "truehd", "aac", "flac", "pcm", "dolby", "surround", "stereo", "mono", "sound", "audio"]
    if any(kw in name_lower or kw in pattern_lower for kw in audio_keywords):
        tags.append("Audio")

    # Video-related
    video_keywords = ["hdr", "dv", "dolby vision", "hevc", "h265", "h264", "x264", "x265", "av1", "remux", "bluray", "webdl", "webrip"]
    if any(kw in name_lower or kw in pattern_lower for kw in video_keywords):
        tags.append("Video")

    # Streaming services
    streaming = ["netflix", "amazon", "amzn", "disney", "dsnp", "hbo", "hmax", "apple", "atvp", "hulu", "peacock", "paramount", "crunchyroll"]
    if any(kw in name_lower or kw in pattern_lower for kw in streaming):
        tags.append("Streaming")

    # Anime-specific
    if "anime" in cf_lower or any(kw in name_lower for kw in ["fansub", "dual audio", "uncensored", "raws"]):
        tags.append("Anime")

    # Resolution
    if any(res in pattern_lower for res in ["1080", "2160", "720", "480", "4k"]):
        tags.append("Resolution")

    return tags


def load_existing_patterns() -> dict:
    """Load all existing patterns from regex_patterns directory.
    
    Returns:
        dict mapping pattern string to filename (without .yml)
    """
    patterns = {}
    if not REGEX_PATTERNS_DIR.exists():
        return patterns

    for f in REGEX_PATTERNS_DIR.glob("*.yml"):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            if data and "pattern" in data:
                patterns[data["pattern"]] = f.stem
        except Exception:
            pass
    return patterns


def extract_patterns_from_custom_formats() -> list:
    """Extract all patterns from custom format conditions.
    
    Returns:
        list of dicts with keys: pattern, name, cf_name, type
    """
    patterns = []
    if not CUSTOM_FORMATS_DIR.exists():
        return patterns

    for f in sorted(CUSTOM_FORMATS_DIR.glob("*.yml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not data or "conditions" not in data:
                continue

            cf_name = data.get("name", f.stem)
            for cond in data.get("conditions", []):
                if "pattern" in cond:
                    patterns.append({
                        "pattern": cond["pattern"],
                        "name": cond.get("name", "Unknown"),
                        "cf_name": cf_name,
                        "type": cond.get("type", "release_title"),
                    })
        except Exception:
            pass
    return patterns


def generate_pattern_file(pattern: str, name: str, cf_name: str, existing_files: set) -> str | None:
    """Generate a YAML file for a pattern.
    
    Returns:
        The filename created, or None if skipped.
    """
    base_name = sanitize_filename(name)
    if not base_name:
        base_name = "pattern"

    # Handle duplicate filenames
    filename = base_name
    counter = 1
    while filename.lower() in existing_files or (REGEX_PATTERNS_DIR / f"{filename}.yml").exists():
        filename = f"{base_name} ({counter})"
        counter += 1

    existing_files.add(filename.lower())

    # Infer tags
    tags = infer_tags(name, pattern, cf_name)

    # Create pattern data
    data = {
        "name": name,
        "pattern": pattern,
        "description": f"Auto-generated from {cf_name}",
        "tags": tags,
        "tests": [],
    }

    # Write file
    filepath = REGEX_PATTERNS_DIR / f"{filename}.yml"
    yaml_str = yaml.dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    filepath.write_text(yaml_str, encoding="utf-8")

    return filename


def main() -> None:
    print("Loading existing patterns...")
    existing_patterns = load_existing_patterns()
    print(f"  Found {len(existing_patterns)} existing pattern files")

    print("Extracting patterns from custom formats...")
    cf_patterns = extract_patterns_from_custom_formats()
    print(f"  Found {len(cf_patterns)} pattern references in custom formats")

    # Find unique patterns that are missing
    seen_patterns = set()
    missing_patterns = []
    for p in cf_patterns:
        pattern_str = p["pattern"]
        if pattern_str not in existing_patterns and pattern_str not in seen_patterns:
            missing_patterns.append(p)
            seen_patterns.add(pattern_str)

    print(f"  Missing patterns: {len(missing_patterns)}")

    if not missing_patterns:
        print("\nAll patterns already exist. Nothing to generate.")
        return

    # Ensure output directory exists
    REGEX_PATTERNS_DIR.mkdir(parents=True, exist_ok=True)

    # Track used filenames (case-insensitive for cross-platform compatibility)
    existing_files = {f.stem.lower() for f in REGEX_PATTERNS_DIR.glob("*.yml")}

    print(f"\nGenerating {len(missing_patterns)} pattern files...")
    created = 0
    for p in missing_patterns:
        filename = generate_pattern_file(
            p["pattern"], p["name"], p["cf_name"], existing_files
        )
        if filename:
            created += 1

    print(f"\nDone! Created {created} new pattern files in {REGEX_PATTERNS_DIR}")

    # Verify coverage
    print("\nVerifying coverage...")
    new_existing = load_existing_patterns()
    cf_pattern_strings = {p["pattern"] for p in cf_patterns}
    still_missing = cf_pattern_strings - set(new_existing.keys())
    if still_missing:
        print(f"  WARNING: {len(still_missing)} patterns still missing!")
        for p in list(still_missing)[:5]:
            print(f"    - {p[:60]}...")
    else:
        print(f"  SUCCESS: All {len(cf_pattern_strings)} patterns now have matching files!")


if __name__ == "__main__":
    main()
