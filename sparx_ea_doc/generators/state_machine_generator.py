"""
State machine documentation generator module.
"""

import logging
from pathlib import Path
from ..utils import generate_breadcrumbs
from ..template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class StateMachineGenerator:
    """Generates state machine documentation"""

    def __init__(self, extractor, output_dir: Path, template_dir: Path = None):
        """
        Initialize the state machine generator

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
        self.use_template = (template_dir / 'state_machine_template.md').exists()

    def generate(self):
        """Generate state machine documentation"""
        logger.info("Generating state machine documentation...")

        sm_dir = self.output_dir / 'state-machines'
        sm_dir.mkdir(exist_ok=True)

        index_file = sm_dir / 'index.md'
        sm_index_content = "# State Machines\n\n"
        sm_index_content += generate_breadcrumbs(index_file, self.output_dir, "State Machines")
        sm_index_content += "This document provides an overview of all state machines in the system.\n\n"

        if not self.extractor.state_machines and not self.extractor.states:
            sm_index_content += "*No state machines found in the model.*\n"
            with open(index_file, 'w') as f:
                f.write(sm_index_content)
            return

        sm_index_content += "## State Machine List\n\n"

        # Generate documentation for each state machine
        for sm in self.extractor.state_machines:
            sm_filename = f"sm-{sm.name.lower().replace(' ', '-')}.md"
            sm_file = sm_dir / sm_filename
            sm_index_content += f"- [{sm.name}]({sm_filename})\n"

            sm_content = self._generate_single_state_machine(sm, sm_file)

            with open(sm_file, 'w') as f:
                f.write(sm_content)

        # Check for orphaned states (states without a parent state machine)
        orphaned_states = self.extractor.states.get(0, []) + self.extractor.states.get(None, [])
        if orphaned_states:
            sm_index_content += "\n## Orphaned States\n\n"
            sm_index_content += "The following states are not associated with a state machine:\n\n"
            for state in orphaned_states:
                sm_index_content += f"- {state.name} ({state.object_type})\n"

        with open(index_file, 'w') as f:
            f.write(sm_index_content)

        logger.info(f"Generated documentation for {len(self.extractor.state_machines)} state machines")

    def _generate_single_state_machine(self, sm, sm_file: Path) -> str:
        """Generate documentation for a single state machine"""
        sm_content = f"# State Machine: {sm.name}\n\n"
        sm_content += generate_breadcrumbs(sm_file, self.output_dir, sm.name)
        sm_content += f"**Package:** {sm.package_name}\n\n"
        sm_content += f"**Description:** {sm.clean_note() or 'No description available'}\n\n"

        # Get states for this state machine
        states = self.extractor.states.get(sm.object_id, [])

        if states:
            # TODO: Revisit state documentation formatting for better readability
            # Consider alternative table formats or presentation styles
            sm_content += "## States\n\n"

            for state in states:
                sm_content += f"### {state.name}\n\n"

                # Get entry, do, exit operations for this state
                state_operations = self.extractor.operations.get(state.object_id, [])
                entry_ops = [op for op in state_operations if op.return_type == 'entry']
                do_ops = [op for op in state_operations if op.return_type == 'do']
                exit_ops = [op for op in state_operations if op.return_type == 'exit']

                # Format operations as bulleted lists
                entry_str = '<br>'.join([f'- {op.name}' for op in entry_ops]) if entry_ops else '-'
                do_str = '<br>'.join([f'- {op.name}' for op in do_ops]) if do_ops else '-'
                exit_str = '<br>'.join([f'- {op.name}' for op in exit_ops]) if exit_ops else '-'
                desc_str = state.clean_note() if state.clean_note() else '-'

                sm_content += "| Property | Value |\n"
                sm_content += "|----------|-------|\n"
                sm_content += f"| Type | {state.object_type} |\n"
                sm_content += f"| Entry | {entry_str} |\n"
                sm_content += f"| Do | {do_str} |\n"
                sm_content += f"| Exit | {exit_str} |\n"
                sm_content += f"| Description | {desc_str} |\n"
                sm_content += "\n"

            # Get transitions (StateFlow connectors)
            sm_content += "## Transitions\n\n"
            transitions_found = False

            for state in states:
                connectors = self.extractor.get_connectors_for_element(state.object_id, 'StateFlow')
                if connectors:
                    transitions_found = True
                    break

            if transitions_found:
                sm_content += "| From | To | Trigger | Guard | Notes |\n"
                sm_content += "|------|----|---------|-------|-------|\n"

                for state in states:
                    connectors = self.extractor.get_connectors_for_element(state.object_id, 'StateFlow')
                    for conn in connectors:
                        if conn.source_id == state.object_id:
                            target = self.extractor.elements.get(conn.target_id)
                            if target:
                                trigger = conn.trigger or '-'
                                guard = conn.guard or '-'
                                notes = conn.notes or '-'
                                sm_content += f"| {state.name} | {target.name} | {trigger} | {guard} | {notes} |\n"
                sm_content += "\n"
            else:
                sm_content += "*No transitions defined.*\n\n"
        else:
            sm_content += "*No states defined for this state machine.*\n\n"

        return sm_content
