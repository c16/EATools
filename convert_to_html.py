#!/usr/bin/env python3
"""
Convert all markdown documentation to HTML using pandoc.
"""

import re
import subprocess
import sys
from pathlib import Path


def fix_html_links(html_file: Path):
    """
    Fix links in HTML file to point to .html instead of .md

    Args:
        html_file: Path to HTML file to fix
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace .md links with .html links
    # Matches: href="something.md" or href="path/to/something.md"
    content = re.sub(r'href="([^"]+)\.md"', r'href="\1.html"', content)

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)


def convert_md_to_html(docs_dir: Path, css_url: str = "https://cdn.jsdelivr.net/npm/water.css@2/out/water.css"):
    """
    Convert all markdown files in docs_dir to HTML using pandoc

    Args:
        docs_dir: Directory containing markdown files
        css_url: URL to CSS stylesheet for styling
    """
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        print(f"Error: Directory {docs_dir} does not exist")
        sys.exit(1)

    # Find all markdown files
    md_files = list(docs_path.rglob("*.md"))

    if not md_files:
        print(f"No markdown files found in {docs_dir}")
        return

    print(f"Found {len(md_files)} markdown files to convert")

    converted = 0
    failed = 0

    for md_file in md_files:
        # Generate HTML filename
        html_file = md_file.with_suffix('.html')

        # Extract title from file
        title = md_file.stem.replace('-', ' ').title()

        # Build pandoc command
        cmd = [
            'pandoc',
            str(md_file),
            '-o', str(html_file),
            '--standalone',
            '--toc',
            f'--css={css_url}',
            f'--metadata', f'title={title}'
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)

            # Fix links in the generated HTML
            fix_html_links(html_file)

            converted += 1
            print(f"✓ {md_file.relative_to(docs_path)}")
        except subprocess.CalledProcessError as e:
            failed += 1
            print(f"✗ {md_file.relative_to(docs_path)}: {e}")

    print(f"\n{'='*60}")
    print(f"Conversion complete:")
    print(f"  ✓ Converted: {converted}")
    print(f"  ✗ Failed: {failed}")
    print(f"  HTML files saved alongside markdown files")
    print(f"  Links updated to reference .html files")
    print(f"{'='*60}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert_to_html.py <docs_directory> [css_url]")
        print("\nExample:")
        print("  python convert_to_html.py docs")
        print("  python convert_to_html.py docs https://unpkg.com/sakura.css/css/sakura.css")
        sys.exit(1)

    docs_dir = sys.argv[1]
    css_url = sys.argv[2] if len(sys.argv) > 2 else "https://cdn.jsdelivr.net/npm/water.css@2/out/water.css"

    convert_md_to_html(docs_dir, css_url)
