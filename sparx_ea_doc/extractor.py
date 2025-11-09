"""
Database extraction module for Sparx Enterprise Architect .qea files.
"""

import sqlite3
import logging
import html
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Dict, List, Optional
from pathlib import Path

from .models import Element, Attribute, Operation, Connector, Scenario, Constraint, Requirement

logger = logging.getLogger(__name__)


class SparxExtractor:
    """Handles extraction of data from Sparx EA SQLite database"""

    def __init__(self, qea_path: Path):
        """
        Initialize the extractor

        Args:
            qea_path: Path to the .qea SQLite database file
        """
        self.qea_path = qea_path
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
        self.requirements: List[Requirement] = []
        self.attributes: Dict[int, List[Attribute]] = defaultdict(list)
        self.operations: Dict[int, List[Operation]] = defaultdict(list)
        self.connectors: List[Connector] = []
        self.scenarios: Dict[int, List[Scenario]] = defaultdict(list)
        self.constraints: Dict[int, List[Constraint]] = defaultdict(list)
        self.packages: Dict[int, str] = {}

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
                   o.Version, o.ModifiedDate, o.ea_guid,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type = 'UseCase'
            ORDER BY o.Object_ID
        """)

        for row in cursor.fetchall():
            element = Element(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type='UseCase',
                note=row['Note'] or '',
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public',
                version=row['Version'] or '',
                modified_date=row['ModifiedDate'] or '',
                guid=row['ea_guid'] or ''
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
            ORDER BY o.Object_ID
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

        # Extract state machine diagrams (these are the main organizational units)
        cursor.execute("""
            SELECT d.Diagram_ID, d.Name, d.Notes, d.Package_ID,
                   p.Name as Package
            FROM t_diagram d
            LEFT JOIN t_package p ON d.Package_ID = p.Package_ID
            WHERE d.Diagram_Type = 'Statechart'
            ORDER BY d.Name
        """)

        diagram_to_sm = {}
        for row in cursor.fetchall():
            # Create a pseudo-element for the state machine diagram
            element = Element(
                object_id=row['Diagram_ID'],  # Using diagram ID as object ID
                name=row['Name'],
                object_type='StateMachine',
                note=row['Notes'] or '',
                stereotype='',
                package_name=row['Package'] or 'Unknown',
                visibility='public'
            )
            self.state_machines.append(element)
            diagram_to_sm[row['Diagram_ID']] = element
            # Note: Not adding to self.elements since Diagram_ID != Object_ID

        # Extract objects on each state machine diagram
        cursor.execute("""
            SELECT do.Diagram_ID, do.Object_ID,
                   o.Name, o.Note, o.Stereotype, o.Scope, o.Object_Type, o.ParentID,
                   p.Name as Package
            FROM t_diagramobjects do
            JOIN t_diagram d ON do.Diagram_ID = d.Diagram_ID
            JOIN t_object o ON do.Object_ID = o.Object_ID
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE d.Diagram_Type = 'Statechart'
            ORDER BY do.Diagram_ID, o.Name
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

            # Group states by their diagram
            diagram_id = row['Diagram_ID']
            self.states[diagram_id].append(element)
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
                   o.[Abstract], o.Version, o.ModifiedDate, o.ea_guid,
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
                visibility=row['Scope'] or 'public',
                version=row['Version'] or '',
                modified_date=row['ModifiedDate'] or '',
                guid=row['ea_guid'] or ''
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
            SELECT Object_ID, Name, [Type], Scope, [Default], Notes,
                   IsStatic, Const, Pos
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
                is_const=bool(row['Const']),
                pos=row['Pos'] or 0
            )
            self.attributes[row['Object_ID']].append(attr)

        logger.info(f"Extracted attributes for {len(self.attributes)} objects")

    def extract_operations(self):
        """Extract operations/methods for classes and components"""
        logger.info("Extracting operations...")
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT OperationID, Object_ID, Name, [Type], Scope,
                   [Abstract], IsStatic, Notes
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
            SELECT OperationID, Name, [Type], Kind
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
                   c.Notes, c.PDATA1, c.PDATA2,
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
                notes=row['Notes'] or '',
                trigger=row['PDATA1'] or '',
                guard=row['PDATA2'] or ''
            )
            self.connectors.append(connector)

        logger.info(f"Extracted {len(self.connectors)} connectors")

    def extract_scenarios(self):
        """Extract scenarios for use cases"""
        logger.info("Extracting scenarios...")
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT Object_ID, Scenario, ScenarioType, Notes, XMLContent, ea_guid
            FROM t_objectscenarios
            ORDER BY Object_ID, Scenario
        """)

        for row in cursor.fetchall():
            object_id = row['Object_ID']
            scenario_name = row['Scenario']
            scenario_type = row['ScenarioType']
            notes = row['Notes'] or ''
            xml_content = row['XMLContent']
            ea_guid = row['ea_guid'] or ''

            steps = []
            extensions = []
            if xml_content:
                try:
                    # Parse XML to extract steps and extensions
                    root = ET.fromstring(xml_content)
                    step_index = 0
                    for step_elem in root.findall('step'):  # Direct children only
                        step_name = step_elem.get('name', '')
                        if step_name:
                            # Decode HTML entities in step name
                            step_name = html.unescape(step_name)
                            steps.append(step_name)

                            # Check for extension elements
                            for ext_elem in step_elem.findall('extension'):
                                ext_level = ext_elem.get('level', '')
                                ext_guid = ext_elem.get('guid', '')
                                if ext_level and ext_guid:
                                    extensions.append((step_index, ext_level, ext_guid))

                            step_index += 1
                except ET.ParseError as e:
                    logger.warning(f"Failed to parse XML for scenario '{scenario_name}': {e}")

            scenario = Scenario(
                name=scenario_name,
                scenario_type=scenario_type,
                steps=steps,
                notes=notes,
                ea_guid=ea_guid,
                extensions=extensions
            )
            self.scenarios[object_id].append(scenario)

        total_scenarios = sum(len(scenarios) for scenarios in self.scenarios.values())
        logger.info(f"Extracted {total_scenarios} scenarios for {len(self.scenarios)} objects")

    def extract_constraints(self):
        """Extract constraints (pre-conditions, post-conditions, etc.)"""
        logger.info("Extracting constraints...")
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT Object_ID, [Constraint], ConstraintType, Notes
            FROM t_objectconstraint
            ORDER BY Object_ID, ConstraintType, [Constraint]
        """)

        for row in cursor.fetchall():
            object_id = row['Object_ID']
            constraint_name = row['Constraint']
            constraint_type = row['ConstraintType']
            notes = row['Notes'] or ''

            constraint = Constraint(
                name=constraint_name,
                constraint_type=constraint_type,
                notes=notes
            )
            self.constraints[object_id].append(constraint)

        total_constraints = sum(len(constraints) for constraints in self.constraints.values())
        logger.info(f"Extracted {total_constraints} constraints for {len(self.constraints)} objects")

    def extract_requirements(self):
        """Extract requirements and their relationships to use cases"""
        logger.info("Extracting requirements...")
        cursor = self.conn.cursor()

        # Extract requirement objects
        # Note: Priority is stored in Note field, Difficulty in Complexity field
        cursor.execute("""
            SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, o.Scope,
                   o.Version, o.ModifiedDate, o.ea_guid, o.Complexity, o.Status,
                   p.Name as Package
            FROM t_object o
            LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
            WHERE o.Object_Type = 'Requirement'
            ORDER BY o.Name
        """)

        requirements_dict = {}
        for row in cursor.fetchall():
            # In EA, priority is often stored in the Note field for requirements
            # If Note looks like a priority value (High, Medium, Low), treat it as such
            note = row['Note'] or ''
            priority = ''
            description = note

            # Check if note is a priority value
            if note.strip() in ['High', 'Medium', 'Low']:
                priority = note.strip()
                description = ''  # No separate description in this model

            requirement = Requirement(
                object_id=row['Object_ID'],
                name=row['Name'],
                object_type='Requirement',
                note=description,
                stereotype=row['Stereotype'] or '',
                package_name=row['Package'] or 'Unknown',
                visibility=row['Scope'] or 'public',
                version=row['Version'] or '',
                modified_date=row['ModifiedDate'] or '',
                guid=row['ea_guid'] or '',
                priority=priority,
                difficulty=row['Complexity'] or '',
                status=row['Status'] or '',
                related_use_cases=[]
            )
            self.requirements.append(requirement)
            self.elements[requirement.object_id] = requirement
            requirements_dict[requirement.object_id] = requirement

        # Extract relationships between requirements and use cases via connectors
        cursor.execute("""
            SELECT c.Start_Object_ID, c.End_Object_ID, c.Connector_Type,
                   src.Name as SourceName, src.Object_Type as SourceType,
                   dest.Name as DestName, dest.Object_Type as DestType
            FROM t_connector c
            JOIN t_object src ON c.Start_Object_ID = src.Object_ID
            JOIN t_object dest ON c.End_Object_ID = dest.Object_ID
            WHERE (src.Object_Type = 'Requirement' AND dest.Object_Type = 'UseCase')
               OR (src.Object_Type = 'UseCase' AND dest.Object_Type = 'Requirement')
        """)

        for row in cursor.fetchall():
            source_id = row['Start_Object_ID']
            target_id = row['End_Object_ID']
            source_type = row['SourceType']
            target_type = row['DestType']

            # Determine which is the requirement and which is the use case
            if source_type == 'Requirement':
                req_id = source_id
                uc_name = row['DestName']
            else:
                req_id = target_id
                uc_name = row['SourceName']

            # Add use case to requirement's related list
            if req_id in requirements_dict:
                if uc_name not in requirements_dict[req_id].related_use_cases:
                    requirements_dict[req_id].related_use_cases.append(uc_name)

        logger.info(f"Extracted {len(self.requirements)} requirements")

    def extract_all(self):
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
            self.extract_scenarios()
            self.extract_constraints()
            self.extract_requirements()

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
