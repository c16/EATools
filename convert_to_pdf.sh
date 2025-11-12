#!/bin/bash
#
# Simple shell script to convert markdown documentation to PDF using pandoc
#
# Usage:
#   ./convert_to_pdf.sh docs_golden
#   ./convert_to_pdf.sh docs_golden docs_pdf
#   ./convert_to_pdf.sh docs_golden docs_pdf xelatex
#

set -e

# Default values
DOCS_DIR="${1:-docs_golden}"
OUTPUT_DIR="${2:-docs_pdf}"
PDF_ENGINE="${3:-pdflatex}"

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc is not installed"
    echo "Install with: sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended"
    echo "Or visit: https://pandoc.org/installing.html"
    exit 1
fi

# Check if source directory exists
if [ ! -d "$DOCS_DIR" ]; then
    echo "Error: Directory $DOCS_DIR does not exist"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Converting markdown files from $DOCS_DIR to PDF in $OUTPUT_DIR"
echo "Using PDF engine: $PDF_ENGINE"
echo ""

# Counters
converted=0
failed=0

# Find all markdown files and convert them
while IFS= read -r -d '' md_file; do
    # Get relative path
    rel_path="${md_file#$DOCS_DIR/}"

    # Create output path
    pdf_file="$OUTPUT_DIR/${rel_path%.md}.pdf"
    pdf_dir="$(dirname "$pdf_file")"

    # Create output directory
    mkdir -p "$pdf_dir"

    # Extract title from filename
    title=$(basename "$md_file" .md | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')

    echo -n "Converting: $rel_path -> ${pdf_file#$OUTPUT_DIR/} ... "

    # Convert to PDF
    if pandoc "$md_file" \
        -o "$pdf_file" \
        --pdf-engine="$PDF_ENGINE" \
        --toc \
        --toc-depth=3 \
        -V geometry:margin=1in \
        -V title="$title" \
        -V linkcolor=blue \
        -V urlcolor=blue \
        --highlight-style=tango \
        2>/dev/null; then
        echo "✓"
        ((converted++))
    else
        echo "✗"
        ((failed++))
    fi
done < <(find "$DOCS_DIR" -type f -name "*.md" -print0)

echo ""
echo "Conversion complete!"
echo "  Converted: $converted"
echo "  Failed: $failed"
echo ""
echo "PDF files are in: $OUTPUT_DIR"
