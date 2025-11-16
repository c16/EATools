"""
Utility functions for documentation generation
"""

import re
import html
import unicodedata
from pathlib import Path
from typing import List, Tuple, Optional


def generate_breadcrumbs(file_path: Path, output_dir: Path, page_title: str) -> str:
    """
    Generate breadcrumb navigation for a documentation page.

    Args:
        file_path: Path to the current file (absolute)
        output_dir: Base output directory (absolute)
        page_title: Title of the current page

    Returns:
        Markdown formatted breadcrumb string

    Examples:
        For classes/domain/order.md:
        > [Home](../../index.md) > [Classes](../index.md) > [Domain](index.md) > Order

        For use-cases/login-use-case.md:
        > [Home](../index.md) > [Use Cases](index.md) > Login Use Case
    """
    # Get relative path from output_dir to file
    try:
        rel_path = file_path.relative_to(output_dir)
    except ValueError:
        # If file_path is not under output_dir, return empty breadcrumbs
        return ""

    # Build breadcrumb parts
    parts: List[Tuple[str, str]] = []

    # Calculate depth (how many levels deep from output_dir)
    depth = len(rel_path.parents) - 1  # -1 because parents includes '.'

    # Add Home link
    if depth > 0:
        home_path = "../" * depth + "index.md"
    else:
        home_path = "index.md"
    parts.append(("Home", home_path))

    # Add intermediate directory links
    # Check if current file is an index.md
    is_index = file_path.name == 'index.md'

    current_path = output_dir
    for i, part in enumerate(rel_path.parents[:-1]):  # Exclude the last parent (output_dir itself)
        # Reverse order - parents are from deepest to shallowest
        actual_parts = list(reversed(list(rel_path.parents[:-1])))
        if i < len(actual_parts):
            dir_part = actual_parts[i]
            dir_name = dir_part.name

            # Skip the last directory if this is an index.md file
            # (the directory name will be shown as the current page title)
            if is_index and i == len(actual_parts) - 1:
                continue

            # Calculate relative path from current file to this index
            levels_up = depth - i - 1
            if levels_up > 0:
                index_path = "../" * levels_up + "index.md"
            else:
                index_path = "index.md"

            # Format directory name for display
            display_name = _format_section_name(dir_name)
            parts.append((display_name, index_path))

    # Add current page (no link, just title)
    parts.append((page_title, None))

    # Build breadcrumb string
    breadcrumb = " > ".join(
        f"[{name}]({path})" if path else name
        for name, path in parts
    )

    return breadcrumb + "\n\n"


def _format_section_name(dir_name: str) -> str:
    """
    Format directory name for display in breadcrumbs.

    Examples:
        'use-cases' -> 'Use Cases'
        'state-machines' -> 'State Machines'
        'domain' -> 'Domain'
    """
    # Replace hyphens with spaces and title case
    formatted = dir_name.replace('-', ' ').replace('_', ' ')

    # Special cases
    if formatted.lower() == 'classes':
        return 'Classes'
    elif formatted.lower() == 'components':
        return 'Components'
    elif formatted.lower() == 'reports':
        return 'Reports'
    else:
        # Title case
        return formatted.title()


def sanitize_filename(name: str) -> str:
    """
    Convert a name to a safe filename.

    Args:
        name: The name to sanitize

    Returns:
        Sanitized filename (without extension)

    Examples:
        'Login Use Case' -> 'login-use-case'
        'Add Item to Basket' -> 'add-item-to-basket'
        'Name\twith\ttabs' -> 'name-with-tabs'
        'Name\nwith\nnewlines' -> 'name-with-newlines'
    """
    import re
    import unicodedata

    # Handle None or empty string
    if not name:
        return 'unnamed'

    # Convert to string (in case it's not)
    name = str(name)

    # Normalize unicode characters
    # NFKD = Normal Form KD (Compatibility Decomposition)
    name = unicodedata.normalize('NFKD', name)

    # Remove control characters and other unprintable characters
    # Keep only printable ASCII and common unicode chars
    name = ''.join(char for char in name if unicodedata.category(char)[0] != 'C')

    # Convert to lowercase
    filename = name.lower()

    # Replace whitespace (spaces, tabs, newlines) with hyphens
    filename = re.sub(r'\s+', '-', filename)

    # Remove or replace problematic characters for filesystems
    # Windows: \ / : * ? " < > |
    # Unix: / (null)
    filename = filename.replace('/', '-').replace('\\', '-')
    filename = filename.replace(':', '-').replace('*', '-')
    filename = filename.replace('?', '').replace('"', '')
    filename = filename.replace('<', '').replace('>', '')
    filename = filename.replace('|', '-')

    # Remove any remaining non-alphanumeric characters except hyphens and underscores
    filename = re.sub(r'[^a-z0-9\-_]', '', filename)

    # Remove multiple consecutive hyphens
    filename = re.sub(r'-+', '-', filename)

    # Remove leading/trailing hyphens or underscores
    filename = filename.strip('-_')

    # Ensure filename is not empty after sanitization
    if not filename:
        filename = 'unnamed'

    # Limit length to 200 characters (leaving room for extension and object_id)
    if len(filename) > 200:
        filename = filename[:200].rstrip('-_')

    return filename


