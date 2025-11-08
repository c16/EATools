"""
Component documentation generator module.
"""

import logging
from pathlib import Path
from ..utils import generate_breadcrumbs
from ..template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class ComponentGenerator:
    """Generates component documentation"""

    def __init__(self, extractor, output_dir: Path, template_dir: Path = None):
        """
        Initialize the component generator

        Args:
            extractor: SparxExtractor instance with extracted data
            output_dir: Output directory for documentation
            template_dir: Directory containing templates (optional)
        """
        self.extractor = extractor
        self.output_dir = output_dir

        # Set up template renderer
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / 'templates'

        self.template_renderer = TemplateRenderer(template_dir)
        self.use_template = (template_dir / 'component_template.md').exists()

    def generate(self):
        """Generate component documentation"""
        logger.info("Generating component documentation...")

        comp_dir = self.output_dir / 'components'
        comp_dir.mkdir(exist_ok=True)

        index_file = comp_dir / 'index.md'
        comp_index_content = "# Components\n\n"
        comp_index_content += generate_breadcrumbs(index_file, self.output_dir, "Components")
        comp_index_content += "This document provides an overview of all components in the system.\n\n"
        comp_index_content += "## Component List\n\n"

        # Generate documentation for each component
        for comp in self.extractor.components:
            comp_filename = f"comp-{comp.name.lower().replace(' ', '-')}.md"
            comp_file = comp_dir / comp_filename
            comp_index_content += f"- [{comp.name}]({comp_filename})\n"

            comp_content = self._generate_single_component(comp, comp_file)

            with open(comp_file, 'w') as f:
                f.write(comp_content)

        # Generate interfaces catalog
        if self.extractor.interfaces:
            self._generate_interfaces_catalog(comp_dir)

        with open(index_file, 'w') as f:
            f.write(comp_index_content)

        logger.info(f"Generated documentation for {len(self.extractor.components)} components")

    def _generate_single_component(self, comp, comp_file: Path) -> str:
        """Generate documentation for a single component"""
        breadcrumbs = generate_breadcrumbs(comp_file, self.output_dir, comp.name)

        # Try to use template if available
        if self.use_template:
            try:
                # TODO: Implement full template rendering for components
                # For now, falls through to hard-coded generation
                pass
            except Exception as e:
                logger.warning(f"Template rendering failed for {comp.name}: {e}, using fallback")

        # Fallback to original hard-coded generation
        comp_content = f"# Component: {comp.name}\n\n"
        comp_content += breadcrumbs

        if comp.stereotype:
            comp_content += f"**Stereotype:** <<{comp.stereotype}>>\n\n"

        comp_content += f"**Package:** {comp.package_name}\n\n"
        comp_content += f"**Description:** {comp.clean_note() or 'No description available'}\n\n"

        # Get interfaces and dependencies
        connectors = self.extractor.get_connectors_for_element(comp.object_id)

        provided_interfaces = []
        required_interfaces = []
        dependencies = []
        used_by = []

        for conn in connectors:
            if conn.connector_type == 'Realisation' or conn.connector_type == 'Realization':
                if conn.source_id == comp.object_id:
                    target = self.extractor.elements.get(conn.target_id)
                    if target and target.object_type == 'Interface':
                        provided_interfaces.append(target.name)
            elif conn.connector_type == 'Dependency':
                if conn.source_id == comp.object_id:
                    target = self.extractor.elements.get(conn.target_id)
                    if target:
                        if target.object_type == 'Interface':
                            required_interfaces.append(target.name)
                        else:
                            dependencies.append(target.name)
                elif conn.target_id == comp.object_id:
                    source = self.extractor.elements.get(conn.source_id)
                    if source:
                        used_by.append(source.name)

        if provided_interfaces or required_interfaces:
            comp_content += "## Interfaces\n\n"

            if provided_interfaces:
                comp_content += "### Provided Interfaces\n\n"
                for iface in provided_interfaces:
                    comp_content += f"- {iface}\n"
                comp_content += "\n"

            if required_interfaces:
                comp_content += "### Required Interfaces\n\n"
                for iface in required_interfaces:
                    comp_content += f"- {iface}\n"
                comp_content += "\n"

        if dependencies or used_by:
            comp_content += "## Dependencies\n\n"

            if dependencies:
                comp_content += f"**Depends on:** {', '.join(dependencies)}\n\n"

            if used_by:
                comp_content += f"**Used by:** {', '.join(used_by)}\n\n"

        # Add attributes if any
        if comp.object_id in self.extractor.attributes:
            attrs = self.extractor.attributes[comp.object_id]
            comp_content += "## Attributes\n\n"
            comp_content += "| Name | Type | Visibility | Default | Static |\n"
            comp_content += "|------|------|------------|---------|--------|\n"

            for attr in attrs:
                static_flag = 'Yes' if attr.is_static else 'No'
                comp_content += f"| {attr.name} | {attr.attr_type} | {attr.scope} | {attr.default or '-'} | {static_flag} |\n"

            comp_content += "\n"

        # Add operations if any
        if comp.object_id in self.extractor.operations:
            ops = self.extractor.operations[comp.object_id]
            comp_content += "## Operations\n\n"
            comp_content += "| Name | Parameters | Return Type | Visibility |\n"
            comp_content += "|------|------------|-------------|------------|\n"

            for op in ops:
                params_str = ', '.join([f"{name}: {ptype}" for name, ptype in op.parameters]) or '-'
                comp_content += f"| {op.name} | {params_str} | {op.return_type} | {op.scope} |\n"

            comp_content += "\n"

        return comp_content

    def _generate_interfaces_catalog(self, comp_dir: Path):
        """Generate interfaces catalog"""
        interfaces_file = comp_dir / 'interfaces.md'

        interfaces_content = "# Interfaces\n\n"
        interfaces_content += generate_breadcrumbs(interfaces_file, self.output_dir, "Interfaces")
        interfaces_content += "This document lists all interfaces in the system.\n\n"

        for iface in self.extractor.interfaces:
            interfaces_content += f"## {iface.name}\n\n"

            if iface.stereotype:
                interfaces_content += f"**Stereotype:** <<{iface.stereotype}>>\n\n"

            interfaces_content += f"**Package:** {iface.package_name}\n\n"
            interfaces_content += f"**Description:** {iface.clean_note() or 'No description available'}\n\n"

            # Add operations
            if iface.object_id in self.extractor.operations:
                ops = self.extractor.operations[iface.object_id]
                interfaces_content += "### Methods\n\n"
                interfaces_content += "| Name | Parameters | Return Type |\n"
                interfaces_content += "|------|------------|-------------|\n"

                for op in ops:
                    params_str = ', '.join([f"{name}: {ptype}" for name, ptype in op.parameters]) or '-'
                    interfaces_content += f"| {op.name} | {params_str} | {op.return_type} |\n"

                interfaces_content += "\n"

            interfaces_content += "---\n\n"

        with open(comp_dir / 'interfaces.md', 'w') as f:
            f.write(interfaces_content)
