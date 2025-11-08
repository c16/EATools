#!/usr/bin/env python3
"""
Test script to verify documentation generation consistency.

This script:
1. Calculates checksum of the .qea model file
2. Generates documentation twice
3. Compares checksums of all generated files to ensure consistency
"""

import sys
import hashlib
import shutil
from pathlib import Path
from typing import Dict
import subprocess


def calculate_file_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files
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
            # Use relative path as key
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
        print(f"Error running generator: {result.stderr}")

    return result.returncode


def main():
    qea_file = Path("test_model.qea")
    output_dir_1 = Path("docs_run1")
    output_dir_2 = Path("docs_run2")

    print("=" * 70)
    print("Documentation Generation Consistency Test")
    print("=" * 70)

    # Step 1: Verify .qea file exists and calculate checksum
    if not qea_file.exists():
        print(f"ERROR: {qea_file} not found")
        return 1

    print(f"\n1. Calculating checksum of {qea_file}...")
    qea_checksum = calculate_file_checksum(qea_file)
    print(f"   Model checksum: {qea_checksum}")

    # Step 2: First generation run
    print(f"\n2. First documentation generation run...")
    if output_dir_1.exists():
        shutil.rmtree(output_dir_1)

    returncode = generate_documentation(qea_file, output_dir_1)
    if returncode != 0:
        print("   FAILED: First generation run failed")
        return 1
    print("   ✓ First generation complete")

    # Step 3: Calculate checksums of first run
    print(f"\n3. Calculating checksums of generated files (run 1)...")
    checksums_1 = calculate_directory_checksums(output_dir_1)
    print(f"   Generated {len(checksums_1)} files")

    # Step 4: Second generation run
    print(f"\n4. Second documentation generation run...")
    if output_dir_2.exists():
        shutil.rmtree(output_dir_2)

    returncode = generate_documentation(qea_file, output_dir_2)
    if returncode != 0:
        print("   FAILED: Second generation run failed")
        return 1
    print("   ✓ Second generation complete")

    # Step 5: Calculate checksums of second run
    print(f"\n5. Calculating checksums of generated files (run 2)...")
    checksums_2 = calculate_directory_checksums(output_dir_2)
    print(f"   Generated {len(checksums_2)} files")

    # Step 6: Compare checksums
    print(f"\n6. Comparing outputs...")

    # Check file counts match
    if len(checksums_1) != len(checksums_2):
        print(f"   FAILED: Different number of files generated")
        print(f"   Run 1: {len(checksums_1)} files")
        print(f"   Run 2: {len(checksums_2)} files")
        return 1

    # Check all files from run 1 exist in run 2
    missing_files = set(checksums_1.keys()) - set(checksums_2.keys())
    if missing_files:
        print(f"   FAILED: Files in run 1 but not in run 2:")
        for f in sorted(missing_files):
            print(f"      - {f}")
        return 1

    # Check all files from run 2 exist in run 1
    extra_files = set(checksums_2.keys()) - set(checksums_1.keys())
    if extra_files:
        print(f"   FAILED: Files in run 2 but not in run 1:")
        for f in sorted(extra_files):
            print(f"      - {f}")
        return 1

    # Compare checksums for each file
    mismatched_files = []
    for filename in checksums_1.keys():
        if checksums_1[filename] != checksums_2[filename]:
            mismatched_files.append(filename)

    if mismatched_files:
        print(f"   FAILED: {len(mismatched_files)} file(s) have different content:")
        for f in sorted(mismatched_files):
            print(f"      - {f}")
            print(f"        Run 1: {checksums_1[f]}")
            print(f"        Run 2: {checksums_2[f]}")
        return 1

    # Success!
    print(f"   ✓ All {len(checksums_1)} files are identical")

    # Step 7: Save checksums to file for reference
    print(f"\n7. Saving checksums to file...")
    checksums_file = Path("test_model_checksums.txt")
    with open(checksums_file, 'w') as f:
        f.write(f"Model file: {qea_file}\n")
        f.write(f"Model checksum: {qea_checksum}\n")
        f.write(f"Generated files: {len(checksums_1)}\n")
        f.write("\n")
        f.write("File checksums:\n")
        f.write("-" * 70 + "\n")
        for filename in sorted(checksums_1.keys()):
            f.write(f"{checksums_1[filename]}  {filename}\n")

    print(f"   Checksums saved to: {checksums_file}")

    # Cleanup
    print(f"\n8. Cleaning up test directories...")
    if output_dir_1.exists():
        shutil.rmtree(output_dir_1)
    if output_dir_2.exists():
        shutil.rmtree(output_dir_2)
    print(f"   ✓ Cleanup complete")

    print("\n" + "=" * 70)
    print("✓ CONSISTENCY TEST PASSED")
    print("=" * 70)
    print(f"\nDocumentation generation is deterministic for:")
    print(f"  Model: {qea_file}")
    print(f"  Checksum: {qea_checksum}")
    print(f"  Files: {len(checksums_1)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
