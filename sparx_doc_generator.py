#!/usr/bin/env python3
"""
Sparx Enterprise Architect Documentation Generator

This utility extracts and documents UML models from Sparx Enterprise Architect
.qea files (SQLite database format) and generates comprehensive markdown documentation.
"""

import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from sparx_ea_doc.extractor import SparxExtractor
from sparx_ea_doc.generators import (
    UseCaseGenerator,
    StateMachineGenerator,
    ComponentGenerator,
    ClassGenerator,
    RequirementGenerator
)
from sparx_ea_doc.quality_reporter import QualityReporter
from sparx_ea_doc.template_renderer import TemplateRenderer
from sparx_ea_doc.diff_generator import DiffGenerator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SparxDocGenerator:
    """Main documentation generator orchestrator"""

    def __init__(self, qea_path: str, output_dir: str = "docs", config: Optional[Dict] = None, template_dir: str = None, track_changes: bool = False):
        """
        Initialize the documentation generator

        Args:
            qea_path: Path to the .qea SQLite database file
            output_dir: Directory for output documentation
            config: Optional configuration dictionary
            template_dir: Optional directory containing templates
            track_changes: Enable change tracking and diff generation
        """
        self.qea_path = Path(qea_path)
        self.output_dir = Path(output_dir)
        self.config = config or {}
        self.track_changes = track_changes

        if not self.qea_path.exists():
            raise FileNotFoundError(f"QEA file not found: {self.qea_path}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized SparxDocGenerator for {self.qea_path}")

        # Set up template directory
        if template_dir is None:
            self.template_dir = Path(__file__).parent / 'templates'
        else:
            self.template_dir = Path(template_dir)

        # Initialize components
        self.extractor = SparxExtractor(self.qea_path)
        self.quality_reporter = QualityReporter(self.extractor, self.output_dir, self.config)
        self.template_renderer = TemplateRenderer(self.template_dir)

        # Initialize diff generator if change tracking is enabled
        self.diff_generator = None
        if self.track_changes:
            self.diff_generator = DiffGenerator(self.output_dir)
            logger.info("Change tracking enabled")

    def analyze_schema(self) -> Dict:
        """
        Analyze and document the database schema

        Returns:
            Dictionary containing schema information
        """
        logger.info("Analyzing database schema...")
        schema_info = {
            'tables': {},
            'analysis_date': datetime.now().isoformat()
        }

        self.extractor.connect_db()

        try:
            cursor = self.extractor.conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                # Get table info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = []
                for col in cursor.fetchall():
                    columns.append({
                        'name': col[1],
                        'type': col[2],
                        'notnull': bool(col[3]),
                        'default': col[4],
                        'pk': bool(col[5])
                    })

                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]

                schema_info['tables'][table] = {
                    'columns': columns,
                    'row_count': row_count
                }

            # Save schema to file
            schema_file = self.output_dir / 'schema.json'
            with open(schema_file, 'w') as f:
                json.dump(schema_info, f, indent=2)

            logger.info(f"Schema analysis complete. Found {len(tables)} tables.")
            logger.info(f"Schema saved to {schema_file}")

        finally:
            self.extractor.close_db()

        return schema_info

    def extract_model_data(self):
        """Extract all model data from the database"""
        logger.info("Starting model data extraction...")
        self.extractor.extract_all()

    def generate_documentation(self):
        """Generate all markdown documentation"""
        logger.info("Starting documentation generation...")

        # Initialize generators
        uc_generator = UseCaseGenerator(self.extractor, self.output_dir)
        req_generator = RequirementGenerator(self.extractor, self.output_dir)
        sm_generator = StateMachineGenerator(self.extractor, self.output_dir)
        comp_generator = ComponentGenerator(self.extractor, self.output_dir)
        class_generator = ClassGenerator(self.extractor, self.output_dir)

        # Generate all documentation
        uc_generator.generate()
        req_generator.generate()
        sm_generator.generate()
        comp_generator.generate()
        class_generator.generate()

        # Generate quality reports
        self.quality_reporter.perform_quality_checks()
        self.quality_reporter.generate_quality_report()
        self.quality_reporter.generate_dependencies_report()

        # Generate main index
        self.generate_index()

        logger.info("Documentation generation complete!")

    def generate_index(self):
        """Generate main index/navigation document"""
        logger.info("Generating main index...")

        # Check if template exists
        template_file = self.template_dir / 'index_template.md'
        use_template = template_file.exists()

        if use_template:
            try:
                # Build data dictionary for template
                data = {
                    'project_title': 'Sparx Enterprise Architect Model Documentation',
                    'source_file': self.qea_path.name,
                    'overview_text': 'This documentation was automatically generated from the Sparx Enterprise Architect model. Navigate through the sections below to explore different aspects of the system architecture.',
                    'total_elements': self.quality_reporter.quality_metrics['total_elements'],
                    'total_packages': len(self.extractor.packages),
                    'total_relationships': len(self.extractor.connectors),
                }

                # Use Cases section
                if self.extractor.use_cases:
                    data['if_use_cases'] = True
                    data['use_case_count'] = len(self.extractor.use_cases)
                    data['actor_count'] = len(self.extractor.actors)
                else:
                    data['if_use_cases'] = False

                # Requirements section
                if self.extractor.requirements:
                    data['if_requirements'] = True
                    data['requirement_count'] = len(self.extractor.requirements)
                else:
                    data['if_requirements'] = False

                # State Machines section
                if self.extractor.state_machines:
                    data['if_state_machines'] = True
                    data['state_machine_count'] = len(self.extractor.state_machines)
                else:
                    data['if_state_machines'] = False

                # Components section
                if self.extractor.components:
                    data['if_components'] = True
                    data['component_count'] = len(self.extractor.components)
                else:
                    data['if_components'] = False

                # Classes section
                if self.extractor.classes:
                    data['if_classes'] = True
                    data['class_count'] = len(self.extractor.classes)
                    data['interface_count'] = len(self.extractor.interfaces)
                    data['enumeration_count'] = len(self.extractor.enumerations)
                else:
                    data['if_classes'] = False

                # Reports section (always present)
                data['if_reports'] = True

                # Load and render template
                template = self.template_renderer.load_template('index_template.md')
                index_content = self.template_renderer.render(template, data)

                with open(self.output_dir / 'index.md', 'w') as f:
                    f.write(index_content)

                logger.info("Main index generated using template")
                return

            except Exception as e:
                logger.warning(f"Template rendering failed for index: {e}, using fallback")

        # Fallback to hard-coded generation
        index_content = "# Sparx Enterprise Architect Model Documentation\n\n"
        index_content += f"**Source:** {self.qea_path.name}\n\n"

        index_content += "## Overview\n\n"
        index_content += "This documentation was automatically generated from the Sparx Enterprise Architect model. "
        index_content += "Navigate through the sections below to explore different aspects of the system architecture.\n\n"

        index_content += "## Documentation Sections\n\n"

        if self.extractor.use_cases:
            index_content += f"### [Use Cases](use-cases/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.use_cases)} use cases and {len(self.extractor.actors)} actors describing "
            index_content += "system functionality and user interactions.\n\n"

        if self.extractor.requirements:
            index_content += f"### [Requirements](requirements/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.requirements)} requirements defining functional and non-functional "
            index_content += "system requirements.\n\n"

        if self.extractor.state_machines:
            index_content += f"### [State Machines](state-machines/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.state_machines)} state machines documenting system states "
            index_content += "and transitions.\n\n"

        if self.extractor.components:
            index_content += f"### [Components](components/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.components)} components and their interfaces, "
            index_content += "showing system architecture and component interactions.\n\n"

        if self.extractor.classes:
            index_content += f"### [Classes and Modules](classes/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.classes)} classes, {len(self.extractor.interfaces)} interfaces, "
            index_content += f"and {len(self.extractor.enumerations)} enumerations documenting the domain model.\n\n"

        index_content += "### [Reports](reports/index.md)\n\n"
        index_content += "Quality reports and analysis of the model documentation and structure.\n\n"

        index_content += "## Model Statistics\n\n"
        index_content += f"- **Total Elements:** {self.quality_reporter.quality_metrics['total_elements']}\n"
        index_content += f"- **Total Packages:** {len(self.extractor.packages)}\n"
        index_content += f"- **Total Relationships:** {len(self.extractor.connectors)}\n"

        with open(self.output_dir / 'index.md', 'w') as f:
            f.write(index_content)

        logger.info("Main index generated")

    def run(self, analyze_schema_only: bool = False):
        """
        Main execution flow

        Args:
            analyze_schema_only: If True, only analyze schema and exit
        """
        try:
            logger.info("=" * 60)
            logger.info("Sparx Enterprise Architect Documentation Generator")
            logger.info("=" * 60)

            if analyze_schema_only:
                self.analyze_schema()
                logger.info("Schema analysis complete")
                return

            # Full extraction and documentation
            self.extract_model_data()
            self.generate_documentation()

            # Handle change tracking
            if self.track_changes and self.diff_generator:
                logger.info("=" * 60)
                logger.info("Processing change tracking...")
                logger.info("=" * 60)

                prev_version = self.diff_generator.get_latest_version()

                if prev_version:
                    logger.info(f"Comparing with previous version: {prev_version['version_id']}")
                    logger.info(f"Previous version timestamp: {prev_version['timestamp']}")

                    try:
                        # Generate diff documentation
                        stats = self.diff_generator.generate_diff_documentation()

                        logger.info("=" * 60)
                        logger.info("Change Summary:")
                        logger.info(f"  Files Added:     {len(stats['files_added'])}")
                        logger.info(f"  Files Removed:   {len(stats['files_removed'])}")
                        logger.info(f"  Files Modified:  {len(stats['files_modified'])}")
                        logger.info(f"  Files Unchanged: {len(stats['files_unchanged'])}")
                        logger.info(f"  Total Additions: +{stats['total_additions']} lines")
                        logger.info(f"  Total Deletions: -{stats['total_deletions']} lines")
                        logger.info("=" * 60)
                        logger.info(f"Diff documentation generated in: {self.diff_generator.diff_output_dir}")
                        logger.info(f"View changes summary: {self.diff_generator.diff_output_dir / 'CHANGES.md'}")

                    except Exception as e:
                        logger.warning(f"Failed to generate diff documentation: {e}")
                else:
                    logger.info("No previous version found - this is the first tracked version")

                # Save current documentation as new version
                logger.info("Saving current documentation as new version...")
                version_id = self.diff_generator.save_current_version(
                    description=f"Documentation generated from {self.qea_path.name}"
                )
                logger.info(f"Version saved: {version_id}")

            logger.info("=" * 60)
            logger.info(f"Documentation generated successfully in: {self.output_dir}")
            logger.info(f"Open {self.output_dir / 'index.md'} to start browsing")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error during execution: {e}", exc_info=True)
            raise


def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file"""
    import yaml

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Generate documentation from Sparx Enterprise Architect .qea files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'qea_file',
        help='Path to the .qea SQLite database file'
    )

    parser.add_argument(
        '--output', '-o',
        default='docs',
        help='Output directory for documentation (default: docs)'
    )

    parser.add_argument(
        '--config', '-c',
        help='Path to configuration YAML file'
    )

    parser.add_argument(
        '--analyze-schema',
        action='store_true',
        help='Only analyze and output database schema'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--track-changes',
        action='store_true',
        help='Enable change tracking and generate diff documentation'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load config if provided
    config = None
    if args.config:
        config = load_config(args.config)

    # Create generator and run
    generator = SparxDocGenerator(
        qea_path=args.qea_file,
        output_dir=args.output,
        config=config,
        track_changes=args.track_changes
    )

    generator.run(analyze_schema_only=args.analyze_schema)


if __name__ == '__main__':
    main()