def generate_filename_with_id(name: str, object_id: int, prefix: str = '', extension: str = 'md') -> str:
    """
    Generate a filename that includes the object_id to prevent name clashes.

    Args:
        name: The element name
        object_id: The object ID from the database
        prefix: Optional prefix (e.g., 'sm-' for state machines, 'comp-' for components)
        extension: File extension without the dot (default: 'md')

    Returns:
        Sanitized filename with object_id (e.g., 'login-use-case-123.md')

    Examples:
        generate_filename_with_id('Login Use Case', 123) -> 'login-use-case-123.md'
        generate_filename_with_id('Order', 456, extension='html') -> 'order-456.html'
        generate_filename_with_id('PaymentSM', 789, prefix='sm-') -> 'sm-paymentsm-789.md'
    """
    sanitized_name = sanitize_filename(name)

    # Combine prefix, name, and object_id
    if prefix:
        filename = f"{prefix}{sanitized_name}-{object_id}.{extension}"
    else:
        filename = f"{sanitized_name}-{object_id}.{extension}"

    return filename


def clean_text_content(text: Optional[str], remove_html: bool = True) -> str:
    """
    Robustly clean text content to handle different codepages and unprintable characters.

    This function ensures text can always be safely written to files without encoding errors.
    It handles text pasted from various sources with different codepages (UTF-8, Windows-1252,
    ISO-8859-1, etc.) and removes problematic characters.

    Args:
        text: The text to clean (can be None)
        remove_html: Whether to remove HTML tags (default: True)

    Returns:
        Cleaned text safe for writing to files

    Examples:
        clean_text_content(None) -> ''
        clean_text_content('Hello\x00World') -> 'HelloWorld'
        clean_text_content('<p>Test</p>') -> 'Test'
        clean_text_content('Café\u200b') -> 'Café'  (removes zero-width space)
    """
    # Handle None or empty
    if not text:
        return ""

    # Convert to string if not already
    try:
        if isinstance(text, bytes):
            # Try multiple encodings in order of likelihood
            for encoding in ['utf-8', 'windows-1252', 'iso-8859-1', 'cp1252']:
                try:
                    text = text.decode(encoding)
                    break
                except (UnicodeDecodeError, AttributeError):
                    continue
            else:
                # Last resort: decode with errors='replace'
                text = text.decode('utf-8', errors='replace')
        else:
            text = str(text)
    except Exception:
        # If all else fails, return empty string
        return ""

    # Remove null bytes (can cause issues in files)
    text = text.replace('\x00', '')

    # Remove HTML tags if requested
    if remove_html:
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        try:
            text = html.unescape(text)
        except Exception:
            pass  # If unescape fails, continue with original text

    # Normalize unicode to NFKC (Compatibility Composition)
    # This handles composed vs decomposed characters
    try:
        text = unicodedata.normalize('NFKC', text)
    except Exception:
        pass  # If normalization fails, continue with original text

    # Remove or replace problematic unicode categories
    cleaned_chars = []
    for char in text:
        try:
            category = unicodedata.category(char)
            # Keep most characters, but filter out problematic ones
            if category[0] == 'C':  # Control characters
                # Keep common whitespace (tab, newline, carriage return)
                if char in ['\t', '\n', '\r']:
                    cleaned_chars.append(char)
                # Skip other control characters
            elif category == 'Cf':  # Format characters (like zero-width space)
                # Skip format characters except soft hyphen
                if char != '\u00ad':
                    continue
                cleaned_chars.append(char)
            else:
                # Keep the character
                cleaned_chars.append(char)
        except Exception:
            # If we can't categorize, try to keep printable ASCII
            if 32 <= ord(char) <= 126 or char in ['\t', '\n', '\r']:
                cleaned_chars.append(char)

    text = ''.join(cleaned_chars)

    # Remove unicode replacement characters that indicate encoding errors
    text = text.replace('\ufffd', '')  # Replacement character
    text = text.replace('\ufeff', '')  # Byte order mark (BOM)

    # Normalize line endings to Unix style
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Remove excessive whitespace while preserving intentional formatting
    # Don't collapse newlines, but do collapse spaces/tabs
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Collapse multiple spaces/tabs to single space
        line = re.sub(r'[ \t]+', ' ', line)
        # Strip leading/trailing whitespace from each line
        line = line.strip()
        cleaned_lines.append(line)

    # Join lines back together
    text = '\n'.join(cleaned_lines)

    # Remove excessive blank lines (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Final strip
    text = text.strip()

    return text
