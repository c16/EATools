"""
Utility functions for documentation generation
"""

from pathlib import Path
from typing import List, Tuple


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
