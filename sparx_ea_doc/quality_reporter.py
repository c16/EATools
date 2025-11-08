"""
Quality checking and reporting module.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from .utils import generate_breadcrumbs

logger = logging.getLogger(__name__)


class QualityReporter:
    """Performs quality checks and generates reports"""

    def __init__(self, extractor, output_dir: Path, config: Dict = None):
        """
        Initialize the quality reporter

        Args:
            extractor: SparxExtractor instance with extracted data
            output_dir: Output directory for documentation
            config: Optional configuration dictionary
        """
        self.extractor = extractor
        self.output_dir = output_dir
        self.config = config or {}

        # Quality metrics storage
        self.quality_metrics: Dict[str, Any] = {
            'undocumented': [],
            'orphaned': [],
            'missing_relationships': [],
            'total_elements': 0
        }

    def perform_quality_checks(self):
        """Perform quality checks on the model"""
        logger.info("Performing quality checks...")

        min_desc_length = self.config.get('quality_checks', {}).get('min_description_length', 20)

        for element in self.extractor.elements.values():
            # Check for undocumented elements
            desc = element.clean_note()
            if not desc or len(desc) < min_desc_length:
                self.quality_metrics['undocumented'].append({
                    'name': element.name,
                    'type': element.object_type,
                    'package': element.package_name
                })

        self.quality_metrics['total_elements'] = len(self.extractor.elements)
        logger.info("Quality checks complete")

    def generate_quality_report(self):
        """Generate quality report"""
        logger.info("Generating quality report...")

        report_dir = self.output_dir / 'reports'
        report_dir.mkdir(exist_ok=True)

        report_file = report_dir / 'quality-report.md'
        report_content = "# Documentation Quality Report\n\n"
        report_content += generate_breadcrumbs(report_file, self.output_dir, "Quality Report")
        report_content += f"**Total Elements:** {self.quality_metrics['total_elements']}\n\n"

        # Undocumented elements
        undoc = self.quality_metrics['undocumented']
        report_content += f"## Undocumented Elements ({len(undoc)})\n\n"

        if undoc:
            report_content += "The following elements have insufficient or missing documentation:\n\n"
            report_content += "| Name | Type | Package |\n"
            report_content += "|------|------|----------|\n"

            for item in undoc:
                report_content += f"| {item['name']} | {item['type']} | {item['package']} |\n"

            report_content += "\n"
        else:
            report_content += "*All elements are properly documented.*\n\n"

        # Summary statistics
        report_content += "## Summary Statistics\n\n"
        report_content += f"- Use Cases: {len(self.extractor.use_cases)}\n"
        report_content += f"- Actors: {len(self.extractor.actors)}\n"
        report_content += f"- State Machines: {len(self.extractor.state_machines)}\n"
        report_content += f"- Components: {len(self.extractor.components)}\n"
        report_content += f"- Classes: {len(self.extractor.classes)}\n"
        report_content += f"- Interfaces: {len(self.extractor.interfaces)}\n"
        report_content += f"- Enumerations: {len(self.extractor.enumerations)}\n"
        report_content += f"- Total Relationships: {len(self.extractor.connectors)}\n"

        documentation_rate = ((self.quality_metrics['total_elements'] - len(undoc)) /
                             self.quality_metrics['total_elements'] * 100) if self.quality_metrics['total_elements'] > 0 else 0
        report_content += f"\n**Documentation Rate:** {documentation_rate:.1f}%\n"

        with open(report_file, 'w') as f:
            f.write(report_content)

        # Generate/update reports index
        self._generate_reports_index()

        logger.info("Quality report generated")

    def generate_dependencies_report(self):
        """Generate dependencies analysis report"""
        logger.info("Generating dependencies report...")

        report_dir = self.output_dir / 'reports'
        report_dir.mkdir(exist_ok=True)

        report_file = report_dir / 'dependencies.md'
        report_content = "# Dependency Analysis\n\n"
        report_content += generate_breadcrumbs(report_file, self.output_dir, "Dependencies")
        # Analyze dependency connectors
        dep_connectors = [c for c in self.extractor.connectors if c.connector_type == 'Dependency']

        report_content += f"## Total Dependencies: {len(dep_connectors)}\n\n"

        if dep_connectors:
            report_content += "| Source | Target | Type |\n"
            report_content += "|--------|--------|------|\n"

            for conn in dep_connectors:
                source = self.extractor.elements.get(conn.source_id)
                target = self.extractor.elements.get(conn.target_id)
                if source and target:
                    report_content += f"| {conn.source_name} | {conn.target_name} | {source.object_type} → {target.object_type} |\n"

            report_content += "\n"

        # Mermaid diagram
        if dep_connectors:
            report_content += "## Dependency Graph\n\n"
            report_content += "```mermaid\n"
            report_content += "graph LR\n"

            added_nodes = set()
            for conn in dep_connectors:
                source = self.extractor.elements.get(conn.source_id)
                target = self.extractor.elements.get(conn.target_id)
                if source and target:
                    # Clean names for mermaid
                    source_id = f"N{conn.source_id}"
                    target_id = f"N{conn.target_id}"

                    if source_id not in added_nodes:
                        report_content += f"    {source_id}[\"{conn.source_name}\"]\n"
                        added_nodes.add(source_id)

                    if target_id not in added_nodes:
                        report_content += f"    {target_id}[\"{conn.target_name}\"]\n"
                        added_nodes.add(target_id)

                    report_content += f"    {source_id} --> {target_id}\n"

            report_content += "```\n\n"

        with open(report_file, 'w') as f:
            f.write(report_content)

        # Generate/update reports index
        self._generate_reports_index()

        logger.info("Dependencies report generated")

    def _generate_reports_index(self):
        """Generate or update the reports index page"""
        report_dir = self.output_dir / 'reports'
        index_file = report_dir / 'index.md'

        index_content = "# Reports\n\n"
        index_content += generate_breadcrumbs(index_file, self.output_dir, "Reports")
        index_content += "This section contains various reports and analyses of the model.\n\n"
        index_content += "## Available Reports\n\n"

        # List report files
        reports = [
            ("Quality Report", "quality-report.md", "Documentation quality metrics and coverage"),
            ("Dependency Analysis", "dependencies.md", "System dependencies and relationships")
        ]

        for title, filename, description in reports:
            index_content += f"### [{title}]({filename})\n\n"
            index_content += f"{description}\n\n"

        with open(index_file, 'w') as f:
            f.write(index_content)
