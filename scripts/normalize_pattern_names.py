#!/usr/bin/env python3
"""
Normalize regex pattern filenames to follow Dictionarry naming conventions.

Fixes:
- Files with (1), (2), etc. suffixes: rename to descriptive names based on source
- Files starting with # or other problematic characters

Run from repository root:
    python3 scripts/normalize_pattern_names.py
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
REGEX_PATTERNS_DIR = REPO_ROOT / "regex_patterns"


def get_safe_filename(name: str) -> str:
    """Convert a name to a safe filename, handling problematic characters."""
    # Replace characters that are problematic at the start of filenames
    if name.startswith('#'):
        name = 'Hash' + name[1:]
    
    # Replace characters that are problematic for filesystems
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    
    # Trim and limit length
    name = name.strip()
    if len(name) > 100:
        name = name[:100]
    
    return name


def find_descriptive_name(pattern: str, current_name: str, description: str) -> str:
    """Find a more descriptive name for a pattern file with (N) suffix."""
    # Extract the base name without the (N) suffix
    base_match = re.match(r'^(.+?)\s*\(\d+\)$', current_name)
    if not base_match:
        return current_name
    
    base_name = base_match.group(1).strip()
    
    # Try to extract context from the description
    # Format is typically "Auto-generated from <CustomFormatName>"
    cf_match = re.search(r'Auto-generated from (.+)$', description)
    if cf_match:
        cf_name = cf_match.group(1)
        # Create a unique name combining base name and source
        new_name = f"{base_name} ({cf_name})"
        return get_safe_filename(new_name)
    
    return current_name


def normalize_files():
    """Normalize all regex pattern filenames."""
    if not REGEX_PATTERNS_DIR.exists():
        print(f"Directory not found: {REGEX_PATTERNS_DIR}", file=sys.stderr)
        sys.exit(1)

    # First pass: collect all files that need renaming
    files_to_rename = []
    existing_names = set()
    
    for f in sorted(REGEX_PATTERNS_DIR.glob("*.yml")):
        existing_names.add(f.stem.lower())
    
    for f in sorted(REGEX_PATTERNS_DIR.glob("*.yml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not data:
                continue
            
            current_name = f.stem
            description = data.get("description", "")
            pattern = data.get("pattern", "")
            
            new_name = current_name
            needs_rename = False
            
            # Check for (N) suffix
            if re.search(r'\(\d+\)$', current_name):
                new_name = find_descriptive_name(pattern, current_name, description)
                needs_rename = True
            
            # Check for problematic starting characters
            if current_name.startswith('#'):
                new_name = 'Hash' + current_name[1:]
                needs_rename = True
            
            if needs_rename and new_name != current_name:
                files_to_rename.append((f, new_name, data))
                
        except Exception as e:
            print(f"Error processing {f.name}: {e}", file=sys.stderr)
    
    print(f"Found {len(files_to_rename)} files to rename")
    
    # Second pass: rename files, handling conflicts
    renamed = 0
    used_names = set(existing_names)
    
    for old_path, new_name, data in files_to_rename:
        # Ensure unique filename
        final_name = new_name
        counter = 1
        while final_name.lower() in used_names and final_name.lower() != old_path.stem.lower():
            # If conflict, try adding a counter
            final_name = f"{new_name} {counter}"
            counter += 1
        
        if final_name.lower() == old_path.stem.lower():
            # No actual rename needed
            continue
        
        new_path = REGEX_PATTERNS_DIR / f"{final_name}.yml"
        
        # Update the name field in the data
        data["name"] = final_name
        
        # Write to new file
        yaml_str = yaml.dump(
            data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )
        new_path.write_text(yaml_str, encoding="utf-8")
        
        # Remove old file
        old_path.unlink()
        
        # Update tracking
        used_names.discard(old_path.stem.lower())
        used_names.add(final_name.lower())
        
        renamed += 1
        print(f"  Renamed: {old_path.name} -> {new_path.name}")
    
    print(f"\nRenamed {renamed} files")
    return renamed


def main():
    print("Normalizing regex pattern filenames...")
    renamed = normalize_files()
    print(f"\nDone! Normalized {renamed} files.")


if __name__ == "__main__":
    main()
