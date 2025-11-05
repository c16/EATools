#!/usr/bin/env python3
"""
Sparx Enterprise Architect Documentation Generator

This utility extracts and documents UML models from Sparx Enterprise Architect
.qea files (SQLite database format) and generates comprehensive markdown documentation.
"""

import sqlite3
import json
import re
import html
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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


class SparxDocGenerator:
    """Main documentation generator class"""

    def __init__(self, qea_path: str, output_dir: str = "docs", config: Optional[Dict] = None):
        """
        Initialize the documentation generator

        Args:
            qea_path: Path to the .qea SQLite database file
            output_dir: Directory for output documentation
            config: Optional configuration dictionary
        """
        self.qea_path = Path(qea_path)
        self.output_dir = Path(output_dir)
        self.config = config or {}
        self.conn: Optional[sqlite3.Connection] = None

        # Data storage
        self.elements: Dict[int, Element] = {}
        self.use_cases: List[Element] = []
        self.actors: List[Element] = []
        self.state_machines: List[Element] = []
        self.states: Dict[int, List[Element]] = defaultdict(list)
        self.components: List[Element] = []
        self.classes: List[Element] = []
        self.interfaces: List[Element] = []
        self.enumerations: List[Element] = []
        self.attributes: Dict[int, List[Attribute]] = defaultdict(list)
        self.operations: Dict[int, List[Operation]] = defaultdict(list)
        self.connectors: List[Connector] = []
        self.packages: Dict[int, str] = {}

        # Quality metrics
        self.quality_metrics: Dict[str, Any] = {
            'undocumented': [],
            'orphaned': [],
            'missing_relationships': [],
            'total_elements': 0
        }

        if not self.qea_path.exists():
            raise FileNotFoundError(f"QEA file not found: {self.qea_path}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized SparxDocGenerator for {self.qea_path}")

    def connect_db(self) -> sqlite3.Connection:
        """Establish connection to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.qea_path)
            self.conn.row_factory = sqlite3.Row
            logger.info("Database connection established")
            return self.conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def analyze_schema(self) -> Dict[str, Any]:
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

        cursor = self.conn.cursor()

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

        return schema_info

    def extract_packages(self):
        """Extract package information"""
        logger.info("Extracting packages...")
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT Package_ID, Name, Parent_ID
            FROM t_package
            ORDER BY Name
        """)

        for row in cursor.fetchall():
            package_id = row['Package_ID']
            package_name = row['Name']
            self.packages[package_id] = package_name

        logger.info(f"Extracted {len(self.packages)} packages")

    def extract_use_cases(self):
        """Extract use cases and actors"""
        logger.info("Extracting use cases and actors...")
        cursor = self.conn.cursor()

        # Extract use cases
        cursor.execute("""
            SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, o.Scope,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type = 'UseCase'
            ORDER BY o.Name
        """)

        for row in cursor.fetchall():
            element = Element(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type='UseCase',
                note=row['Note'] or '',
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public'
            )
            self.use_cases.append(element)
            self.elements[element.object_id] = element

        # Extract actors
        cursor.execute("""
            SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, o.Scope,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type = 'Actor'
            ORDER BY o.Name
        """)

        for row in cursor.fetchall():
            element = Element(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type='Actor',
                note=row['Note'] or '',
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public'
            )
            self.actors.append(element)
            self.elements[element.object_id] = element

        logger.info(f"Extracted {len(self.use_cases)} use cases and {len(self.actors)} actors")

    def extract_state_machines(self):
        """Extract state machines and states"""
        logger.info("Extracting state machines...")
        cursor = self.conn.cursor()

        # Extract state machine diagrams/containers
        cursor.execute("""
            SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, o.Scope,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type = 'StateMachine'
            ORDER BY o.Name
        """)

        for row in cursor.fetchall():
            element = Element(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type='StateMachine',
                note=row['Note'] or '',
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public'
            )
            self.state_machines.append(element)
            self.elements[element.object_id] = element

        # Extract states
        cursor.execute("""
            SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, o.Scope,
                   o.ParentID, o.Object_Type,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type IN ('State', 'StateNode', 'InitialState', 'FinalState')
            ORDER BY o.ParentID, o.Name
        """)

        for row in cursor.fetchall():
            element = Element(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type=row['Object_Type'],
                note=row['Note'] or '',
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public'
            )
            parent_id = row['ParentID']
            self.states[parent_id].append(element)
            self.elements[element.object_id] = element

        logger.info(f"Extracted {len(self.state_machines)} state machines")

    def extract_components(self):
        """Extract components"""
        logger.info("Extracting components...")
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, o.Scope,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type = 'Component'
            ORDER BY o.Name
        """)

        for row in cursor.fetchall():
            element = Element(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type='Component',
                note=row['Note'] or '',
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public'
            )
            self.components.append(element)
            self.elements[element.object_id] = element

        logger.info(f"Extracted {len(self.components)} components")

    def extract_classes(self):
        """Extract classes, interfaces, and enumerations"""
        logger.info("Extracting classes, interfaces, and enumerations...")
        cursor = self.conn.cursor()

        # Extract classes
        cursor.execute("""
            SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, o.Scope,
                   o.Abstract,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type = 'Class'
            ORDER BY o.Name
        """)

        for row in cursor.fetchall():
            element = Element(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type='Class',
                note=row['Note'] or '',
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public'
            )
            self.classes.append(element)
            self.elements[element.object_id] = element

        # Extract interfaces
        cursor.execute("""
            SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, o.Scope,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type = 'Interface'
            ORDER BY o.Name
        """)

        for row in cursor.fetchall():
            element = Element(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type='Interface',
                note=row['Note'] or '',
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public'
            )
            self.interfaces.append(element)
            self.elements[element.object_id] = element

        # Extract enumerations
        cursor.execute("""
            SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, o.Scope,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type = 'Enumeration'
            ORDER BY o.Name
        """)

        for row in cursor.fetchall():
            element = Element(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type='Enumeration',
                note=row['Note'] or '',
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public'
            )
            self.enumerations.append(element)
            self.elements[element.object_id] = element

        logger.info(f"Extracted {len(self.classes)} classes, {len(self.interfaces)} interfaces, "
                   f"and {len(self.enumerations)} enumerations")

    def extract_attributes(self):
        """Extract attributes for classes and components"""
        logger.info("Extracting attributes...")
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT Object_ID, Name, Type, Scope, Default, Notes,
                   IsStatic, IsConst, Pos
            FROM t_attribute
            ORDER BY Object_ID, Pos
        """)

        for row in cursor.fetchall():
            attr = Attribute(
                name=row['Name'],
                attr_type=row['Type'] or 'unknown',
                scope=row['Scope'] or 'Public',
                default=row['Default'] or '',
                notes=row['Notes'] or '',
                is_static=bool(row['IsStatic']),
                is_const=bool(row['IsConst']),
                pos=row['Pos'] or 0
            )
            self.attributes[row['Object_ID']].append(attr)

        logger.info(f"Extracted attributes for {len(self.attributes)} objects")

    def extract_operations(self):
        """Extract operations/methods for classes and components"""
        logger.info("Extracting operations...")
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT OperationID, Object_ID, Name, Type, Scope,
                   Abstract, IsStatic, Notes
            FROM t_operation
            ORDER BY Object_ID, Name
        """)

        operations_data = {}
        for row in cursor.fetchall():
            op = Operation(
                name=row['Name'],
                return_type=row['Type'] or 'void',
                scope=row['Scope'] or 'Public',
                is_abstract=bool(row['Abstract']),
                is_static=bool(row['IsStatic']),
                notes=row['Notes'] or ''
            )
            operations_data[row['OperationID']] = (row['Object_ID'], op)

        # Extract operation parameters
        cursor.execute("""
            SELECT OperationID, Name, Type, Kind
            FROM t_operationparams
            ORDER BY OperationID, Pos
        """)

        for row in cursor.fetchall():
            op_id = row['OperationID']
            if op_id in operations_data:
                kind = row['Kind'] or 'in'
                if kind.lower() != 'return':  # Skip return type parameters
                    obj_id, op = operations_data[op_id]
                    op.parameters.append((row['Name'], row['Type'] or 'unknown'))

        # Organize by object
        for obj_id, op in operations_data.values():
            self.operations[obj_id].append(op)

        logger.info(f"Extracted operations for {len(self.operations)} objects")

    def extract_connectors(self):
        """Extract relationships between elements"""
        logger.info("Extracting connectors/relationships...")
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT c.Connector_ID, c.Connector_Type,
                   c.Start_Object_ID, c.End_Object_ID,
                   c.SourceCard, c.DestCard,
                   c.SourceRole, c.DestRole,
                   c.Notes,
                   o1.Name as SourceName, o1.Object_Type as SourceType,
                   o2.Name as TargetName, o2.Object_Type as TargetType
            FROM t_connector c
            LEFT JOIN t_object o1 ON c.Start_Object_ID = o1.Object_ID
            LEFT JOIN t_object o2 ON c.End_Object_ID = o2.Object_ID
            ORDER BY c.Connector_ID
        """)

        for row in cursor.fetchall():
            connector = Connector(
                connector_id=row['Connector_ID'],
                connector_type=row['Connector_Type'],
                source_id=row['Start_Object_ID'],
                target_id=row['End_Object_ID'],
                source_name=row['SourceName'] or 'Unknown',
                target_name=row['TargetName'] or 'Unknown',
                source_card=row['SourceCard'] or '',
                target_card=row['DestCard'] or '',
                source_role=row['SourceRole'] or '',
                target_role=row['DestRole'] or '',
                notes=row['Notes'] or ''
            )
            self.connectors.append(connector)

        logger.info(f"Extracted {len(self.connectors)} connectors")

    def extract_model_data(self):
        """Main extraction orchestrator"""
        logger.info("Starting model data extraction...")

        self.connect_db()

        try:
            self.extract_packages()
            self.extract_use_cases()
            self.extract_state_machines()
            self.extract_components()
            self.extract_classes()
            self.extract_attributes()
            self.extract_operations()
            self.extract_connectors()

            self.quality_metrics['total_elements'] = len(self.elements)
            logger.info(f"Extraction complete. Total elements: {len(self.elements)}")

        except Exception as e:
            logger.error(f"Error during extraction: {e}")
            raise
        finally:
            self.close_db()

    def get_connectors_for_element(self, element_id: int, connector_type: Optional[str] = None) -> List[Connector]:
        """Get all connectors involving a specific element"""
        connectors = []
        for conn in self.connectors:
            if conn.source_id == element_id or conn.target_id == element_id:
                if connector_type is None or conn.connector_type == connector_type:
                    connectors.append(conn)
        return connectors

    def generate_use_case_docs(self):
        """Generate use case documentation"""
        logger.info("Generating use case documentation...")

        uc_dir = self.output_dir / 'use-cases'
        uc_dir.mkdir(exist_ok=True)

        # Generate actors documentation
        actors_content = "# Actors\n\n"
        actors_content += "This document lists all actors in the system.\n\n"

        for actor in self.actors:
            actors_content += f"## {actor.name}\n\n"
            if actor.stereotype:
                actors_content += f"**Stereotype:** <<{actor.stereotype}>>\n\n"
            actors_content += f"**Description:** {actor.clean_note() or 'No description available'}\n\n"
            actors_content += "---\n\n"

        with open(uc_dir / 'actors.md', 'w') as f:
            f.write(actors_content)

        # Generate individual use case documents
        uc_index_content = "# Use Cases\n\n"
        uc_index_content += "This document provides an overview of all use cases in the system.\n\n"
        uc_index_content += "## Use Case List\n\n"

        for idx, uc in enumerate(self.use_cases, 1):
            uc_id = f"UC-{idx:03d}"
            uc_filename = f"uc-{idx:03d}-{uc.name.lower().replace(' ', '-')}.md"

            # Add to index
            uc_index_content += f"- [{uc_id}: {uc.name}]({uc_filename})\n"

            # Generate individual use case file
            uc_content = f"# {uc_id}: {uc.name}\n\n"

            if uc.stereotype:
                uc_content += f"**Stereotype:** <<{uc.stereotype}>>\n\n"

            uc_content += f"**Package:** {uc.package_name}\n\n"
            uc_content += f"**Description:** {uc.clean_note() or 'No description available'}\n\n"

            # Find related actors and use cases
            connectors = self.get_connectors_for_element(uc.object_id)

            actors_list = []
            includes = []
            extends = []
            associations = []

            for conn in connectors:
                if conn.source_id == uc.object_id:
                    target = self.elements.get(conn.target_id)
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
                    source = self.elements.get(conn.source_id)
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

            with open(uc_dir / uc_filename, 'w') as f:
                f.write(uc_content)

        # Write index
        with open(uc_dir / 'index.md', 'w') as f:
            f.write(uc_index_content)

        logger.info(f"Generated documentation for {len(self.use_cases)} use cases")

    def generate_state_machine_docs(self):
        """Generate state machine documentation"""
        logger.info("Generating state machine documentation...")

        sm_dir = self.output_dir / 'state-machines'
        sm_dir.mkdir(exist_ok=True)

        sm_index_content = "# State Machines\n\n"
        sm_index_content += "This document provides an overview of all state machines in the system.\n\n"

        if not self.state_machines and not self.states:
            sm_index_content += "*No state machines found in the model.*\n"
            with open(sm_dir / 'index.md', 'w') as f:
                f.write(sm_index_content)
            return

        sm_index_content += "## State Machine List\n\n"

        # If we have state machine containers
        for sm in self.state_machines:
            sm_filename = f"sm-{sm.name.lower().replace(' ', '-')}.md"
            sm_index_content += f"- [{sm.name}]({sm_filename})\n"

            sm_content = f"# State Machine: {sm.name}\n\n"
            sm_content += f"**Package:** {sm.package_name}\n\n"
            sm_content += f"**Description:** {sm.clean_note() or 'No description available'}\n\n"

            # Get states for this state machine
            states = self.states.get(sm.object_id, [])

            if states:
                sm_content += "## States\n\n"
                sm_content += "| State | Type | Description |\n"
                sm_content += "|-------|------|-------------|\n"

                for state in states:
                    desc = state.clean_note() or 'No description'
                    sm_content += f"| {state.name} | {state.object_type} | {desc} |\n"

                sm_content += "\n"

                # Get transitions (StateFlow connectors)
                sm_content += "## Transitions\n\n"
                transitions_found = False

                for state in states:
                    connectors = self.get_connectors_for_element(state.object_id, 'StateFlow')
                    if connectors:
                        transitions_found = True
                        break

                if transitions_found:
                    sm_content += "| From | To | Notes |\n"
                    sm_content += "|------|----|-------|\n"

                    for state in states:
                        connectors = self.get_connectors_for_element(state.object_id, 'StateFlow')
                        for conn in connectors:
                            if conn.source_id == state.object_id:
                                target = self.elements.get(conn.target_id)
                                if target:
                                    notes = conn.notes or '-'
                                    sm_content += f"| {state.name} | {target.name} | {notes} |\n"
                    sm_content += "\n"
                else:
                    sm_content += "*No transitions defined.*\n\n"
            else:
                sm_content += "*No states defined for this state machine.*\n\n"

            with open(sm_dir / sm_filename, 'w') as f:
                f.write(sm_content)

        # Also check for orphaned states (states without a parent state machine)
        orphaned_states = self.states.get(0, []) + self.states.get(None, [])
        if orphaned_states:
            sm_index_content += "\n## Orphaned States\n\n"
            sm_index_content += "The following states are not associated with a state machine:\n\n"
            for state in orphaned_states:
                sm_index_content += f"- {state.name} ({state.object_type})\n"

        with open(sm_dir / 'index.md', 'w') as f:
            f.write(sm_index_content)

        logger.info(f"Generated documentation for {len(self.state_machines)} state machines")

    def generate_component_docs(self):
        """Generate component documentation"""
        logger.info("Generating component documentation...")

        comp_dir = self.output_dir / 'components'
        comp_dir.mkdir(exist_ok=True)

        comp_index_content = "# Components\n\n"
        comp_index_content += "This document provides an overview of all components in the system.\n\n"
        comp_index_content += "## Component List\n\n"

        for comp in self.components:
            comp_filename = f"comp-{comp.name.lower().replace(' ', '-')}.md"
            comp_index_content += f"- [{comp.name}]({comp_filename})\n"

            comp_content = f"# Component: {comp.name}\n\n"

            if comp.stereotype:
                comp_content += f"**Stereotype:** <<{comp.stereotype}>>\n\n"

            comp_content += f"**Package:** {comp.package_name}\n\n"
            comp_content += f"**Description:** {comp.clean_note() or 'No description available'}\n\n"

            # Get interfaces and dependencies
            connectors = self.get_connectors_for_element(comp.object_id)

            provided_interfaces = []
            required_interfaces = []
            dependencies = []
            used_by = []

            for conn in connectors:
                if conn.connector_type == 'Realisation' or conn.connector_type == 'Realization':
                    if conn.source_id == comp.object_id:
                        target = self.elements.get(conn.target_id)
                        if target and target.object_type == 'Interface':
                            provided_interfaces.append(target.name)
                elif conn.connector_type == 'Dependency':
                    if conn.source_id == comp.object_id:
                        target = self.elements.get(conn.target_id)
                        if target:
                            if target.object_type == 'Interface':
                                required_interfaces.append(target.name)
                            else:
                                dependencies.append(target.name)
                    elif conn.target_id == comp.object_id:
                        source = self.elements.get(conn.source_id)
                        if source:
                            used_by.append(source.name)

            if provided_interfaces or required_interfaces:
                comp_content += "## Interfaces\n\n"

                if provided_interfaces:
                    comp_content += "### Provided Interfaces\n\n"
                    for iface in provided_interfaces:
                        comp_content += f"- {iface}\n"
                    comp_content += "\n"

                if required_interfaces:
                    comp_content += "### Required Interfaces\n\n"
                    for iface in required_interfaces:
                        comp_content += f"- {iface}\n"
                    comp_content += "\n"

            if dependencies or used_by:
                comp_content += "## Dependencies\n\n"

                if dependencies:
                    comp_content += f"**Depends on:** {', '.join(dependencies)}\n\n"

                if used_by:
                    comp_content += f"**Used by:** {', '.join(used_by)}\n\n"

            # Add attributes if any
            if comp.object_id in self.attributes:
                attrs = self.attributes[comp.object_id]
                comp_content += "## Attributes\n\n"
                comp_content += "| Name | Type | Visibility | Default | Static |\n"
                comp_content += "|------|------|------------|---------|--------|\n"

                for attr in attrs:
                    static_flag = 'Yes' if attr.is_static else 'No'
                    comp_content += f"| {attr.name} | {attr.attr_type} | {attr.scope} | {attr.default or '-'} | {static_flag} |\n"

                comp_content += "\n"

            # Add operations if any
            if comp.object_id in self.operations:
                ops = self.operations[comp.object_id]
                comp_content += "## Operations\n\n"
                comp_content += "| Name | Parameters | Return Type | Visibility |\n"
                comp_content += "|------|------------|-------------|------------|\n"

                for op in ops:
                    params_str = ', '.join([f"{name}: {ptype}" for name, ptype in op.parameters]) or '-'
                    comp_content += f"| {op.name} | {params_str} | {op.return_type} | {op.scope} |\n"

                comp_content += "\n"

            with open(comp_dir / comp_filename, 'w') as f:
                f.write(comp_content)

        # Generate interfaces catalog
        if self.interfaces:
            interfaces_content = "# Interfaces\n\n"
            interfaces_content += "This document lists all interfaces in the system.\n\n"

            for iface in self.interfaces:
                interfaces_content += f"## {iface.name}\n\n"

                if iface.stereotype:
                    interfaces_content += f"**Stereotype:** <<{iface.stereotype}>>\n\n"

                interfaces_content += f"**Package:** {iface.package_name}\n\n"
                interfaces_content += f"**Description:** {iface.clean_note() or 'No description available'}\n\n"

                # Add operations
                if iface.object_id in self.operations:
                    ops = self.operations[iface.object_id]
                    interfaces_content += "### Methods\n\n"
                    interfaces_content += "| Name | Parameters | Return Type |\n"
                    interfaces_content += "|------|------------|-------------|\n"

                    for op in ops:
                        params_str = ', '.join([f"{name}: {ptype}" for name, ptype in op.parameters]) or '-'
                        interfaces_content += f"| {op.name} | {params_str} | {op.return_type} |\n"

                    interfaces_content += "\n"

                interfaces_content += "---\n\n"

            with open(comp_dir / 'interfaces.md', 'w') as f:
                f.write(interfaces_content)

        with open(comp_dir / 'index.md', 'w') as f:
            f.write(comp_index_content)

        logger.info(f"Generated documentation for {len(self.components)} components")

    def generate_class_docs(self):
        """Generate class and module documentation"""
        logger.info("Generating class documentation...")

        class_dir = self.output_dir / 'classes'
        class_dir.mkdir(exist_ok=True)

        # Group classes by package
        classes_by_package = defaultdict(list)
        for cls in self.classes:
            classes_by_package[cls.package_name].append(cls)

        class_index_content = "# Classes and Modules\n\n"
        class_index_content += "This document provides an overview of all classes in the system.\n\n"
        class_index_content += "## Packages\n\n"

        for package_name, classes in sorted(classes_by_package.items()):
            package_dir = class_dir / package_name.lower().replace(' ', '-')
            package_dir.mkdir(exist_ok=True)

            class_index_content += f"### {package_name}\n\n"

            for cls in sorted(classes, key=lambda x: x.name):
                class_filename = f"{cls.name.lower().replace(' ', '-')}.md"
                class_index_content += f"- [{cls.name}]({package_name.lower().replace(' ', '-')}/{class_filename})\n"

                class_content = f"# Class: {cls.name}\n\n"

                if cls.stereotype:
                    class_content += f"**Stereotype:** <<{cls.stereotype}>>\n\n"

                class_content += f"**Package:** {cls.package_name}\n\n"
                class_content += f"**Visibility:** {cls.visibility}\n\n"
                class_content += f"**Description:** {cls.clean_note() or 'No description available'}\n\n"

                # Get inheritance and relationships
                connectors = self.get_connectors_for_element(cls.object_id)

                inherits_from = []
                implements = []
                associations = []
                dependencies = []

                for conn in connectors:
                    if conn.connector_type == 'Generalization':
                        if conn.source_id == cls.object_id:
                            target = self.elements.get(conn.target_id)
                            if target:
                                inherits_from.append(target.name)
                    elif conn.connector_type == 'Realisation' or conn.connector_type == 'Realization':
                        if conn.source_id == cls.object_id:
                            target = self.elements.get(conn.target_id)
                            if target and target.object_type == 'Interface':
                                implements.append(target.name)
                    elif conn.connector_type in ['Association', 'Aggregation', 'Composition']:
                        if conn.source_id == cls.object_id:
                            target = self.elements.get(conn.target_id)
                            if target:
                                card = f" ({conn.target_card})" if conn.target_card else ""
                                role = f" - {conn.target_role}" if conn.target_role else ""
                                associations.append(f"{target.name}{card}{role} [{conn.connector_type}]")
                        elif conn.target_id == cls.object_id:
                            source = self.elements.get(conn.source_id)
                            if source:
                                card = f" ({conn.source_card})" if conn.source_card else ""
                                role = f" - {conn.source_role}" if conn.source_role else ""
                                associations.append(f"{source.name}{card}{role} [{conn.connector_type}]")
                    elif conn.connector_type == 'Dependency':
                        if conn.source_id == cls.object_id:
                            target = self.elements.get(conn.target_id)
                            if target:
                                dependencies.append(target.name)

                # Attributes section
                if cls.object_id in self.attributes:
                    attrs = self.attributes[cls.object_id]
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
                if cls.object_id in self.operations:
                    ops = self.operations[cls.object_id]
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

                with open(package_dir / class_filename, 'w') as f:
                    f.write(class_content)

            class_index_content += "\n"

        # Generate enumerations documentation
        if self.enumerations:
            class_index_content += "## Enumerations\n\n"

            for enum in self.enumerations:
                enum_content = f"### {enum.name}\n\n"
                enum_content += f"**Package:** {enum.package_name}\n\n"
                enum_content += f"**Description:** {enum.clean_note() or 'No description available'}\n\n"

                if enum.object_id in self.attributes:
                    attrs = self.attributes[enum.object_id]
                    enum_content += "**Values:**\n\n"
                    for attr in attrs:
                        default = f" = {attr.default}" if attr.default else ""
                        enum_content += f"- {attr.name}{default}\n"
                    enum_content += "\n"

                class_index_content += enum_content

        with open(class_dir / 'index.md', 'w') as f:
            f.write(class_index_content)

        logger.info(f"Generated documentation for {len(self.classes)} classes")

    def perform_quality_checks(self):
        """Perform quality checks on the model"""
        logger.info("Performing quality checks...")

        min_desc_length = self.config.get('quality_checks', {}).get('min_description_length', 20)

        for element in self.elements.values():
            # Check for undocumented elements
            desc = element.clean_note()
            if not desc or len(desc) < min_desc_length:
                self.quality_metrics['undocumented'].append({
                    'name': element.name,
                    'type': element.object_type,
                    'package': element.package_name
                })

        logger.info("Quality checks complete")

    def generate_quality_report(self):
        """Generate quality report"""
        logger.info("Generating quality report...")

        report_dir = self.output_dir / 'reports'
        report_dir.mkdir(exist_ok=True)

        report_content = "# Documentation Quality Report\n\n"
        report_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
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
        report_content += f"- Use Cases: {len(self.use_cases)}\n"
        report_content += f"- Actors: {len(self.actors)}\n"
        report_content += f"- State Machines: {len(self.state_machines)}\n"
        report_content += f"- Components: {len(self.components)}\n"
        report_content += f"- Classes: {len(self.classes)}\n"
        report_content += f"- Interfaces: {len(self.interfaces)}\n"
        report_content += f"- Enumerations: {len(self.enumerations)}\n"
        report_content += f"- Total Relationships: {len(self.connectors)}\n"

        documentation_rate = ((self.quality_metrics['total_elements'] - len(undoc)) /
                             self.quality_metrics['total_elements'] * 100) if self.quality_metrics['total_elements'] > 0 else 0
        report_content += f"\n**Documentation Rate:** {documentation_rate:.1f}%\n"

        with open(report_dir / 'quality-report.md', 'w') as f:
            f.write(report_content)

        logger.info("Quality report generated")

    def generate_dependencies_report(self):
        """Generate dependencies analysis report"""
        logger.info("Generating dependencies report...")

        report_dir = self.output_dir / 'reports'
        report_dir.mkdir(exist_ok=True)

        report_content = "# Dependency Analysis\n\n"
        report_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Analyze dependency connectors
        dep_connectors = [c for c in self.connectors if c.connector_type == 'Dependency']

        report_content += f"## Total Dependencies: {len(dep_connectors)}\n\n"

        if dep_connectors:
            report_content += "| Source | Target | Type |\n"
            report_content += "|--------|--------|------|\n"

            for conn in dep_connectors:
                source = self.elements.get(conn.source_id)
                target = self.elements.get(conn.target_id)
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
                source = self.elements.get(conn.source_id)
                target = self.elements.get(conn.target_id)
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

        with open(report_dir / 'dependencies.md', 'w') as f:
            f.write(report_content)

        logger.info("Dependencies report generated")

    def generate_index(self):
        """Generate main index/navigation document"""
        logger.info("Generating main index...")

        index_content = "# Sparx Enterprise Architect Model Documentation\n\n"
        index_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        index_content += f"**Source:** {self.qea_path.name}\n\n"

        index_content += "## Overview\n\n"
        index_content += "This documentation was automatically generated from the Sparx Enterprise Architect model. "
        index_content += "Navigate through the sections below to explore different aspects of the system architecture.\n\n"

        index_content += "## Documentation Sections\n\n"

        if self.use_cases:
            index_content += f"### [Use Cases](use-cases/index.md)\n\n"
            index_content += f"Contains {len(self.use_cases)} use cases and {len(self.actors)} actors describing "
            index_content += "system functionality and user interactions.\n\n"

        if self.state_machines:
            index_content += f"### [State Machines](state-machines/index.md)\n\n"
            index_content += f"Contains {len(self.state_machines)} state machines documenting system states "
            index_content += "and transitions.\n\n"

        if self.components:
            index_content += f"### [Components](components/index.md)\n\n"
            index_content += f"Contains {len(self.components)} components and their interfaces, "
            index_content += "showing system architecture and component interactions.\n\n"

        if self.classes:
            index_content += f"### [Classes and Modules](classes/index.md)\n\n"
            index_content += f"Contains {len(self.classes)} classes, {len(self.interfaces)} interfaces, "
            index_content += f"and {len(self.enumerations)} enumerations documenting the domain model.\n\n"

        index_content += "### Reports\n\n"
        index_content += "- [Quality Report](reports/quality-report.md) - Documentation quality metrics\n"
        index_content += "- [Dependency Analysis](reports/dependencies.md) - System dependencies and relationships\n\n"

        index_content += "## Model Statistics\n\n"
        index_content += f"- **Total Elements:** {self.quality_metrics['total_elements']}\n"
        index_content += f"- **Total Packages:** {len(self.packages)}\n"
        index_content += f"- **Total Relationships:** {len(self.connectors)}\n"

        with open(self.output_dir / 'index.md', 'w') as f:
            f.write(index_content)

        logger.info("Main index generated")

    def generate_documentation(self):
        """Generate all markdown documentation"""
        logger.info("Starting documentation generation...")

        self.generate_use_case_docs()
        self.generate_state_machine_docs()
        self.generate_component_docs()
        self.generate_class_docs()
        self.perform_quality_checks()
        self.generate_quality_report()
        self.generate_dependencies_report()
        self.generate_index()

        logger.info("Documentation generation complete!")

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
                self.connect_db()
                try:
                    self.analyze_schema()
                finally:
                    self.close_db()
                logger.info("Schema analysis complete")
                return

            # Full extraction and documentation
            self.extract_model_data()
            self.generate_documentation()

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
        config=config
    )

    generator.run(analyze_schema_only=args.analyze_schema)


if __name__ == '__main__':
    main()
