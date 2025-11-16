"""
Requirement documentation generator module.
"""

import logging
from pathlib import Path
from typing import Dict, List
from ..utils import generate_breadcrumbs, sanitize_filename, generate_filename_with_id
from ..template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class RequirementGenerator:
    """Generates requirement documentation"""

    def __init__(self, extractor, output_dir: Path, template_dir: Path = None):
        """
        Initialize the requirement generator

        Args:
            extractor: SparxExtractor instance with extracted data
            output_dir: Output directory for documentation
            template_dir: Directory containing templates (optional)
        """
        self.extractor = extractor
        self.output_dir = output_dir

        # Set up template renderer
        if template_dir is None:
            # Default to templates/ directory in project root
            template_dir = Path(__file__).parent.parent.parent / 'templates'

        self.template_renderer = TemplateRenderer(template_dir)
        self.use_template = (template_dir / 'requirement_template.md').exists()

    def generate(self):
        """Generate requirement documentation"""
        logger.info("Generating requirement documentation...")

        req_dir = self.output_dir / 'requirements'
        req_dir.mkdir(exist_ok=True)

        # Generate individual requirement documents
        self._generate_requirement_docs(req_dir)

        logger.info(f"Generated documentation for {len(self.extractor.requirements)} requirements")

    def _generate_requirement_docs(self, req_dir: Path):
        """Generate individual requirement documents"""
        index_file = req_dir / 'index.md'

        # Group requirements by stereotype
        by_stereotype = {}
        for req in self.extractor.requirements:
            stereotype = req.stereotype or 'General'
            if stereotype not in by_stereotype:
                by_stereotype[stereotype] = []
            by_stereotype[stereotype].append(req)

        req_index_content = "# Requirements\n\n"
        req_index_content += generate_breadcrumbs(index_file, self.output_dir, "Requirements")
        req_index_content += "This document provides an overview of all requirements in the system.\n\n"

        # Create table of contents by stereotype
        for stereotype in sorted(by_stereotype.keys()):
            req_index_content += f"## {stereotype}\n\n"
            for req in sorted(by_stereotype[stereotype], key=lambda r: r.name):
                req_filename = generate_filename_with_id(req.name, req.object_id)
                # Create display name in "Alias - Name" format
                if req.alias:
                    display_name = f"{req.alias} - {req.name}"
                else:
                    display_name = req.name
                req_index_content += f"- [{display_name}]({req_filename})"
                if req.priority:
                    req_index_content += f" - **{req.priority}**"
                req_index_content += "\n"
            req_index_content += "\n"

        # Generate individual requirement files
        for req in self.extractor.requirements:
            req_filename = generate_filename_with_id(req.name, req.object_id)
            req_file = req_dir / req_filename

            # Generate individual requirement file
            req_content = self._generate_single_requirement(req, req_file)

            with open(req_file, 'w') as f:
                f.write(req_content)

        # Write index
        with open(index_file, 'w') as f:
            f.write(req_index_content)

    def _generate_single_requirement(self, req, req_file: Path) -> str:
        """
        Generate documentation for a single requirement

        Args:
            req: Requirement object
            req_file: Output file path

        Returns:
            Generated content
        """
        # Create display name in "Alias - Name" format for breadcrumbs
        if req.alias:
            display_name = f"{req.alias} - {req.name}"
        else:
            display_name = req.name
        breadcrumbs = generate_breadcrumbs(req_file, self.output_dir, display_name)

        # Try template-based generation first if template exists
        if self.use_template:
            try:
                return self._generate_with_template(req, breadcrumbs)
            except Exception as e:
                logger.warning(f"Template rendering failed for {req.name}: {e}. Falling back to hard-coded generation.")

        # Fallback to hard-coded generation
        return self._generate_hardcoded(req, breadcrumbs)

    def _generate_with_template(self, req, breadcrumbs: str) -> str:
        """
        Generate requirement documentation using template

        Args:
            req: Requirement object
            breadcrumbs: Pre-generated breadcrumb navigation

        Returns:
            Rendered documentation
        """
        # Load template
        template = self.template_renderer.load_template('requirement_template.md')

        # Build data dictionary
        # Create display name in "Alias - Name" format
        if req.alias:
            display_name = f"{req.alias} - {req.name}"
        else:
            display_name = req.name

        data = {
            'requirement_name': req.name,
            'requirement_display_name': display_name,
            'package_name': req.package_name,
            'description': req.clean_note() or 'No description available',
        }

        # Add stereotype if exists
        if req.stereotype:
            data['if_stereotype'] = True
            data['stereotype'] = f"<<{req.stereotype}>>"
        else:
            data['if_stereotype'] = False

        # Add metadata
        metadata_parts = []
        if req.version:
            metadata_parts.append(f"Version: {req.version}")
        if req.modified_date:
            metadata_parts.append(f"Modified: {req.modified_date}")
        if req.guid:
            metadata_parts.append(f"GUID: {req.guid}")

        if metadata_parts:
            data['metadata_parts'] = ' | '.join(metadata_parts)
        else:
            data['metadata_parts'] = ''

        # Add priority
        if req.priority:
            data['if_priority'] = True
            data['priority'] = req.priority
        else:
            data['if_priority'] = False

        # Add difficulty
        if req.difficulty:
            data['if_difficulty'] = True
            data['difficulty'] = req.difficulty
        else:
            data['if_difficulty'] = False

        # Add status
        if req.status:
            data['if_status'] = True
            data['status'] = req.status
        else:
            data['if_status'] = False

        # Add related use cases
        if req.related_use_cases:
            data['if_related_use_cases'] = True
            uc_list = []
            for uc_name in sorted(req.related_use_cases):
                # Look up the use case object to get its object_id
                uc_obj = next((uc for uc in self.extractor.use_cases if uc.name == uc_name), None)
                if uc_obj:
                    uc_filename = generate_filename_with_id(uc_name, uc_obj.object_id)
                    uc_list.append(f"- [{uc_name}](../use-cases/{uc_filename})")
                else:
                    # Fallback if use case not found
                    uc_filename = sanitize_filename(uc_name)
                    uc_list.append(f"- [{uc_name}](../use-cases/{uc_filename}.md)")
            data['related_use_case'] = '\n'.join(uc_list)
        else:
            data['if_related_use_cases'] = False

        # Render template
        content = self.template_renderer.render(template, data)

        # Prepend breadcrumbs
        return f"{breadcrumbs}\n\n{content}"

    def _generate_hardcoded(self, req, breadcrumbs: str) -> str:
        """
        Generate requirement documentation using hard-coded format (fallback)

        Args:
            req: Requirement object
            breadcrumbs: Pre-generated breadcrumb navigation

        Returns:
            Generated content
        """
        # Create display name in "Alias - Name" format
        if req.alias:
            display_name = f"{req.alias} - {req.name}"
        else:
            display_name = req.name

        content = f"# {display_name}\n\n"
        content += breadcrumbs
        content += "\n\n"

        if req.stereotype:
            content += f"**Stereotype:** <<{req.stereotype}>>\n\n"

        content += f"**Package:** {req.package_name}\n\n"

        # Add metadata
        metadata_parts = []
        if req.version:
            metadata_parts.append(f"Version: {req.version}")
        if req.modified_date:
            metadata_parts.append(f"Modified: {req.modified_date}")
        if req.guid:
            metadata_parts.append(f"GUID: {req.guid}")

        if metadata_parts:
            content += f"**{' | '.join(metadata_parts)}**\n\n"

        content += f"**Description:** {req.clean_note() or 'No description available'}\n\n"

        if req.priority:
            content += f"**Priority:** {req.priority}\n\n"

        if req.difficulty:
            content += f"**Difficulty:** {req.difficulty}\n\n"

        if req.status:
            content += f"**Status:** {req.status}\n\n"

        # Add related use cases
        if req.related_use_cases:
            content += "**Related Use Cases:**\n\n"
            for uc_name in sorted(req.related_use_cases):
                # Look up the use case object to get its object_id
                uc_obj = next((uc for uc in self.extractor.use_cases if uc.name == uc_name), None)
                if uc_obj:
                    uc_filename = generate_filename_with_id(uc_name, uc_obj.object_id)
                    content += f"- [{uc_name}](../use-cases/{uc_filename})\n"
                else:
                    # Fallback if use case not found
                    uc_filename = sanitize_filename(uc_name)
                    content += f"- [{uc_name}](../use-cases/{uc_filename}.md)\n"
            content += "\n"

        return content
