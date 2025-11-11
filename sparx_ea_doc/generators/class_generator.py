"""
Class and module documentation generator module.
"""

import logging
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class ClassGenerator:
    """Generates class and module documentation"""

    def __init__(self, extractor, output_dir: Path):
        """
        Initialize the class generator

        Args:
            extractor: SparxExtractor instance with extracted data
            output_dir: Output directory for documentation
        """
        self.extractor = extractor
        self.output_dir = output_dir
        self.should_generate = None  # Optional filter function for selective generation

    def generate(self):
        """Generate class and module documentation"""
        logger.info("Generating class documentation...")

        class_dir = self.output_dir / 'classes'
        class_dir.mkdir(exist_ok=True)

        # Group classes by package
        classes_by_package = defaultdict(list)
        for cls in self.extractor.classes:
            classes_by_package[cls.package_name].append(cls)

        class_index_content = "# Classes and Modules\n\n"
        class_index_content += "This document provides an overview of all classes in the system.\n\n"
        class_index_content += "## Packages\n\n"

        # Generate documentation for each package
        for package_name, classes in sorted(classes_by_package.items()):
            package_dir = class_dir / package_name.lower().replace(' ', '-')
            package_dir.mkdir(exist_ok=True)

            class_index_content += f"### {package_name}\n\n"

            for cls in sorted(classes, key=lambda x: x.name):
                class_filename = f"{cls.name.lower().replace(' ', '-')}.md"
                safe_package = package_name.lower().replace(' ', '-')
                class_filepath = f"classes/{safe_package}/{class_filename}"
                class_index_content += f"- [{cls.name}]({safe_package}/{class_filename})\n"

                # Generate individual class file if selected
                if not self.should_generate or self.should_generate(class_filepath):
                    class_content = self._generate_single_class(cls)

                    with open(package_dir / class_filename, 'w') as f:
                        f.write(class_content)

            class_index_content += "\n"

        # Generate enumerations documentation
        if self.extractor.enumerations:
            class_index_content += self._generate_enumerations_section()

        # Write index if selected
        if not self.should_generate or self.should_generate('classes/index.md'):
            with open(class_dir / 'index.md', 'w') as f:
                f.write(class_index_content)

        logger.info(f"Generated documentation for {len(self.extractor.classes)} classes")

    def _generate_single_class(self, cls) -> str:
        """Generate documentation for a single class"""
        class_content = f"# Class: {cls.name}\n\n"

        if cls.stereotype:
            class_content += f"**Stereotype:** <<{cls.stereotype}>>\n\n"

        class_content += f"**Package:** {cls.package_name}\n\n"
        class_content += f"**Visibility:** {cls.visibility}\n\n"
        class_content += f"**Description:** {cls.clean_note() or 'No description available'}\n\n"

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

        # Attributes section
        if cls.object_id in self.extractor.attributes:
            attrs = self.extractor.attributes[cls.object_id]
            class_content += "## Attributes\n\n"
            class_content += "| Name | Type | Visibility | Default | Static | Const | Description |\n"
            class_content += "|------|------|------------|---------|--------|-------|-------------|\n"

            for attr in attrs:
                static_flag = 'Yes' if attr.is_static else 'No'
                const_flag = 'Yes' if attr.is_const else 'No'
                desc = attr.notes or '-'
                class_content += f"| {attr.name} | {attr.attr_type} | {attr.scope} | {attr.default or '-'} | {static_flag} | {const_flag} | {desc} |\n"

            class_content += "\n"

        # Operations section
        if cls.object_id in self.extractor.operations:
            ops = self.extractor.operations[cls.object_id]
            class_content += "## Methods\n\n"
            class_content += "| Name | Parameters | Return Type | Visibility | Abstract | Static | Description |\n"
            class_content += "|------|------------|-------------|------------|----------|--------|-------------|\n"

            for op in ops:
                params_str = ', '.join([f"{name}: {ptype}" for name, ptype in op.parameters]) or '-'
                abstract_flag = 'Yes' if op.is_abstract else 'No'
                static_flag = 'Yes' if op.is_static else 'No'
                desc = op.notes or '-'
                class_content += f"| {op.name} | {params_str} | {op.return_type} | {op.scope} | {abstract_flag} | {static_flag} | {desc} |\n"

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
