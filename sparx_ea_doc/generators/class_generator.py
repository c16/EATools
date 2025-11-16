"""
Class and module documentation generator module.
"""

import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
from ..utils import generate_breadcrumbs, generate_filename_with_id, sanitize_filename
from ..template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class ClassGenerator:
    """Generates class and module documentation"""

    def __init__(self, extractor, output_dir: Path, template_dir: Path = None, diagram_guid_to_png: Dict[str, str] = None):
        """
        Initialize the class generator

        Args:
            extractor: SparxExtractor instance with extracted data
            output_dir: Output directory for documentation
            template_dir: Directory containing templates (optional)
            diagram_guid_to_png: Mapping of diagram GUIDs to PNG file paths
        """
        self.extractor = extractor
        self.output_dir = output_dir
        self.diagram_guid_to_png = diagram_guid_to_png or {}

        # Set up template renderer
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / 'templates'

        self.template_renderer = TemplateRenderer(template_dir)
        self.use_template = (template_dir / 'class_template.md').exists()

    def _get_package_diagrams(self, package_names: List[str]) -> List[tuple]:
        """
        Get diagrams for given package names

        Args:
            package_names: List of package names to find diagrams for

        Returns:
            List of (diagram_guid, diagram_name) tuples
        """
        diagrams = []
        cursor = self.extractor.conn.cursor()

        # Query diagrams by package name
        placeholders = ','.join('?' * len(package_names))
        query = f"""
            SELECT d.ea_guid, d.Name
            FROM t_diagram d
            JOIN t_package p ON d.Package_ID = p.Package_ID
            WHERE p.Name IN ({placeholders})
            ORDER BY d.Name
        """
        cursor.execute(query, package_names)

        for row in cursor.fetchall():
            diagrams.append((row[0], row[1]))

        return diagrams

    def _get_class_diagrams(self, object_id: int) -> List[tuple]:
        """
        Get diagrams that contain a specific class

        Args:
            object_id: The object ID of the class

        Returns:
            List of (diagram_guid, diagram_name) tuples
        """
        diagrams = []
        cursor = self.extractor.conn.cursor()

        # Query diagrams where this object appears
        cursor.execute("""
            SELECT DISTINCT d.ea_guid, d.Name
            FROM t_diagram d
            JOIN t_diagramobjects do ON d.Diagram_ID = do.Diagram_ID
            WHERE do.Object_ID = ?
            ORDER BY d.Name
        """, (object_id,))

        for row in cursor.fetchall():
            diagrams.append((row[0], row[1]))

        return diagrams

    def generate(self):
        """Generate class and module documentation"""
        logger.info("Generating class documentation...")

        class_dir = self.output_dir / 'classes'
        class_dir.mkdir(exist_ok=True)

        # Group classes by package
        classes_by_package = defaultdict(list)
        for cls in self.extractor.classes:
            classes_by_package[cls.package_name].append(cls)

        index_file = class_dir / 'index.md'
        class_index_content = "# Classes and Modules\n\n"
        class_index_content += generate_breadcrumbs(index_file, self.output_dir, "Classes")
        class_index_content += "This document provides an overview of all classes in the system.\n\n"
        class_index_content += "## Packages\n\n"

        # Generate documentation for each package
        for package_name, classes in sorted(classes_by_package.items()):
            package_dir_name = sanitize_filename(package_name)
            package_dir = class_dir / package_dir_name
            package_dir.mkdir(exist_ok=True)

            class_index_content += f"### {package_name}\n\n"

            # Create package index
            package_index_file = package_dir / 'index.md'
            package_index_content = f"# {package_name} Package\n\n"
            package_index_content += generate_breadcrumbs(package_index_file, self.output_dir, package_name)
            package_index_content += f"Classes in the {package_name} package.\n\n"

            # Add package-level diagrams
            package_diagrams = self._get_package_diagrams([package_name])
            if package_diagrams:
                package_index_content += "## Diagrams\n\n"
                for diagram_guid, diagram_name in package_diagrams:
                    if diagram_guid in self.diagram_guid_to_png:
                        png_path = self.diagram_guid_to_png[diagram_guid]
                        png_path = f"../../{png_path}"  # Relative from classes/package/
                        package_index_content += f"### {diagram_name}\n\n"
                        package_index_content += f"![{diagram_name}]({png_path})\n\n"
                package_index_content += "\n"

            package_index_content += "## Classes\n\n"

            for cls in sorted(classes, key=lambda x: x.name):
                class_filename = generate_filename_with_id(cls.name, cls.object_id)
                class_file = package_dir / class_filename
                class_index_content += f"- [{cls.name}]({package_dir_name}/{class_filename})\n"
                package_index_content += f"- [{cls.name}]({class_filename})\n"

                class_content = self._generate_single_class(cls, class_file)

                with open(class_file, 'w') as f:
                    f.write(class_content)

            # Write package index
            with open(package_index_file, 'w') as f:
                f.write(package_index_content)

            class_index_content += "\n"

        # Generate enumerations documentation
        if self.extractor.enumerations:
            class_index_content += self._generate_enumerations_section()

        with open(index_file, 'w') as f:
            f.write(class_index_content)

        logger.info(f"Generated documentation for {len(self.extractor.classes)} classes")

    def _generate_single_class(self, cls, class_file: Path) -> str:
        """Generate documentation for a single class"""
        breadcrumbs = generate_breadcrumbs(class_file, self.output_dir, cls.name)

        # Try to use template if available
        if self.use_template:
            try:
                # TODO: Implement full template rendering for classes
                # For now, falls through to hard-coded generation
                pass
            except Exception as e:
                logger.warning(f"Template rendering failed for {cls.name}: {e}, using fallback")

        # Fallback to original hard-coded generation
        class_content = f"# Class: {cls.name}\n\n"
        class_content += breadcrumbs

        if cls.stereotype:
            class_content += f"**Stereotype:** <<{cls.stereotype}>>\n\n"

        class_content += f"**Package:** {cls.package_name}\n\n"

        # Add metadata line (version, modified date, guid)
        metadata_parts = []
        if cls.version:
            metadata_parts.append(f"Version: {cls.version}")
        if cls.modified_date:
            metadata_parts.append(f"Modified: {cls.modified_date}")
        if cls.guid:
            metadata_parts.append(f"GUID: {cls.guid}")

        if metadata_parts:
            class_content += f"**{' | '.join(metadata_parts)}**\n\n"

        class_content += f"**Description:** {cls.clean_note() or 'No description available'}\n\n"

        # Add diagrams where this class appears
        class_diagrams = self._get_class_diagrams(cls.object_id)
        if class_diagrams:
            class_content += "## Diagrams\n\n"
            for diagram_guid, diagram_name in class_diagrams:
                if diagram_guid in self.diagram_guid_to_png:
                    png_path = self.diagram_guid_to_png[diagram_guid]
                    # Relative path from classes/package/class.md to diagrams/
                    png_path = f"../../{png_path}"
                    class_content += f"### {diagram_name}\n\n"
                    class_content += f"![{diagram_name}]({png_path})\n\n"
            class_content += "\n"

        # Get inheritance and relationships
        connectors = self.extractor.get_connectors_for_element(cls.object_id)

        inherits_from = []
        implements = []
        associations = []
        dependencies = []

        for conn in connectors:
            if conn.connector_type == 'Generalization':
                if conn.source_id == cls.object_id:
                    target = self.extractor.elements.get(conn.target_id)
                    if target:
                        inherits_from.append(target.name)
            elif conn.connector_type == 'Realisation' or conn.connector_type == 'Realization':
                if conn.source_id == cls.object_id:
                    target = self.extractor.elements.get(conn.target_id)
                    if target and target.object_type == 'Interface':
                        implements.append(target.name)
            elif conn.connector_type in ['Association', 'Aggregation', 'Composition']:
                if conn.source_id == cls.object_id:
                    target = self.extractor.elements.get(conn.target_id)
                    if target:
                        card = f" ({conn.target_card})" if conn.target_card else ""
                        role = f" - {conn.target_role}" if conn.target_role else ""
                        associations.append(f"{target.name}{card}{role} [{conn.connector_type}]")
                elif conn.target_id == cls.object_id:
                    source = self.extractor.elements.get(conn.source_id)
                    if source:
                        card = f" ({conn.source_card})" if conn.source_card else ""
                        role = f" - {conn.source_role}" if conn.source_role else ""
                        associations.append(f"{source.name}{card}{role} [{conn.connector_type}]")
            elif conn.connector_type == 'Dependency':
                if conn.source_id == cls.object_id:
                    target = self.extractor.elements.get(conn.target_id)
                    if target:
                        dependencies.append(target.name)

        # Operations section (public only) - show methods first
        if cls.object_id in self.extractor.operations:
            ops = [op for op in self.extractor.operations[cls.object_id] if op.scope.lower() == 'public']
            if ops:
                class_content += "## Methods\n\n"
                class_content += "| Name | Parameters | Return Type | Description |\n"
                class_content += "|------|------------|-------------|-------------|\n"

                for op in ops:
                    params_str = ', '.join([f"{name}: {ptype}" for name, ptype in op.parameters]) or '-'
                    desc = op.notes or '-'
                    class_content += f"| {op.name} | {params_str} | {op.return_type} | {desc} |\n"

                class_content += "\n"

        # Attributes section (public only) - show attributes after methods
        if cls.object_id in self.extractor.attributes:
            attrs = [attr for attr in self.extractor.attributes[cls.object_id] if attr.scope.lower() == 'public']
            if attrs:
                class_content += "## Attributes\n\n"
                class_content += "| Name | Type | Default | Const | Description |\n"
                class_content += "|------|------|---------|-------|-------------|\n"

                for attr in attrs:
                    const_flag = 'Yes' if attr.is_const else 'No'
                    desc = attr.notes or '-'
                    class_content += f"| {attr.name} | {attr.attr_type} | {attr.default or '-'} | {const_flag} | {desc} |\n"

                class_content += "\n"

        # Relationships section
        if inherits_from or implements or associations or dependencies:
            class_content += "## Relationships\n\n"

            if inherits_from:
                class_content += f"**Inherits from:** {', '.join(inherits_from)}\n\n"

            if implements:
                class_content += f"**Implements:** {', '.join(implements)}\n\n"

            if associations:
                class_content += "**Associations:**\n\n"
                for assoc in associations:
                    class_content += f"- {assoc}\n"
                class_content += "\n"

            if dependencies:
                class_content += f"**Dependencies:** {', '.join(dependencies)}\n\n"

        return class_content

    def _generate_enumerations_section(self) -> str:
        """Generate enumerations section for the index"""
        content = "## Enumerations\n\n"

        for enum in self.extractor.enumerations:
            content += f"### {enum.name}\n\n"
            content += f"**Package:** {enum.package_name}\n\n"
            content += f"**Description:** {enum.clean_note() or 'No description available'}\n\n"

            if enum.object_id in self.extractor.attributes:
                attrs = self.extractor.attributes[enum.object_id]
                content += "**Values:**\n\n"
                for attr in attrs:
                    default = f" = {attr.default}" if attr.default else ""
                    content += f"- {attr.name}{default}\n"
                content += "\n"

        return content
