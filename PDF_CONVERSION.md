# PDF Conversion Guide

This guide explains how to convert the markdown documentation to PDF format using the provided conversion scripts.

## Prerequisites

### Install Pandoc

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended texlive-latex-extra
```

**macOS (using Homebrew):**
```bash
brew install pandoc
brew install --cask basictex
```

**Windows:**
Download and install from:
- Pandoc: https://pandoc.org/installing.html
- MiKTeX: https://miktex.org/download

### Verify Installation

```bash
pandoc --version
pdflatex --version
```

## Usage

### Option 1: Python Script (Recommended)

The Python script (`convert_to_pdf.py`) provides more features and better error handling.

#### Convert Individual Files

```bash
# Convert all markdown files in docs_golden to PDF
python convert_to_pdf.py docs_golden

# Specify output directory
python convert_to_pdf.py docs_golden --output docs_pdf

# Use a different PDF engine
python convert_to_pdf.py docs_golden --engine xelatex
```

#### Create Combined PDF

```bash
# Create a single PDF containing all documentation
python convert_to_pdf.py docs_golden --combined documentation.pdf

# With custom engine
python convert_to_pdf.py docs_golden --combined docs.pdf --engine xelatex
```

#### Available PDF Engines

- **pdflatex** (default) - Good for most documents, widely compatible
- **xelatex** - Better Unicode support, handles more fonts
- **lualatex** - Modern TeX engine with Lua scripting
- **wkhtmltopdf** - Uses WebKit to render HTML to PDF (no LaTeX required)

### Option 2: Shell Script (Simple)

The bash script (`convert_to_pdf.sh`) is simpler and faster for basic conversions.

```bash
# Convert with defaults (docs_golden -> docs_pdf)
./convert_to_pdf.sh

# Specify source and output directories
./convert_to_pdf.sh docs_golden docs_pdf

# Specify PDF engine
./convert_to_pdf.sh docs_golden docs_pdf xelatex
```

## Output Structure

When converting individual files, the directory structure is preserved:

```
docs_pdf/
├── index.pdf
├── use-cases/
│   ├── index.pdf
│   ├── actors.pdf
│   ├── login-use-case.pdf
│   └── ...
├── requirements/
│   ├── index.pdf
│   └── ...
├── components/
├── classes/
├── state-machines/
└── reports/
```

## Examples

### Convert Generated Documentation

```bash
# Generate documentation first
python sparx_doc_generator.py test_model.qea --output docs_latest

# Convert to PDF
python convert_to_pdf.py docs_latest --output docs_latest_pdf
```

### Convert Golden Baseline

```bash
# Convert the golden baseline to PDF
python convert_to_pdf.py docs_golden --output docs_golden_pdf
```

### Create Complete Documentation PDF

```bash
# Create a single comprehensive PDF
python convert_to_pdf.py docs_golden --combined complete_documentation.pdf
```

## Troubleshooting

### Error: "pandoc: pdflatex not found"

Install a LaTeX distribution:
- **Ubuntu/Debian:** `sudo apt-get install texlive-latex-base texlive-fonts-recommended`
- **macOS:** `brew install --cask basictex`
- **Windows:** Install MiKTeX from https://miktex.org/

### Error: "Unicode character not supported"

Use XeLaTeX engine which has better Unicode support:
```bash
python convert_to_pdf.py docs_golden --engine xelatex
```

### PDF Generation is Slow

This is normal. LaTeX compilation can take time, especially for documents with:
- Many files (30+ documents)
- Complex formatting
- Tables and code blocks

The combined PDF option is faster than converting individual files.

### Alternative: Convert via HTML

If PDF generation fails, you can convert to HTML first:
```bash
# Convert to HTML (if convert_to_html.py exists)
python convert_to_html.py docs_golden

# Then use a browser to print to PDF
# Or use wkhtmltopdf:
wkhtmltopdf docs_golden/index.html documentation.pdf
```

## Customization

### Modify PDF Styling

Edit the pandoc commands in the scripts to customize:

```bash
pandoc input.md \
  -o output.pdf \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=3 \
  -V geometry:margin=1in \          # Margins
  -V fontsize=11pt \                # Font size
  -V mainfont="Arial" \             # Font family (xelatex only)
  -V linkcolor=blue \               # Link color
  -V urlcolor=blue \                # URL color
  --highlight-style=tango \         # Code syntax highlighting
  -V papersize=a4                   # Paper size (a4, letter)
```

### Add Custom Header/Footer

Create a LaTeX template and use it with pandoc:
```bash
pandoc input.md -o output.pdf --template=custom-template.tex
```

## Integration with Documentation Generator

You can add PDF generation to the documentation workflow:

```bash
#!/bin/bash
# generate_and_convert.sh

# Generate markdown documentation
python sparx_doc_generator.py test_model.qea --output docs_latest

# Convert to PDF
python convert_to_pdf.py docs_latest --output docs_latest_pdf

# Create combined PDF
python convert_to_pdf.py docs_latest --combined latest_documentation.pdf

echo "Documentation generated and converted to PDF"
echo "  Markdown: docs_latest/"
echo "  PDF: docs_latest_pdf/"
echo "  Combined: latest_documentation.pdf"
```

## Support

For pandoc-related issues, see:
- Pandoc User's Guide: https://pandoc.org/MANUAL.html
- Pandoc PDF documentation: https://pandoc.org/MANUAL.html#creating-a-pdf

For LaTeX issues:
- TeX Stack Exchange: https://tex.stackexchange.com/
