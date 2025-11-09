"""
Data models for Sparx Enterprise Architect elements.
"""

import re
import html
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Element:
    """Base class for model elements"""
    object_id: int
    name: str
    object_type: str
    note: str
    stereotype: str
    package_name: str
    visibility: str = 'public'
    version: str = ''
    modified_date: str = ''
    guid: str = ''

    def clean_note(self) -> str:
        """Remove HTML tags and clean up note text"""
        if not self.note:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', self.note)
        # Decode HTML entities
        text = html.unescape(text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def parse_structured_note(self) -> Dict[str, str]:
        """
        Parse notes field for structured sections like:
        - Preconditions / Pre-conditions
        - Postconditions / Post-conditions
        - Main Flow / Scenario
        - Alternative Flows
        - Business Rules
        Returns dict with section names as keys
        """
        if not self.note:
            return {}

        # Remove HTML tags but keep structure
        text = re.sub(r'<[^>]+>', '', self.note)
        text = html.unescape(text)

        sections = {}
        current_section = None
        current_content = []

        # Common section headers to look for (case-insensitive)
        section_patterns = [
            (r'^(pre[-\s]?conditions?):?\s*$', 'Preconditions'),
            (r'^(post[-\s]?conditions?):?\s*$', 'Postconditions'),
            (r'^(main\s+flow):?\s*$', 'Main Flow'),
            (r'^(basic\s+flow):?\s*$', 'Main Flow'),
            (r'^(scenarios?):?\s*$', 'Scenarios'),
            (r'^(alternative\s+flows?):?\s*$', 'Alternative Flows'),
            (r'^(business\s+rules?):?\s*$', 'Business Rules'),
            (r'^(exceptions?):?\s*$', 'Exceptions'),
            (r'^(description):?\s*$', 'Description'),
        ]

        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line is a section header
            is_header = False
            for pattern, section_name in section_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    # Save previous section if any
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section_name
                    current_content = []
                    is_header = True
                    break

            if not is_header:
                if current_section:
                    current_content.append(line)
                else:
                    # Content before any section header goes to Description
                    if 'Description' not in sections:
                        sections['Description'] = line
                    else:
                        sections['Description'] += '\n' + line

        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections


@dataclass
class Attribute:
    """Class/component attribute"""
    name: str
    attr_type: str
    scope: str  # Public, Private, Protected
    default: str
    notes: str
    is_static: bool
    is_const: bool
    pos: int


@dataclass
class Operation:
    """Class/component operation/method"""
    name: str
    return_type: str
    scope: str
    is_abstract: bool
    is_static: bool
    notes: str
    parameters: List[Tuple[str, str]] = field(default_factory=list)  # [(name, type), ...]


@dataclass
class Connector:
    """Relationship between elements"""
    connector_id: int
    connector_type: str
    source_id: int
    target_id: int
    source_name: str
    target_name: str
    source_card: str
    target_card: str
    source_role: str
    target_role: str
    notes: str
    trigger: str = ''
    guard: str = ''
    stereotype: str = ''


@dataclass
class Scenario:
    """Use case scenario"""
    name: str
    scenario_type: str  # Basic Path, Exception, Alternate, etc.
    steps: List[str] = field(default_factory=list)
    notes: str = ''
    ea_guid: str = ''
    extensions: List[Tuple[int, str, str]] = field(default_factory=list)  # [(step_index, level, extension_guid), ...]


@dataclass
class Constraint:
    """Object constraint (pre-condition, post-condition, etc.)"""
    name: str
    constraint_type: str  # Pre-condition, Post-condition, etc.
    notes: str = ''
