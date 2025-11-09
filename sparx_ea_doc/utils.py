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
    """
    # Convert to lowercase and replace spaces with hyphens
    filename = name.lower().replace(' ', '-')

    # Remove or replace problematic characters
    filename = filename.replace('/', '-').replace('\\', '-')
    filename = filename.replace(':', '-').replace('*', '-')
    filename = filename.replace('?', '').replace('"', '')
    filename = filename.replace('<', '').replace('>', '')
    filename = filename.replace('|', '-')

    # Remove multiple consecutive hyphens
    while '--' in filename:
        filename = filename.replace('--', '-')

    # Remove leading/trailing hyphens
    filename = filename.strip('-')

    return filename
