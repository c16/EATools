#!/usr/bin/env python3
"""
Convert all markdown documentation to PDF using pandoc.

Requirements:
    - pandoc (with PDF support)
    - pdflatex or xelatex or other LaTeX engine
    - Or use wkhtmltopdf as an alternative

Usage:
    python convert_to_pdf.py docs_golden
    python convert_to_pdf.py docs_golden --output docs_pdf
    python convert_to_pdf.py docs_golden --engine xelatex
    python convert_to_pdf.py docs_golden --combined combined.pdf
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_pandoc():
    """Check if pandoc is installed"""
    try:
        result = subprocess.run(['pandoc', '--version'],
                              capture_output=True,
                              text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def convert_md_to_pdf(md_file: Path, output_file: Path, engine: str = "pdflatex"):
    """
    Convert a single markdown file to PDF using pandoc

    Args:
        md_file: Path to markdown file
        output_file: Path to output PDF file
        engine: PDF engine to use (pdflatex, xelatex, lualatex, wkhtmltopdf)
    """
    # Extract title from file
    title = md_file.stem.replace('-', ' ').title()

    # Build pandoc command
    cmd = [
        'pandoc',
        str(md_file),
        '-o', str(output_file),
        '--pdf-engine=' + engine,
        '--toc',
        '--toc-depth=3',
        '-V', 'geometry:margin=1in',
        '-V', f'title={title}',
        '-V', 'linkcolor=blue',
        '-V', 'urlcolor=blue',
        '--highlight-style=tango',
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, str(e)


def convert_directory(docs_dir: Path, output_dir: Path = None, engine: str = "pdflatex"):
    """
    Convert all markdown files in docs_dir to PDF

    Args:
        docs_dir: Directory containing markdown files
        output_dir: Output directory for PDF files (if None, creates PDFs alongside markdown)
        engine: PDF engine to use
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
    print(f"Using PDF engine: {engine}")
    print()

    converted = 0
    failed = 0
    failures = []

    for md_file in md_files:
        # Determine output path
        if output_dir:
            # Preserve directory structure in output
            rel_path = md_file.relative_to(docs_path)
            pdf_file = output_dir / rel_path.with_suffix('.pdf')
            pdf_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Place PDF next to markdown file
            pdf_file = md_file.with_suffix('.pdf')

        print(f"Converting: {md_file.relative_to(docs_path)} -> {pdf_file.name}", end='... ')

        success, error = convert_md_to_pdf(md_file, pdf_file, engine)

        if success:
            print("✓")
            converted += 1
        else:
            print("✗")
            failed += 1
            failures.append((md_file, error))

    print()
    print(f"Conversion complete!")
    print(f"  Converted: {converted}")
    print(f"  Failed: {failed}")

    if failures:
        print()
        print("Failed conversions:")
        for md_file, error in failures:
            print(f"  - {md_file.name}")
            if error and len(error) < 200:
                print(f"    Error: {error.strip()}")


def create_combined_pdf(docs_dir: Path, output_file: Path, engine: str = "pdflatex"):
    """
    Create a single combined PDF from all markdown files

    Args:
        docs_dir: Directory containing markdown files
        output_file: Output PDF file path
        engine: PDF engine to use
    """
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        print(f"Error: Directory {docs_dir} does not exist")
        sys.exit(1)

    # Find all markdown files
    md_files = sorted(docs_path.rglob("*.md"))

    if not md_files:
        print(f"No markdown files found in {docs_dir}")
        return

    print(f"Creating combined PDF from {len(md_files)} markdown files")
    print(f"Output: {output_file}")
    print(f"Using PDF engine: {engine}")
    print()

    # Build pandoc command with all markdown files
    cmd = [
        'pandoc',
        *[str(f) for f in md_files],
        '-o', str(output_file),
        '--pdf-engine=' + engine,
        '--toc',
        '--toc-depth=3',
        '-V', 'geometry:margin=1in',
        '-V', 'title=Documentation',
        '-V', 'linkcolor=blue',
        '-V', 'urlcolor=blue',
        '--highlight-style=tango',
    ]

    try:
        print("Converting...", end=' ')
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓")
        print(f"\nCombined PDF created successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print("✗")
        print(f"\nError creating combined PDF:")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print("✗")
        print(f"\nError: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Convert markdown documentation to PDF using pandoc',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert_to_pdf.py docs_golden
  python convert_to_pdf.py docs_golden --output docs_pdf
  python convert_to_pdf.py docs_golden --engine xelatex
  python convert_to_pdf.py docs_golden --combined documentation.pdf

PDF Engines:
  pdflatex  - Default, good for most documents
  xelatex   - Better Unicode support, handles more fonts
  lualatex  - Modern TeX engine with Lua scripting
  wkhtmltopdf - Uses WebKit to render HTML to PDF (no LaTeX required)
        """
    )
    parser.add_argument('docs_dir', help='Directory containing markdown files')
    parser.add_argument('--output', '-o', help='Output directory for PDF files')
    parser.add_argument('--engine', '-e', default='pdflatex',
                       choices=['pdflatex', 'xelatex', 'lualatex', 'wkhtmltopdf'],
                       help='PDF engine to use (default: pdflatex)')
    parser.add_argument('--combined', '-c', help='Create a single combined PDF with this filename')

    args = parser.parse_args()

    # Check if pandoc is installed
    if not check_pandoc():
        print("Error: pandoc is not installed or not in PATH")
        print("Install pandoc from: https://pandoc.org/installing.html")
        sys.exit(1)

    docs_dir = Path(args.docs_dir)
    output_dir = Path(args.output) if args.output else None

    if args.combined:
        # Create combined PDF
        output_file = Path(args.combined)
        create_combined_pdf(docs_dir, output_file, args.engine)
    else:
        # Convert each file individually
        convert_directory(docs_dir, output_dir, args.engine)


if __name__ == '__main__':
    main()
