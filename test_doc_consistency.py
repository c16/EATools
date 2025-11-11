#!/usr/bin/env python3
"""
Regression test for documentation generation.

This script ensures that documentation output remains consistent unless
intentional changes are made to documentation features.

Usage:
    python test_doc_consistency.py              # Test latest against golden
    python test_doc_consistency.py --update     # Update golden baseline

Golden Set: Expected documentation output (checked into git)
Latest Set: Newly generated documentation (temporary)
"""

import sys
import hashlib
import shutil
import argparse
import difflib
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess


def calculate_file_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def calculate_directory_checksums(directory: Path) -> Dict[str, str]:
    """Calculate checksums for all files in a directory recursively"""
    checksums = {}

    if not directory.exists():
        return checksums

    for file_path in sorted(directory.rglob('*')):
        if file_path.is_file():
            rel_path = file_path.relative_to(directory)
            checksums[str(rel_path)] = calculate_file_checksum(file_path)

    return checksums


def generate_documentation(qea_file: Path, output_dir: Path) -> int:
    """Run the documentation generator"""
    cmd = [
        sys.executable,
        "sparx_doc_generator.py",
        str(qea_file),
        "--output", str(output_dir)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Generator failed: {result.stderr}")

    return result.returncode


def get_file_diff(golden_file: Path, latest_file: Path) -> List[str]:
    """Generate unified diff between two files"""
    try:
        with open(golden_file, 'r') as f:
            golden_lines = f.readlines()
        with open(latest_file, 'r') as f:
            latest_lines = f.readlines()

        diff = difflib.unified_diff(
            golden_lines,
            latest_lines,
            fromfile=f'golden/{golden_file.name}',
            tofile=f'latest/{latest_file.name}',
            lineterm=''
        )
        return list(diff)
    except Exception as e:
        return [f"Error generating diff: {e}"]


def compare_documentation(golden_dir: Path, latest_dir: Path) -> Tuple[bool, List[str]]:
    """
    Compare golden vs latest documentation.

    Returns:
        (matches, differences) where differences is a list of issue descriptions
    """
    differences = []

    # Calculate checksums
    golden_checksums = calculate_directory_checksums(golden_dir)
    latest_checksums = calculate_directory_checksums(latest_dir)

    # Check for missing files
    golden_files = set(golden_checksums.keys())
    latest_files = set(latest_checksums.keys())

    missing_in_latest = golden_files - latest_files
    extra_in_latest = latest_files - golden_files

    if missing_in_latest:
        differences.append("\n❌ Files in GOLDEN but missing in LATEST:")
        for f in sorted(missing_in_latest):
            differences.append(f"   - {f}")

    if extra_in_latest:
        differences.append("\n❌ Files in LATEST but not in GOLDEN:")
        for f in sorted(extra_in_latest):
            differences.append(f"   + {f}")

    # Compare matching files
    modified_files = []
    for filename in golden_files & latest_files:
        if golden_checksums[filename] != latest_checksums[filename]:
            modified_files.append(filename)

    if modified_files:
        differences.append(f"\n❌ {len(modified_files)} file(s) have different content:")
        for f in sorted(modified_files):
            differences.append(f"   • {f}")

            # Show diff for first few files
            if len([d for d in differences if d.startswith("   • ")]) <= 3:
                golden_file = golden_dir / f
                latest_file = latest_dir / f
                diff_lines = get_file_diff(golden_file, latest_file)

                if diff_lines:
                    differences.append("\n     Diff:")
                    # Show first 20 lines of diff
                    for line in diff_lines[:20]:
                        differences.append(f"     {line}")
                    if len(diff_lines) > 20:
                        differences.append(f"     ... ({len(diff_lines) - 20} more lines)")

    matches = len(differences) == 0

    return matches, differences


def main():
    parser = argparse.ArgumentParser(
        description='Test documentation generation consistency'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update golden baseline with latest generated docs'
    )
    args = parser.parse_args()

    qea_file = Path("test_model.qea")
    golden_dir = Path("docs_golden")
    latest_dir = Path("docs_latest")

    print("=" * 70)
    print("Documentation Generation Regression Test")
    print("=" * 70)

    # Verify .qea file exists
    if not qea_file.exists():
        print(f"\n❌ ERROR: {qea_file} not found")
        return 1

    # Calculate model checksum
    print(f"\n📄 Model: {qea_file}")
    qea_checksum = calculate_file_checksum(qea_file)
    print(f"   Checksum: {qea_checksum}")

    if args.update:
        # Update golden baseline
        print(f"\n🔄 Updating golden baseline...")

        if golden_dir.exists():
            print(f"   Removing old golden: {golden_dir}")
            shutil.rmtree(golden_dir)

        print(f"   Generating new golden documentation...")
        returncode = generate_documentation(qea_file, golden_dir)

        if returncode != 0:
            print(f"\n❌ FAILED: Could not generate documentation")
            return 1

        golden_checksums = calculate_directory_checksums(golden_dir)
        print(f"\n✅ Golden baseline updated: {len(golden_checksums)} files")

        # Save checksums
        checksums_file = Path("test_model_checksums.txt")
        with open(checksums_file, 'w') as f:
            f.write(f"Model file: {qea_file}\n")
            f.write(f"Model checksum: {qea_checksum}\n")
            f.write(f"Generated files: {len(golden_checksums)}\n")
            f.write("\n")
            f.write("Golden file checksums:\n")
            f.write("-" * 70 + "\n")
            for filename in sorted(golden_checksums.keys()):
                f.write(f"{golden_checksums[filename]}  {filename}\n")

        print(f"   Checksums saved to: {checksums_file}")
        print("\n⚠️  Don't forget to commit the updated golden baseline!")

        return 0

    else:
        # Test mode: compare latest against golden
        print(f"\n🧪 Running regression test...")

        # Check golden exists
        if not golden_dir.exists():
            print(f"\n❌ ERROR: Golden baseline not found at {golden_dir}")
            print(f"   Run with --update to create initial golden baseline")
            return 1

        # Generate latest
        if latest_dir.exists():
            shutil.rmtree(latest_dir)

        print(f"\n1. Generating latest documentation...")
        returncode = generate_documentation(qea_file, latest_dir)

        if returncode != 0:
            print(f"\n❌ FAILED: Could not generate documentation")
            return 1

        latest_checksums = calculate_directory_checksums(latest_dir)
        print(f"   ✓ Generated {len(latest_checksums)} files")

        # Compare
        print(f"\n2. Comparing latest vs golden...")
        matches, differences = compare_documentation(golden_dir, latest_dir)

        if matches:
            # Success!
            print(f"   ✅ All files match golden baseline")
            print("\n" + "=" * 70)
            print("✅ REGRESSION TEST PASSED")
            print("=" * 70)
            print(f"\nDocumentation output is consistent with golden baseline.")
            print(f"Files: {len(latest_checksums)}")

            # Cleanup
            shutil.rmtree(latest_dir)

            return 0
        else:
            # Differences found
            print("\n" + "=" * 70)
            print("❌ REGRESSION TEST FAILED")
            print("=" * 70)
            print("\nDocumentation output differs from golden baseline:")

            for diff in differences:
                print(diff)

            print("\n" + "=" * 70)
            print("\nIf these changes are INTENTIONAL (new feature):")
            print("  python test_doc_consistency.py --update")
            print("\nIf these changes are UNINTENTIONAL (regression):")
            print("  Fix the code and re-run this test")
            print("=" * 70)

            print(f"\nLatest output saved in: {latest_dir}")
            print(f"Golden baseline in: {golden_dir}")

            return 1


if __name__ == "__main__":
    sys.exit(main())
