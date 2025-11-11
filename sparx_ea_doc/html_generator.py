"""
HTML Documentation Generator

Converts markdown documentation to HTML using native Python markdown library.
Does not use pandoc - pure Python implementation.
"""

import re
import shutil
import logging
from pathlib import Path
from typing import Optional

try:
    import markdown
    from markdown.extensions.toc import TocExtension
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
    from markdown.extensions.codehilite import CodeHiliteExtension
except ImportError:
    raise ImportError(
        "markdown library is required for HTML generation. "
        "Install it with: pip install markdown"
    )

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Generate HTML documentation from markdown files"""

    # Default CSS for styling (embedded)
    DEFAULT_CSS = """
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        line-height: 1.6;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        color: #333;
        background: #f5f5f5;
    }

    .container {
        background: white;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }

    h1 {
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }

    h2 {
        border-bottom: 2px solid #bdc3c7;
        padding-bottom: 8px;
    }

    a {
        color: #3498db;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    code {
        background: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 3px;
        padding: 2px 6px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9em;
    }

    pre {
        background: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        overflow-x: auto;
    }

    pre code {
        border: none;
        padding: 0;
        background: none;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }

    th {
        background: #3498db;
        color: white;
        font-weight: bold;
    }

    tr:nth-child(even) {
        background: #f8f8f8;
    }

    blockquote {
        border-left: 4px solid #3498db;
        padding-left: 20px;
        margin-left: 0;
        color: #555;
        font-style: italic;
    }

    img {
        max-width: 100%;
        height: auto;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    ul, ol {
        margin: 10px 0;
        padding-left: 30px;
    }

    li {
        margin: 5px 0;
    }

    .toc {
        background: #ecf0f1;
        border-radius: 5px;
        padding: 20px;
        margin: 20px 0;
    }

    .toc ul {
        list-style-type: none;
        padding-left: 0;
    }

    .toc ul ul {
        padding-left: 20px;
    }

    .breadcrumb {
        color: #7f8c8d;
        font-size: 0.9em;
        margin-bottom: 20px;
    }

    .metadata {
        background: #ecf0f1;
        border-radius: 5px;
        padding: 15px;
        margin: 20px 0;
        font-size: 0.9em;
    }

    .metadata strong {
        color: #2c3e50;
    }

    hr {
        border: none;
        border-top: 2px solid #bdc3c7;
        margin: 30px 0;
    }
    """

    def __init__(self, docs_dir: Path, output_dir: Optional[Path] = None, css_url: Optional[str] = None):
        """
        Initialize HTML generator

        Args:
            docs_dir: Directory containing markdown files
            output_dir: Output directory for HTML files (default: docs_html in same parent as docs_dir)
            css_url: Optional URL to external CSS stylesheet
        """
        self.docs_dir = Path(docs_dir)

        if not self.docs_dir.exists():
            raise FileNotFoundError(f"Documentation directory not found: {self.docs_dir}")

        # Default output directory: docs_html alongside docs
        if output_dir is None:
            self.output_dir = self.docs_dir.parent / (self.docs_dir.name + "_html")
        else:
            self.output_dir = Path(output_dir)

        self.css_url = css_url
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize markdown processor with extensions
        self.md = markdown.Markdown(
            extensions=[
                TocExtension(title='Table of Contents', toc_depth='2-3'),
                TableExtension(),
                FencedCodeExtension(),
                CodeHiliteExtension(css_class='highlight'),
                'nl2br',  # Convert newlines to <br>
                'sane_lists',  # Better list handling
            ],
            output_format='html5'
        )

        logger.info(f"HTML Generator initialized: {self.docs_dir} -> {self.output_dir}")

    def _fix_md_links_to_html(self, html_content: str) -> str:
        """
        Convert all .md links to .html links in HTML content

        Args:
            html_content: HTML content with .md links

        Returns:
            HTML content with .html links
        """
        # Match href="...md" and href="...md#anchor"
        html_content = re.sub(r'href="([^"]+)\.md(#[^"]*)?(")', r'href="\1.html\2\3', html_content)
        return html_content

    def _generate_html_wrapper(self, title: str, content: str, breadcrumb: str = "") -> str:
        """
        Wrap markdown-generated HTML in a complete HTML document

        Args:
            title: Page title
            content: HTML content (converted from markdown)
            breadcrumb: Breadcrumb navigation HTML

        Returns:
            Complete HTML document
        """
        # Use external CSS if provided, otherwise embed default CSS
        if self.css_url:
            css_link = f'<link rel="stylesheet" href="{self.css_url}">'
        else:
            css_link = f'<style>{self.DEFAULT_CSS}</style>'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {css_link}
</head>
<body>
    <div class="container">
        {breadcrumb}
        {content}
    </div>
</body>
</html>
"""
        return html

    def _extract_breadcrumb(self, md_content: str) -> tuple[str, str]:
        """
        Extract breadcrumb from markdown content (first line if it starts with '[')

        Args:
            md_content: Markdown content

        Returns:
            Tuple of (breadcrumb_html, remaining_content)
        """
        lines = md_content.split('\n', 1)

        if lines and lines[0].strip().startswith('['):
            # First line is breadcrumb
            breadcrumb_md = lines[0].strip()
            remaining_content = lines[1] if len(lines) > 1 else ""

            # Convert breadcrumb markdown to HTML
            breadcrumb_html = self.md.convert(breadcrumb_md)
            breadcrumb_html = f'<div class="breadcrumb">{breadcrumb_html}</div>'

            # Reset markdown processor
            self.md.reset()

            return breadcrumb_html, remaining_content

        return "", md_content

    def convert_file(self, md_file: Path) -> Path:
        """
        Convert a single markdown file to HTML

        Args:
            md_file: Path to markdown file

        Returns:
            Path to generated HTML file
        """
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Extract breadcrumb if present
        breadcrumb_html, md_content = self._extract_breadcrumb(md_content)

        # Convert markdown to HTML
        html_content = self.md.convert(md_content)

        # Fix links to point to .html files
        html_content = self._fix_md_links_to_html(html_content)

        # Reset markdown processor for next file
        self.md.reset()

        # Generate title from filename
        title = md_file.stem.replace('-', ' ').replace('_', ' ').title()

        # Wrap in complete HTML document
        full_html = self._generate_html_wrapper(title, html_content, breadcrumb_html)

        # Calculate relative path and output path
        rel_path = md_file.relative_to(self.docs_dir)
        html_file = self.output_dir / rel_path.with_suffix('.html')

        # Create parent directories
        html_file.parent.mkdir(parents=True, exist_ok=True)

        # Write HTML file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)

        return html_file

    def generate_all(self) -> dict:
        """
        Convert all markdown files to HTML

        Returns:
            Dictionary with statistics (converted, failed, total)
        """
        logger.info(f"Starting HTML generation from {self.docs_dir}")

        # Find all markdown files
        md_files = list(self.docs_dir.rglob("*.md"))

        if not md_files:
            logger.warning(f"No markdown files found in {self.docs_dir}")
            return {'converted': 0, 'failed': 0, 'total': 0}

        logger.info(f"Found {len(md_files)} markdown files to convert")

        converted = 0
        failed = 0
        failed_files = []

        for md_file in md_files:
            try:
                html_file = self.convert_file(md_file)
                converted += 1
                rel_path = md_file.relative_to(self.docs_dir)
                logger.debug(f"✓ Converted: {rel_path}")
            except Exception as e:
                failed += 1
                failed_files.append((md_file, str(e)))
                logger.error(f"✗ Failed to convert {md_file}: {e}")

        # Copy diagrams directory if it exists
        diagrams_src = self.docs_dir / 'diagrams'
        if diagrams_src.exists() and diagrams_src.is_dir():
            diagrams_dst = self.output_dir / 'diagrams'
            if diagrams_dst.exists():
                shutil.rmtree(diagrams_dst)
            shutil.copytree(diagrams_src, diagrams_dst)
            logger.info("✓ Copied diagrams directory")

        # Log summary
        logger.info("=" * 60)
        logger.info("HTML Generation Complete:")
        logger.info(f"  ✓ Converted: {converted}")
        logger.info(f"  ✗ Failed: {failed}")
        logger.info(f"  Total: {len(md_files)}")
        logger.info(f"  Output: {self.output_dir}")
        logger.info("=" * 60)

        if failed_files:
            logger.warning("Failed files:")
            for md_file, error in failed_files:
                logger.warning(f"  - {md_file.name}: {error}")

        return {
            'converted': converted,
            'failed': failed,
            'total': len(md_files),
            'output_dir': str(self.output_dir),
            'failed_files': failed_files
        }
