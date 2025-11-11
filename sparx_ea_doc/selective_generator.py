"""
Selective documentation generator module
Supports generating only specific documents based on selection
"""

import logging
from pathlib import Path
from typing import Set, Optional, Callable
from datetime import datetime

from .extractor import SparxExtractor
from .generators import (
    UseCaseGenerator,
    StateMachineGenerator,
    ComponentGenerator,
    ClassGenerator
)
from .quality_reporter import QualityReporter

logger = logging.getLogger(__name__)


class SelectiveGenerator:
    """
    Wrapper around generators to support selective file generation
    """

    def __init__(self, extractor: SparxExtractor, output_dir: Path, selected_files: Set[str]):
        """
        Initialize selective generator

        Args:
            extractor: SparxExtractor instance with extracted data
            output_dir: Output directory for documentation
            selected_files: Set of file paths to generate (relative paths like 'use-cases/index.md')
        """
        self.extractor = extractor
        self.output_dir = output_dir
        self.selected_files = selected_files

    def should_generate(self, file_path: str) -> bool:
        """Check if a file should be generated based on selection"""
        return file_path in self.selected_files

    def generate_all(self, progress_callback: Optional[Callable[[str], None]] = None):
        """
        Generate all selected documentation

        Args:
            progress_callback: Optional callback function to report progress
        """
        generators = {
            'use-cases': UseCaseGenerator(self.extractor, self.output_dir),
            'state-machines': StateMachineGenerator(self.extractor, self.output_dir),
            'components': ComponentGenerator(self.extractor, self.output_dir),
            'classes': ClassGenerator(self.extractor, self.output_dir)
        }

        for name, generator in generators.items():
            if progress_callback:
                progress_callback(f"Generating {name}...")

            # Inject selection filter
            generator.should_generate = self.should_generate
            generator.generate()

        # Generate reports if selected
        if any('reports/' in f for f in self.selected_files):
            if progress_callback:
                progress_callback("Generating reports...")

            quality_reporter = QualityReporter(self.extractor, self.output_dir, {})
            quality_reporter.perform_quality_checks()

            if self.should_generate('reports/quality-report.md'):
                quality_reporter.generate_quality_report()

            if self.should_generate('reports/dependencies.md'):
                quality_reporter.generate_dependencies_report()

        # Generate index if selected
        if self.should_generate('index.md'):
            if progress_callback:
                progress_callback("Generating index...")
            self._generate_index()

    def _generate_index(self):
        """Generate main index document"""
        index_content = "# Sparx Enterprise Architect Model Documentation\n\n"
        index_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        index_content += "## Documentation Sections\n\n"

        if self.extractor.use_cases:
            index_content += f"### [Use Cases](use-cases/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.use_cases)} use cases.\n\n"

        if self.extractor.state_machines:
            index_content += f"### [State Machines](state-machines/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.state_machines)} state machines.\n\n"

        if self.extractor.components:
            index_content += f"### [Components](components/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.components)} components.\n\n"

        if self.extractor.classes:
            index_content += f"### [Classes and Modules](classes/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.classes)} classes.\n\n"

        with open(self.output_dir / 'index.md', 'w') as f:
            f.write(index_content)
