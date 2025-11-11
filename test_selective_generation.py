#!/usr/bin/env python3
"""
Test script for selective documentation generation
"""

import tempfile
import shutil
from pathlib import Path

from sparx_ea_doc.extractor import SparxExtractor
from sparx_ea_doc.selective_generator import SelectiveGenerator

def test_selective_generation():
    """Test that selective generation works correctly"""
    print("Testing selective generation...")

    # Setup
    qea_path = Path("test_model.qea")
    if not qea_path.exists():
        print(f"Error: {qea_path} not found")
        return False

    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)

        # Extract model data
        print("Extracting model data...")
        extractor = SparxExtractor(qea_path)
        extractor.extract_all()

        # Test 1: Generate only use case index and actors
        print("\nTest 1: Generate only selected files...")
        selected_files = {
            'use-cases/index.md',
            'use-cases/actors.md',
            'index.md'
        }

        generator = SelectiveGenerator(extractor, output_dir, selected_files)
        generator.generate_all()

        # Verify only selected files were generated
        generated_files = set()
        for file_path in output_dir.rglob('*.md'):
            rel_path = file_path.relative_to(output_dir)
            generated_files.add(str(rel_path).replace('\\', '/'))

        print(f"Expected files: {selected_files}")
        print(f"Generated files: {generated_files}")

        if generated_files == selected_files:
            print("✓ Test 1 passed: Only selected files were generated")
        else:
            print("✗ Test 1 failed: File mismatch")
            print(f"  Extra files: {generated_files - selected_files}")
            print(f"  Missing files: {selected_files - generated_files}")
            return False

        # Clean up for next test
        shutil.rmtree(output_dir)
        output_dir.mkdir()

        # Test 2: Generate all files
        print("\nTest 2: Generate all files...")
        all_files = {
            'index.md',
            'use-cases/index.md',
            'use-cases/actors.md',
        }

        # Add all use cases
        for uc in extractor.use_cases:
            filename = f"{uc.name.lower().replace(' ', '-')}.md"
            all_files.add(f'use-cases/{filename}')

        generator = SelectiveGenerator(extractor, output_dir, all_files)
        generator.generate_all()

        generated_files = set()
        for file_path in output_dir.rglob('*.md'):
            rel_path = file_path.relative_to(output_dir)
            generated_files.add(str(rel_path).replace('\\', '/'))

        print(f"Generated {len(generated_files)} files")

        if all_files.issubset(generated_files):
            print("✓ Test 2 passed: All expected files were generated")
        else:
            print("✗ Test 2 failed")
            print(f"  Missing files: {all_files - generated_files}")
            return False

    print("\n✓ All tests passed!")
    return True


if __name__ == '__main__':
    success = test_selective_generation()
    exit(0 if success else 1)
