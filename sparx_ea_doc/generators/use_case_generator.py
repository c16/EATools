"""
Use case documentation generator module.
"""

import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

logger = logging.getLogger(__name__)


class UseCaseGenerator:
    """Generates use case documentation"""

    def __init__(self, extractor, output_dir: Path):
        """
        Initialize the use case generator

        Args:
            extractor: SparxExtractor instance with extracted data
            output_dir: Output directory for documentation
        """
        self.extractor = extractor
        self.output_dir = output_dir

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

    def _generate_actors_doc(self, uc_dir: Path):
        """Generate actors documentation"""
        actors_content = "# Actors\n\n"
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
        uc_index_content = "# Use Cases\n\n"
        uc_index_content += "This document provides an overview of all use cases in the system.\n\n"
        uc_index_content += "## Use Case List\n\n"

        for uc in self.extractor.use_cases:
            uc_filename = f"{uc.name.lower().replace(' ', '-')}.md"

            # Add to index
            uc_index_content += f"- [{uc.name}]({uc_filename})\n"

            # Generate individual use case file
            uc_content = self._generate_single_use_case(uc)

            with open(uc_dir / uc_filename, 'w') as f:
                f.write(uc_content)

        # Write index
        with open(uc_dir / 'index.md', 'w') as f:
            f.write(uc_index_content)

    def _generate_single_use_case(self, uc) -> str:
        """Generate documentation for a single use case"""
        uc_content = f"# {uc.name}\n\n"

        if uc.stereotype:
            uc_content += f"**Stereotype:** <<{uc.stereotype}>>\n\n"

        uc_content += f"**Package:** {uc.package_name}\n\n"

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

        actors_list = []
        includes = []
        extends = []
        associations = []

        for conn in connectors:
            if conn.source_id == uc.object_id:
                target = self.extractor.elements.get(conn.target_id)
                if target:
                    if target.object_type == 'Actor':
                        actors_list.append(target.name)
                    elif target.object_type == 'UseCase':
                        if 'include' in conn.connector_type.lower():
                            includes.append(target.name)
                        elif 'extend' in conn.connector_type.lower():
                            extends.append(target.name)
                        else:
                            associations.append(target.name)
            elif conn.target_id == uc.object_id:
                source = self.extractor.elements.get(conn.source_id)
                if source:
                    if source.object_type == 'Actor':
                        actors_list.append(source.name)
                    elif source.object_type == 'UseCase':
                        if 'extend' in conn.connector_type.lower():
                            extends.append(source.name)

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

        if associations:
            uc_content += "**Related Use Cases:**\n"
            for assoc in associations:
                uc_content += f"- {assoc}\n"
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

                    content += f"## {level_prefix}{scenario.scenario_type}: {scenario.name}\n\n"

                    if scenario.steps:
                        content += "**Steps:**\n\n"
                        for idx, step in enumerate(scenario.steps, 1):
                            content += f"{idx}. {step}\n"

                            # Check if this step has extensions (for Basic Path)
                            if scenario.scenario_type == 'Basic Path':
                                for ext_step_idx, ext_level, ext_guid in scenario.extensions:
                                    if ext_step_idx == idx - 1:  # idx is 1-based, ext_step_idx is 0-based
                                        # Find the scenario that this extension points to
                                        if ext_guid in guid_to_scenario:
                                            ext_scenario = guid_to_scenario[ext_guid]
                                            flow_type = "Alternate flow" if ext_scenario.scenario_type == "Alternate" else "Exception flow"
                                            content += f"   {ext_level}. {flow_type}: {ext_scenario.name}\n"

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

                    content += f"## {level_prefix}{scenario.scenario_type}: {scenario.name}\n\n"

                    if scenario.steps:
                        content += "**Steps:**\n\n"
                        for idx, step in enumerate(scenario.steps, 1):
                            content += f"{idx}. {step}\n"

                            # Check if this step has extensions
                            for ext_step_idx, ext_level, ext_guid in scenario.extensions:
                                if ext_step_idx == idx - 1:  # idx is 1-based, ext_step_idx is 0-based
                                    # Find the scenario that this extension points to
                                    if ext_guid in guid_to_scenario:
                                        ext_scenario = guid_to_scenario[ext_guid]
                                        flow_type = "Alternate flow" if ext_scenario.scenario_type == "Alternate" else "Exception flow"
                                        content += f"   {ext_level}. {flow_type}: {ext_scenario.name}\n"

                        content += "\n"

                    if scenario.notes:
                        content += f"**Notes:** {scenario.notes}\n\n"

        return content
