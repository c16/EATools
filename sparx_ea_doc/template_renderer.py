"""
Template rendering module for documentation generation.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders documentation templates with data"""

    def __init__(self, template_dir: Path):
        """
        Initialize the template renderer

        Args:
            template_dir: Directory containing template files
        """
        self.template_dir = template_dir

    def load_template(self, template_name: str) -> str:
        """
        Load a template file

        Args:
            template_name: Name of the template file (e.g., 'use_case_template.md')

        Returns:
            Template content as string
        """
        template_path = self.template_dir / template_name
        if not template_path.exists():
            logger.warning(f"Template not found: {template_path}, using fallback")
            return ""

        with open(template_path, 'r') as f:
            return f.read()

    def render(self, template_content: str, data: Dict[str, Any]) -> str:
        """
        Render a template with the provided data

        Args:
            template_content: Template string with placeholders
            data: Dictionary of data to fill into template

        Returns:
            Rendered content
        """
        if not template_content:
            return ""

        content = template_content

        # Process conditional sections (if_xxx)
        content = self._process_conditionals(content, data)

        # Process repeating sections (for_each_xxx)
        content = self._process_loops(content, data)

        # Replace simple placeholders
        content = self._replace_placeholders(content, data)

        return content

    def _process_conditionals(self, content: str, data: Dict[str, Any]) -> str:
        """
        Process conditional sections <if_xxx>...</if_xxx>

        Args:
            content: Template content
            data: Data dictionary

        Returns:
            Content with conditionals processed
        """
        # Pattern to match <if_xxx>...</if_xxx>
        pattern = r'<if_([^>]+)>(.*?)</if_\1>'

        def replace_conditional(match):
            condition_key = match.group(1)  # e.g., "actors"
            section_content = match.group(2)

            # Build the full condition name with "if_" prefix
            condition_name = f"if_{condition_key}"

            # Check if the condition is met
            if condition_name in data and data[condition_name]:
                logger.debug(f"Conditional if_{condition_key} is TRUE, including content")
                return section_content
            logger.debug(f"Conditional if_{condition_key} is FALSE or missing, excluding content")
            return ""

        # Use re.DOTALL to match across newlines
        return re.sub(pattern, replace_conditional, content, flags=re.DOTALL)

    def _process_loops(self, content: str, data: Dict[str, Any]) -> str:
        """
        Process repeating sections <for_each_xxx>...</for_each_xxx>

        Args:
            content: Template content
            data: Data dictionary with lists

        Returns:
            Content with loops processed
        """
        # Pattern to match <for_each_xxx>...</for_each_xxx>
        pattern = r'<for_each_([^>]+)>(.*?)</for_each_\1>'

        def replace_loop(match):
            loop_name = match.group(1)
            section_content = match.group(2)

            # Get the list data
            list_key = f"{loop_name}_list"
            if list_key not in data or not isinstance(data[list_key], list):
                return ""

            # Render section for each item
            result = []
            for item in data[list_key]:
                # Replace placeholders in this section with item data
                item_content = self._replace_placeholders(section_content, item)
                result.append(item_content)

            return ''.join(result)

        return re.sub(pattern, replace_loop, content, flags=re.DOTALL)

    def _replace_placeholders(self, content: str, data: Dict[str, Any]) -> str:
        """
        Replace simple placeholders <placeholder_name> with values

        Args:
            content: Content with placeholders
            data: Data dictionary

        Returns:
            Content with placeholders replaced
        """
        # Pattern to match <placeholder>
        pattern = r'<([^>]+)>'

        def replace_placeholder(match):
            key = match.group(1)

            # Skip if it's a conditional or loop marker
            if key.startswith('if_') or key.startswith('for_each_') or key.startswith('/'):
                return match.group(0)

            # Return value if exists, otherwise keep placeholder
            if key in data:
                value = data[key]
                # Convert None to empty string
                if value is None:
                    return ""
                # Convert lists to comma-separated string
                if isinstance(value, list):
                    return ', '.join(str(v) for v in value)
                return str(value)

            # Keep placeholder if no data found
            return match.group(0)

        return re.sub(pattern, replace_placeholder, content)
