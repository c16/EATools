#!/usr/bin/env python3
"""
Quick test to verify template integration is working
"""

from pathlib import Path
import sys

# Add the project to path
sys.path.insert(0, str(Path(__file__).parent))

from sparx_ea_doc.extractor import SparxExtractor
from sparx_ea_doc.generators import UseCaseGenerator

def test_template_integration():
    """Test that template integration works"""
    print("Testing template integration...")

    # Path to test model
    test_model = Path(__file__).parent / "test_model.qea"
    if not test_model.exists():
        print(f"ERROR: Test model not found at {test_model}")
        return False

    # Path to templates
    template_dir = Path(__file__).parent / "sparx_ea_doc" / "templates"
    if not template_dir.exists():
        print(f"ERROR: Templates directory not found at {template_dir}")
        return False

    print(f"✓ Test model found: {test_model}")
    print(f"✓ Templates directory found: {template_dir}")

    # Extract data from model
    print("\nExtracting data from model...")
    extractor = SparxExtractor(str(test_model))
    extractor.extract_all()

    print(f"✓ Extracted {len(extractor.use_cases)} use cases")

    # Test generator with template
    print("\nTesting UseCaseGenerator with templates...")
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)

    generator = UseCaseGenerator(extractor, output_dir, template_dir)

    if generator.template_renderer is None:
        print("ERROR: Template renderer was not initialized")
        return False

    print(f"✓ Template renderer initialized")

    # Test generating a use case if we have any
    if extractor.use_cases:
        uc = extractor.use_cases[0]
        print(f"\nGenerating use case: {uc.name}")

        content = generator._generate_single_use_case(uc)

        if not content:
            print("ERROR: No content generated")
            return False

        if uc.name not in content:
            print("ERROR: Use case name not found in generated content")
            return False

        print(f"✓ Use case generated successfully ({len(content)} characters)")
        print("\nFirst 500 characters of generated content:")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)

    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_template_integration()
    sys.exit(0 if success else 1)
