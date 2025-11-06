"""
Sparx Enterprise Architect Documentation Generator Package
"""

from .models import Element, Attribute, Operation, Connector, Scenario, Constraint
from .extractor import SparxExtractor
from .quality_reporter import QualityReporter

__all__ = [
    'Element',
    'Attribute',
    'Operation',
    'Connector',
    'Scenario',
    'Constraint',
    'SparxExtractor',
    'QualityReporter',
]
