#!/usr/bin/env python3
"""
Test text cleaning with various problematic characters and encodings.

Tests the clean_text_content function with text from different sources that
might have different codepages, unprintable characters, or encoding issues.
"""

from sparx_ea_doc.utils import clean_text_content


def test_text_cleaning():
    """Test various problematic text inputs"""

    tests = [
        # Test 1: None and empty
        {
            'name': 'None input',
            'input': None,
            'expected': '',
        },
        {
            'name': 'Empty string',
            'input': '',
            'expected': '',
        },

        # Test 2: Null bytes
        {
            'name': 'Null bytes',
            'input': 'Hello\x00World\x00Test',
            'expected': 'HelloWorldTest',
        },

        # Test 3: HTML tags and entities
        {
            'name': 'HTML tags',
            'input': '<p>This is a <b>test</b></p>',
            'expected': 'This is a test',
        },
        {
            'name': 'HTML entities',
            'input': 'Test &amp; Demo &lt;example&gt;',
            'expected': 'Test & Demo <example>',
        },

        # Test 4: Different line endings
        {
            'name': 'Windows line endings',
            'input': 'Line1\r\nLine2\r\nLine3',
            'expected': 'Line1\nLine2\nLine3',
        },
        {
            'name': 'Old Mac line endings',
            'input': 'Line1\rLine2\rLine3',
            'expected': 'Line1\nLine2\nLine3',
        },

        # Test 5: Unicode characters from different languages
        {
            'name': 'Unicode - European characters',
            'input': 'Café résumé naïve',
            'expected': 'Café résumé naïve',
        },
        {
            'name': 'Unicode - Greek',
            'input': 'Αυτό είναι ένα τεστ',
            'expected': 'Αυτό είναι ένα τεστ',
        },
        {
            'name': 'Unicode - Cyrillic',
            'input': 'Это тест',
            'expected': 'Это тест',
        },
        {
            'name': 'Unicode - Chinese',
            'input': '这是一个测试',
            'expected': '这是一个测试',
        },
        {
            'name': 'Unicode - Japanese',
            'input': 'これはテストです',
            'expected': 'これはテストです',
        },

        # Test 6: Zero-width and format characters
        {
            'name': 'Zero-width space',
            'input': 'Word\u200bWord',
            'expected': 'WordWord',
        },
        {
            'name': 'Zero-width joiner',
            'input': 'Word\u200dWord',
            'expected': 'WordWord',
        },
        {
            'name': 'Byte order mark',
            'input': '\ufeffTest Content',
            'expected': 'Test Content',
        },

        # Test 7: Replacement character (indicates encoding error)
        {
            'name': 'Replacement character',
            'input': 'Test\ufffdContent',
            'expected': 'TestContent',
        },

        # Test 8: Control characters
        {
            'name': 'Bell character',
            'input': 'Test\x07Content',
            'expected': 'TestContent',
        },
        {
            'name': 'Escape character',
            'input': 'Test\x1bContent',
            'expected': 'TestContent',
        },

        # Test 9: Excessive whitespace
        {
            'name': 'Multiple spaces',
            'input': 'Test     Content     Here',
            'expected': 'Test Content Here',
        },
        {
            'name': 'Multiple newlines',
            'input': 'Line1\n\n\n\n\nLine2',
            'expected': 'Line1\n\nLine2',
        },
        {
            'name': 'Mixed whitespace',
            'input': 'Test\t\t\tContent   \t  Here',
            'expected': 'Test Content Here',
        },

        # Test 10: Real-world copy/paste scenarios
        {
            'name': 'Word document paste',
            'input': '<p>This text was copied from <b>Microsoft Word</b> with &ldquo;smart quotes&rdquo; and an em-dash&mdash;like this.</p>',
            # Note: quotes may be normalized to different unicode forms
            'expected_contains': ['Microsoft Word', 'smart quotes', 'em-dash', 'like this'],
        },
        {
            'name': 'PDF copy paste with ligatures',
            'input': 'The office workflow includes filing documents.',  # 'ffi' might be ligature
            'expected': 'The office workflow includes filing documents.',
        },

        # Test 11: Combined problematic characters
        {
            'name': 'Multiple issues combined',
            'input': '<p>Test\x00with\r\nnull\u200bbytes\x07and&nbsp;HTML</p>\ufeff',
            'expected': 'Testwith\nnullbytesand HTML',
        },

        # Test 12: Bytes input (simulating different codepages)
        {
            'name': 'UTF-8 bytes',
            'input': 'Café'.encode('utf-8'),
            'expected': 'Café',
        },
        {
            'name': 'Windows-1252 bytes',
            'input': 'Café'.encode('windows-1252'),
            'expected': 'Café',
        },
        {
            'name': 'ISO-8859-1 bytes',
            'input': 'Café'.encode('iso-8859-1'),
            'expected': 'Café',
        },

        # Test 13: Preserve intentional formatting
        {
            'name': 'Preserve tabs in structured content',
            'input': 'Step 1:\tAction A\nStep 2:\tAction B',
            'expected': 'Step 1: Action A\nStep 2: Action B',
        },
        {
            'name': 'Preserve paragraph breaks',
            'input': 'Paragraph 1\n\nParagraph 2',
            'expected': 'Paragraph 1\n\nParagraph 2',
        },
    ]

    print("=" * 80)
    print("Testing Text Cleaning Function")
    print("=" * 80)

    passed = 0
    failed = 0

    for test in tests:
        result = clean_text_content(test['input'])

        # Check if using 'expected' or 'expected_contains'
        if 'expected_contains' in test:
            success = all(substring in result for substring in test['expected_contains'])
        else:
            success = result == test['expected']

        if success:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"

        print(f"\n{status}: {test['name']}")
        if not success:
            print(f"  Input:    {repr(test['input'])}")
            if 'expected_contains' in test:
                print(f"  Expected to contain: {test['expected_contains']}")
            else:
                print(f"  Expected: {repr(test['expected'])}")
            print(f"  Got:      {repr(result)}")

    print("\n" + "=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 80)

    return failed == 0


if __name__ == '__main__':
    success = test_text_cleaning()
    exit(0 if success else 1)
