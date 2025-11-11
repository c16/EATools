#!/usr/bin/env python3
"""
Convert all markdown documentation to HTML using pandoc.
"""

import re
import subprocess
import sys
from pathlib import Path
import shutil


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


def convert_md_to_html(docs_dir: Path, output_dir: Path = None, css_url: str = "https://cdn.jsdelivr.net/npm/water.css@2/out/water.css"):
    """
    Convert all markdown files in docs_dir to HTML using pandoc

    Args:
        docs_dir: Directory containing markdown files
        output_dir: Output directory for HTML files (default: same as docs_dir)
        css_url: URL to CSS stylesheet for styling
    """
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        print(f"Error: Directory {docs_dir} does not exist")
        sys.exit(1)

    # If output_dir specified, use it; otherwise output alongside markdown
    if output_dir:
        output_path = Path(output_dir)
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        separate_tree = True
        print(f"Output directory: {output_path}")
    else:
        output_path = docs_path
        separate_tree = False

    # Find all markdown files
    md_files = list(docs_path.rglob("*.md"))

    if not md_files:
        print(f"No markdown files found in {docs_dir}")
        return

    print(f"Found {len(md_files)} markdown files to convert")

    converted = 0
    failed = 0

    for md_file in md_files:
        # Calculate relative path from docs_dir
        rel_path = md_file.relative_to(docs_path)

        # Generate HTML filename in output tree
        if separate_tree:
            html_file = output_path / rel_path.with_suffix('.html')
            # Create parent directories in output tree
            html_file.parent.mkdir(parents=True, exist_ok=True)
        else:
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
            print(f"✓ {rel_path}")
        except subprocess.CalledProcessError as e:
            failed += 1
            print(f"✗ {rel_path}: {e}")

    # Copy diagrams directory if it exists
    diagrams_src = docs_path / 'diagrams'
    if diagrams_src.exists() and diagrams_src.is_dir():
        if separate_tree:
            diagrams_dst = output_path / 'diagrams'
            if diagrams_dst.exists():
                shutil.rmtree(diagrams_dst)
            shutil.copytree(diagrams_src, diagrams_dst)
            print(f"✓ Copied diagrams directory")
        # If not separate tree, diagrams are already in the right place

    print(f"\n{'='*60}")
    print(f"Conversion complete:")
    print(f"  ✓ Converted: {converted}")
    print(f"  ✗ Failed: {failed}")
    if separate_tree:
        print(f"  HTML files saved to: {output_path}")
    else:
        print(f"  HTML files saved alongside markdown files")
    print(f"  Links updated to reference .html files")
    print(f"{'='*60}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert_to_html.py <docs_directory> [output_directory] [css_url]")
        print("\nExamples:")
        print("  python convert_to_html.py docs")
        print("  python convert_to_html.py docs docs_html")
        print("  python convert_to_html.py docs docs_html https://unpkg.com/sakura.css/css/sakura.css")
        sys.exit(1)

    docs_dir = sys.argv[1]

    # Determine output_dir and css_url based on number of arguments
    output_dir = None
    css_url = "https://cdn.jsdelivr.net/npm/water.css@2/out/water.css"

    if len(sys.argv) >= 3:
        # Check if second argument is a URL (starts with http)
        if sys.argv[2].startswith('http'):
            css_url = sys.argv[2]
        else:
            output_dir = sys.argv[2]

    if len(sys.argv) >= 4:
        css_url = sys.argv[3]

    convert_md_to_html(docs_dir, output_dir, css_url)
