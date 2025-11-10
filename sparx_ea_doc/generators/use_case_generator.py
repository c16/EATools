"""
Use case documentation generator module.
"""

import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
from ..utils import generate_breadcrumbs
from ..template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class UseCaseGenerator:
    """Generates use case documentation"""

    def __init__(self, extractor, output_dir: Path, template_dir: Path = None, diagram_guid_to_png: Dict[str, str] = None):
        """
        Initialize the use case generator

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
            # Default to templates/ directory in project root
            template_dir = Path(__file__).parent.parent.parent / 'templates'

        self.template_renderer = TemplateRenderer(template_dir)
        self.use_template = (template_dir / 'use_case_template.md').exists()

    def generate(self):
        """Generate use case documentation"""
        logger.info("Generating use case documentation...")

        uc_dir = self.output_dir / 'use-cases'
        uc_dir.mkdir(exist_ok=True)

        # Generate actors documentation
        self._generate_actors_doc(uc_dir)

        # Generate individual use case documents
        self._generate_use_case_docs(uc_dir)

        logger.info(f"Generated documentation for {len(self.extractor.use_cases)} use cases")

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

    def _generate_actors_doc(self, uc_dir: Path):
        """Generate actors documentation"""
        actors_file = uc_dir / 'actors.md'

        actors_content = "# Actors\n\n"
        actors_content += generate_breadcrumbs(actors_file, self.output_dir, "Actors")
        actors_content += "This document lists all actors in the system.\n\n"

        for actor in self.extractor.actors:
            actors_content += f"## {actor.name}\n\n"
            if actor.stereotype:
                actors_content += f"**Stereotype:** <<{actor.stereotype}>>\n\n"
            actors_content += f"**Description:** {actor.clean_note() or 'No description available'}\n\n"
            actors_content += "---\n\n"

        with open(uc_dir / 'actors.md', 'w') as f:
            f.write(actors_content)

    def _generate_use_case_docs(self, uc_dir: Path):
        """Generate individual use case documents"""
        index_file = uc_dir / 'index.md'

        uc_index_content = "# Use Cases\n\n"
        uc_index_content += generate_breadcrumbs(index_file, self.output_dir, "Use Cases")
        uc_index_content += "This document provides an overview of all use cases in the system.\n\n"

        # Add package-level diagrams
        package_diagrams = self._get_package_diagrams(['UseCases', 'Requirements'])
        if package_diagrams:
            uc_index_content += "## Diagrams\n\n"
            for diagram_guid, diagram_name in package_diagrams:
                if diagram_guid in self.diagram_guid_to_png:
                    png_path = self.diagram_guid_to_png[diagram_guid]
                    png_path = f"../{png_path}"
                    uc_index_content += f"### {diagram_name}\n\n"
                    uc_index_content += f"![{diagram_name}]({png_path})\n\n"
            uc_index_content += "\n"

        uc_index_content += "## Use Case List\n\n"

        for uc in self.extractor.use_cases:
            uc_filename = f"{uc.name.lower().replace(' ', '-')}.md"
            uc_file = uc_dir / uc_filename

            # Add to index
            uc_index_content += f"- [{uc.name}]({uc_filename})\n"

            # Generate individual use case file
            uc_content = self._generate_single_use_case(uc, uc_file)

            with open(uc_file, 'w') as f:
                f.write(uc_content)

        # Write index
        with open(index_file, 'w') as f:
            f.write(uc_index_content)

    def _generate_with_template(self, uc, breadcrumbs: str) -> str:
        """
        Generate use case documentation using template

        Args:
            uc: UseCase object
            breadcrumbs: Pre-generated breadcrumb navigation

        Returns:
            Rendered documentation
        """
        # Load template
        template = self.template_renderer.load_template('use_case_template.md')

        # Build data dictionary
        data = {
            'use_case_name': uc.name,
            'package_name': uc.package_name,
            'description': uc.clean_note() or 'No description available',
        }

        # Add stereotype if exists
        if uc.stereotype:
            data['if_stereotype'] = True
            data['stereotype'] = uc.stereotype
        else:
            data['if_stereotype'] = False

        # Add metadata
        metadata_parts = []
        if uc.version:
            metadata_parts.append(f"Version: {uc.version}")
        if uc.modified_date:
            metadata_parts.append(f"Modified: {uc.modified_date}")
        if uc.guid:
            metadata_parts.append(f"GUID: {uc.guid}")

        if metadata_parts:
            data['metadata_parts'] = ' | '.join(metadata_parts)
        else:
            data['metadata_parts'] = ''

        # Get related actors and use cases
        connectors = self.extractor.get_connectors_for_element(uc.object_id)

        actors_set = set()
        includes_set = set()
        extends_set = set()
        associations_set = set()

        for conn in connectors:
            if conn.source_id == uc.object_id:
                target = self.extractor.elements.get(conn.target_id)
                if target:
                    if target.object_type == 'Actor':
                        actors_set.add(target.name)
                    elif target.object_type == 'UseCase':
                        if 'include' in conn.connector_type.lower():
                            includes_set.add(target.name)
                        elif 'extend' in conn.connector_type.lower():
                            extends_set.add(target.name)
                        else:
                            associations_set.add(target.name)
            elif conn.target_id == uc.object_id:
                source = self.extractor.elements.get(conn.source_id)
                if source:
                    if source.object_type == 'Actor':
                        actors_set.add(source.name)
                    elif source.object_type == 'UseCase':
                        if 'extend' in conn.connector_type.lower():
                            extends_set.add(source.name)

        # Add actors
        if actors_set:
            data['if_actors'] = True
            data['actors_list'] = ', '.join(sorted(actors_set))
        else:
            data['if_actors'] = False

        # Add includes
        if includes_set:
            data['if_includes'] = True
            includes_content = ""
            for inc in sorted(includes_set):
                includes_content += f"- <<include>> {inc}\n"
            data['included_use_case'] = includes_content
        else:
            data['if_includes'] = False

        # Add extends
        if extends_set:
            data['if_extends'] = True
            extends_content = ""
            for ext in sorted(extends_set):
                extends_content += f"- <<extend>> {ext}\n"
            data['extending_use_case'] = extends_content
        else:
            data['if_extends'] = False

        # Add related
        if associations_set:
            data['if_related'] = True
            related_content = ""
            for assoc in sorted(associations_set):
                related_content += f"- {assoc}\n"
            data['related_use_case'] = related_content
        else:
            data['if_related'] = False

        # Add related requirements
        requirements_set = set()
        for conn in connectors:
            if conn.source_id == uc.object_id:
                target = self.extractor.elements.get(conn.target_id)
                if target and target.object_type == 'Requirement':
                    requirements_set.add(target.name)
            elif conn.target_id == uc.object_id:
                source = self.extractor.elements.get(conn.source_id)
                if source and source.object_type == 'Requirement':
                    requirements_set.add(source.name)

        if requirements_set:
            data['if_requirements'] = True
            req_content = ""
            from ..utils import sanitize_filename
            for req_name in sorted(requirements_set):
                req_filename = sanitize_filename(req_name)
                req_content += f"- [{req_name}](../requirements/{req_filename}.md)\n"
            data['requirement_list'] = req_content
        else:
            data['if_requirements'] = False

        # Add diagrams
        diagrams = self.extractor.get_diagrams_for_element(uc.object_id)
        if diagrams:
            data['if_diagrams'] = True
            diagram_content = ""
            for diagram_guid in diagrams:
                # Check if PNG rendering is available
                if diagram_guid in self.diagram_guid_to_png:
                    png_path = self.diagram_guid_to_png[diagram_guid]
                    # Fix path to be relative from use-cases/ subdirectory
                    png_path = f"../{png_path}"
                    diagram_content += f"![Diagram {diagram_guid}]({png_path})\n\n"
                else:
                    # Fallback to text placeholder
                    diagram_content += f"- diagram {diagram_guid}\n"
            data['diagram_list'] = diagram_content
        else:
            data['if_diagrams'] = False

        # Add preconditions and postconditions from constraints
        if uc.object_id in self.extractor.constraints:
            preconditions = [c for c in self.extractor.constraints[uc.object_id] if c.constraint_type == 'Pre-condition']
            postconditions = [c for c in self.extractor.constraints[uc.object_id] if c.constraint_type == 'Post-condition']

            if preconditions:
                data['if_preconditions'] = True
                precond_content = ""
                for pc in preconditions:
                    precond_content += f"**{pc.name}**\n\n"
                    if pc.notes:
                        precond_content += f"{pc.notes}\n\n"
                data['precondition_name'] = preconditions[0].name if preconditions else ""
                data['precondition_description'] = precond_content
            else:
                data['if_preconditions'] = False

            if postconditions:
                data['if_postconditions'] = True
                postcond_content = ""
                for pc in postconditions:
                    postcond_content += f"**{pc.name}**\n\n"
                    if pc.notes:
                        postcond_content += f"{pc.notes}\n\n"
                data['postcondition_name'] = postconditions[0].name if postconditions else ""
                data['postcondition_description'] = postcond_content
            else:
                data['if_postconditions'] = False
        else:
            data['if_preconditions'] = False
            data['if_postconditions'] = False

        # Parse structured notes
        sections = uc.parse_structured_note()

        # Add structured sections
        section_names = ['Main Flow', 'Alternative Flows', 'Business Rules', 'Exceptions']
        for section_name in section_names:
            key = section_name.lower().replace(' ', '_')
            if_key = f"if_{key}"

            if section_name in sections:
                data[if_key] = True
                if section_name == 'Business Rules':
                    # Format as bulleted list
                    rules = [line.strip() for line in sections[section_name].split('\n') if line.strip()]
                    if len(rules) > 1:
                        data[f"{key}_content"] = '\n'.join(f"- {rule}" for rule in rules)
                    else:
                        data[f"{key}_content"] = sections[section_name]
                else:
                    data[f"{key}_content"] = sections[section_name]
            else:
                data[if_key] = False

        # Add scenarios (pre-rendered)
        if uc.object_id in self.extractor.scenarios:
            data['if_scenarios'] = True
            data['scenario_content'] = self._generate_scenarios_section(uc.object_id)
        else:
            data['if_scenarios'] = False

        # Debug: log data keys
        logger.debug(f"Data keys for {uc.name}: {list(data.keys())}")
        logger.debug(f"if_actors: {data.get('if_actors')}, if_preconditions: {data.get('if_preconditions')}, if_scenarios: {data.get('if_scenarios')}")

        # Render template
        rendered = self.template_renderer.render(template, data)

        # Prepend breadcrumbs (title is in template)
        # Remove title from template output if it exists
        if rendered.startswith(f"# {uc.name}"):
            # Template includes title, insert breadcrumbs after it
            lines = rendered.split('\n', 2)
            if len(lines) >= 2:
                return f"{lines[0]}\n\n{breadcrumbs}{lines[1]}\n" + (lines[2] if len(lines) > 2 else "")

        # Template doesn't include title, add it
        return f"# {uc.name}\n\n{breadcrumbs}{rendered}"

    def _generate_single_use_case(self, uc, uc_file: Path) -> str:
        """Generate documentation for a single use case"""
        # Generate breadcrumbs first (always added regardless of template use)
        breadcrumbs = generate_breadcrumbs(uc_file, self.output_dir, uc.name)

        # Try to use template if available
        if self.use_template:
            try:
                return self._generate_with_template(uc, breadcrumbs)
            except Exception as e:
                logger.warning(f"Template rendering failed for {uc.name}: {e}, using fallback")

        # Fallback to original hard-coded generation
        uc_content = f"# {uc.name}\n\n"
        uc_content += breadcrumbs

        if uc.stereotype:
            uc_content += f"**Stereotype:** <<{uc.stereotype}>>\n\n"

        uc_content += f"**Package:** {uc.package_name}\n\n"

        # Add metadata line (version, modified date, guid)
        metadata_parts = []
        if uc.version:
            metadata_parts.append(f"Version: {uc.version}")
        if uc.modified_date:
            metadata_parts.append(f"Modified: {uc.modified_date}")
        if uc.guid:
            metadata_parts.append(f"GUID: {uc.guid}")

        if metadata_parts:
            uc_content += f"**{' | '.join(metadata_parts)}**\n\n"

        # Parse structured notes
        sections = uc.parse_structured_note()

        # Description - only show if there's content not in other sections
        has_structured_sections = any(key in sections for key in ['Preconditions', 'Postconditions',
                                                                   'Main Flow', 'Scenarios',
                                                                   'Alternative Flows', 'Business Rules',
                                                                   'Exceptions'])

        if 'Description' in sections and sections['Description']:
            uc_content += f"**Description:** {sections['Description']}\n\n"
        elif not has_structured_sections and uc.clean_note():
            # If no structured sections found, show the whole note as description
            uc_content += f"**Description:** {uc.clean_note()}\n\n"
        elif not has_structured_sections:
            uc_content += "**Description:** No description available\n\n"

        # Find related actors and use cases
        connectors = self.extractor.get_connectors_for_element(uc.object_id)

        actors_set = set()
        includes_set = set()
        extends_set = set()
        associations_set = set()
        invokes_set = set()
        realizes_set = set()

        for conn in connectors:
            # Check both connector_type and stereotype for relationship type
            conn_type_lower = conn.connector_type.lower()
            stereotype_lower = conn.stereotype.lower() if conn.stereotype else ''

            if conn.source_id == uc.object_id:
                target = self.extractor.elements.get(conn.target_id)
                if target:
                    if target.object_type == 'Actor':
                        actors_set.add(target.name)
                    elif target.object_type == 'UseCase':
                        # Check stereotype first, then connector_type
                        if 'include' in stereotype_lower or 'include' in conn_type_lower:
                            includes_set.add(target.name)
                        elif 'extend' in stereotype_lower or 'extend' in conn_type_lower:
                            extends_set.add(target.name)
                        elif 'invoke' in stereotype_lower or conn_type_lower == 'dependency':
                            invokes_set.add(target.name)
                        elif 'realize' in stereotype_lower or 'realise' in stereotype_lower or conn_type_lower == 'realisation':
                            realizes_set.add(target.name)
                        else:
                            associations_set.add(target.name)
            elif conn.target_id == uc.object_id:
                source = self.extractor.elements.get(conn.source_id)
                if source:
                    if source.object_type == 'Actor':
                        actors_set.add(source.name)
                    elif source.object_type == 'UseCase':
                        # For incoming relationships, only extend relationships are shown
                        if 'extend' in stereotype_lower or 'extend' in conn_type_lower:
                            extends_set.add(source.name)

        # Convert sets to sorted lists
        actors_list = sorted(actors_set)
        includes = sorted(includes_set)
        extends = sorted(extends_set)
        invokes = sorted(invokes_set)
        realizes = sorted(realizes_set)
        associations = sorted(associations_set)

        if actors_list:
            uc_content += f"**Actors:** {', '.join(actors_list)}\n\n"

        if includes:
            uc_content += "**Includes:**\n"
            for inc in includes:
                uc_content += f"- <<include>> {inc}\n"
            uc_content += "\n"

        if extends:
            uc_content += "**Extended by:**\n"
            for ext in extends:
                uc_content += f"- <<extend>> {ext}\n"
            uc_content += "\n"

        if invokes:
            uc_content += "**Invokes:**\n"
            for inv in invokes:
                uc_content += f"- <<invokes>> {inv}\n"
            uc_content += "\n"

        if realizes:
            uc_content += "**Realizes:**\n"
            for rel in realizes:
                uc_content += f"- <<realize>> {rel}\n"
            uc_content += "\n"

        if associations:
            uc_content += "**Related Use Cases:**\n"
            for assoc in associations:
                uc_content += f"- {assoc}\n"
            uc_content += "\n"

        # Add diagrams
        diagrams = self.extractor.get_diagrams_for_element(uc.object_id)
        if diagrams:
            uc_content += "**Diagrams:**\n\n"
            for diagram_guid in diagrams:
                # Check if PNG rendering is available
                if diagram_guid in self.diagram_guid_to_png:
                    png_path = self.diagram_guid_to_png[diagram_guid]
                    # Fix path to be relative from use-cases/ subdirectory
                    png_path = f"../{png_path}"
                    uc_content += f"![Diagram {diagram_guid}]({png_path})\n\n"
                else:
                    # Fallback to text placeholder
                    uc_content += f"- diagram {diagram_guid}\n"
            if not any(diagram_guid in self.diagram_guid_to_png for diagram_guid in diagrams):
                uc_content += "\n"

        # Add pre-conditions and post-conditions from constraints table
        if uc.object_id in self.extractor.constraints:
            preconditions = [c for c in self.extractor.constraints[uc.object_id] if c.constraint_type == 'Pre-condition']
            postconditions = [c for c in self.extractor.constraints[uc.object_id] if c.constraint_type == 'Post-condition']

            if preconditions:
                uc_content += "## Preconditions\n\n"
                for pc in preconditions:
                    uc_content += f"**{pc.name}**\n\n"
                    if pc.notes:
                        uc_content += f"{pc.notes}\n\n"

            if postconditions:
                uc_content += "## Postconditions\n\n"
                for pc in postconditions:
                    uc_content += f"**{pc.name}**\n\n"
                    if pc.notes:
                        uc_content += f"{pc.notes}\n\n"

        # Add structured sections from notes (excluding Preconditions/Postconditions if already shown from constraints)
        section_order = ['Preconditions', 'Postconditions', 'Main Flow', 'Scenarios',
                       'Alternative Flows', 'Business Rules', 'Exceptions']

        # Skip Preconditions/Postconditions from notes if we already added them from constraints
        has_constraints = uc.object_id in self.extractor.constraints
        preconditions_from_constraints = has_constraints and any(c.constraint_type == 'Pre-condition' for c in self.extractor.constraints[uc.object_id])
        postconditions_from_constraints = has_constraints and any(c.constraint_type == 'Post-condition' for c in self.extractor.constraints[uc.object_id])

        for section_name in section_order:
            # Skip if already shown from constraints
            if section_name == 'Preconditions' and preconditions_from_constraints:
                continue
            if section_name == 'Postconditions' and postconditions_from_constraints:
                continue

            if section_name in sections:
                uc_content += f"## {section_name}\n\n"
                # Format Business Rules as a bulleted list if they have multiple lines
                if section_name == 'Business Rules':
                    rules = [line.strip() for line in sections[section_name].split('\n') if line.strip()]
                    if len(rules) > 1:
                        for rule in rules:
                            uc_content += f"- {rule}\n"
                        uc_content += "\n"
                    else:
                        uc_content += f"{sections[section_name]}\n\n"
                else:
                    uc_content += f"{sections[section_name]}\n\n"

        # Add scenarios from t_objectscenarios table
        if uc.object_id in self.extractor.scenarios:
            uc_content += self._generate_scenarios_section(uc.object_id)

        return uc_content

    def _format_step_with_uc_references(self, step: str, uc_object_id: int) -> str:
        """Format a step to use proper UML notation for use case references"""
        # Replace single angle bracket notation with double angle brackets
        # The model may have <include>, <extend>, <invoke> etc. which should be <<include>>, <<extend>>, <<invoke>>
        import re

        # Replace <include> with <<include>>
        step = re.sub(r'<include>', '<<include>>', step, flags=re.IGNORECASE)
        # Replace <extend> with <<extend>>
        step = re.sub(r'<extend>', '<<extend>>', step, flags=re.IGNORECASE)
        # Replace <invoke> with <<invoke>>
        step = re.sub(r'<invoke>', '<<invoke>>', step, flags=re.IGNORECASE)

        return step

    def _generate_scenarios_section(self, object_id: int) -> str:
        """Generate scenarios section for a use case"""
        content = ""
        uc_scenarios = self.extractor.scenarios[object_id]

        # Create a GUID-to-scenario mapping for quick lookup
        guid_to_scenario = {}
        for scenario in uc_scenarios:
            if scenario.ea_guid:
                guid_to_scenario[scenario.ea_guid] = scenario

        # Create a GUID-to-level mapping from extensions in Basic Path
        guid_to_level = {}
        for scenario in uc_scenarios:
            if scenario.scenario_type == 'Basic Path':
                for ext_step_idx, ext_level, ext_guid in scenario.extensions:
                    guid_to_level[ext_guid] = ext_level

        # Group scenarios by type
        scenarios_by_type = defaultdict(list)
        for scenario in uc_scenarios:
            scenarios_by_type[scenario.scenario_type].append(scenario)

        # Display scenarios organized by type
        for scenario_type in ['Basic Path', 'Alternate', 'Exception']:
            if scenario_type in scenarios_by_type:
                # Sort scenarios by their step level
                sorted_scenarios = sorted(
                    scenarios_by_type[scenario_type],
                    key=lambda s: guid_to_level.get(s.ea_guid, '0') if s.ea_guid else '0'
                )

                for scenario in sorted_scenarios:
                    # For Alternate/Exception, prefix with step level if available
                    if scenario.scenario_type in ['Alternate', 'Exception'] and scenario.ea_guid in guid_to_level:
                        level_prefix = guid_to_level[scenario.ea_guid] + " "
                    else:
                        level_prefix = ""

                    content += f"### {level_prefix}{scenario.scenario_type}: {scenario.name}\n\n"

                    if scenario.steps:
                        content += "**Steps:**\n\n"
                        for idx, step in enumerate(scenario.steps, 1):
                            formatted_step = self._format_step_with_uc_references(step, object_id)
                            content += f"{idx}. {formatted_step}\n"

                            # Check if this step has extensions (for Basic Path)
                            if scenario.scenario_type == 'Basic Path':
                                for ext_step_idx, ext_level, ext_guid in scenario.extensions:
                                    if ext_step_idx == idx - 1:  # idx is 1-based, ext_step_idx is 0-based
                                        # Find the scenario that this extension points to
                                        if ext_guid in guid_to_scenario:
                                            ext_scenario = guid_to_scenario[ext_guid]
                                            flow_type = "Alternate flow" if ext_scenario.scenario_type == "Alternate" else "Exception flow"
                                            content += f"   - _{ext_level}. {flow_type}: {ext_scenario.name}_\n"

                        content += "\n"

                    if scenario.notes:
                        content += f"**Notes:** {scenario.notes}\n\n"

        # Display any other scenario types not in the standard list
        for scenario_type, scenarios in scenarios_by_type.items():
            if scenario_type not in ['Basic Path', 'Alternate', 'Exception']:
                # Sort scenarios by their step level
                sorted_scenarios = sorted(
                    scenarios,
                    key=lambda s: guid_to_level.get(s.ea_guid, '0') if s.ea_guid else '0'
                )

                for scenario in sorted_scenarios:
                    # Prefix with step level if available
                    if scenario.ea_guid in guid_to_level:
                        level_prefix = guid_to_level[scenario.ea_guid] + " "
                    else:
                        level_prefix = ""

                    content += f"### {level_prefix}{scenario.scenario_type}: {scenario.name}\n\n"

                    if scenario.steps:
                        content += "**Steps:**\n\n"
                        for idx, step in enumerate(scenario.steps, 1):
                            formatted_step = self._format_step_with_uc_references(step, object_id)
                            content += f"{idx}. {formatted_step}\n"

                            # Check if this step has extensions
                            for ext_step_idx, ext_level, ext_guid in scenario.extensions:
                                if ext_step_idx == idx - 1:  # idx is 1-based, ext_step_idx is 0-based
                                    # Find the scenario that this extension points to
                                    if ext_guid in guid_to_scenario:
                                        ext_scenario = guid_to_scenario[ext_guid]
                                        flow_type = "Alternate flow" if ext_scenario.scenario_type == "Alternate" else "Exception flow"
                                        content += f"   - _{ext_level}. {flow_type}: {ext_scenario.name}_\n"

                        content += "\n"

                    if scenario.notes:
                        content += f"**Notes:** {scenario.notes}\n\n"

        return content
