"""
Diagram rendering module for Sparx Enterprise Architect diagrams.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import graphviz

logger = logging.getLogger(__name__)


class DiagramRenderer:
    """Renders Sparx EA diagrams to PNG using Graphviz"""

    def __init__(self, extractor, output_dir: Path):
        """
        Initialize the diagram renderer

        Args:
            extractor: SparxExtractor instance with database connection
            output_dir: Output directory for rendered diagrams
        """
        self.extractor = extractor
        self.output_dir = output_dir
        self.diagrams_dir = output_dir / 'diagrams'
        self.diagrams_dir.mkdir(exist_ok=True)

    def render_diagram(self, diagram_id: int, diagram_name: str) -> Path:
        """
        Render a single diagram to PNG

        Args:
            diagram_id: The diagram ID from t_diagram table
            diagram_name: The name of the diagram

        Returns:
            Path to the generated PNG file
        """
        logger.info(f"Rendering diagram: {diagram_name} (ID: {diagram_id})")

        # Get diagram properties to check what to display
        diagram_props = self._get_diagram_properties(diagram_id)

        # Get diagram objects and connectors
        objects = self._get_diagram_objects(diagram_id)
        connectors = self._get_diagram_connectors(diagram_id)

        # Enrich objects with attributes and operations if needed
        if not diagram_props.get('hide_attributes', False) or not diagram_props.get('hide_operations', False):
            self._enrich_objects_with_features(objects, diagram_props)

        # Create Graphviz graph using neato for absolute positioning
        dot = graphviz.Digraph(comment=diagram_name, engine='neato')
        dot.attr(overlap='false', splines='true')
        dot.attr('node', shape='box', style='filled', fillcolor='lightblue',
                 fontname='Arial', fontsize='10')
        dot.attr('edge', fontname='Arial', fontsize='9')

        # Add nodes with positions from EA
        for obj_id, obj_data in objects.items():
            label = self._format_node_label(obj_data, diagram_props)
            shape, fillcolor = self._get_node_style(obj_data['object_type'])

            # Get position and size from EA coordinates
            pos_str = self._calculate_position(obj_data)
            width = obj_data['width'] / 72.0  # Convert to inches
            height = obj_data['height'] / 72.0  # Convert to inches

            dot.node(str(obj_id), label=label, shape=shape, fillcolor=fillcolor,
                    pos=pos_str, width=str(width), height=str(height), fixedsize='true')

        # Add edges
        for conn in connectors:
            edge_label = self._format_edge_label(conn)
            edge_style = self._get_edge_style(conn['connector_type'])

            dot.edge(str(conn['source_id']), str(conn['target_id']),
                    label=edge_label, **edge_style)

        # Render to PNG
        filename_base = diagram_name.lower().replace(' ', '_')
        output_path = self.diagrams_dir / filename_base

        try:
            dot.render(output_path, format='png', cleanup=True)
            png_file = Path(f"{output_path}.png")
            logger.info(f"Diagram rendered successfully: {png_file}")
            return png_file
        except Exception as e:
            logger.error(f"Failed to render diagram {diagram_name}: {e}")
            raise

    def _get_diagram_objects(self, diagram_id: int) -> Dict:
        """Get all objects in a diagram with position information"""
        cursor = self.extractor.conn.cursor()

        cursor.execute("""
            SELECT do.Object_ID, o.Name, o.Object_Type, o.Stereotype,
                   do.RectLeft, do.RectTop, do.RectRight, do.RectBottom
            FROM t_diagramobjects do
            JOIN t_object o ON do.Object_ID = o.Object_ID
            WHERE do.Diagram_ID = ?
            ORDER BY do.Sequence
        """, (diagram_id,))

        objects = {}
        for row in cursor.fetchall():
            left = row['RectLeft']
            top = row['RectTop']
            right = row['RectRight']
            bottom = row['RectBottom']

            objects[row['Object_ID']] = {
                'name': row['Name'],
                'object_type': row['Object_Type'],
                'stereotype': row['Stereotype'] or '',
                'left': left,
                'top': top,
                'right': right,
                'bottom': bottom,
                'width': abs(right - left),
                'height': abs(bottom - top)
            }

        return objects

    def _get_diagram_connectors(self, diagram_id: int) -> List[Dict]:
        """Get all connectors in a diagram"""
        cursor = self.extractor.conn.cursor()

        cursor.execute("""
            SELECT c.Connector_ID, c.Connector_Type, c.Start_Object_ID, c.End_Object_ID,
                   c.SourceCard, c.DestCard, c.SourceRole, c.DestRole, c.Name
            FROM t_diagramlinks dl
            JOIN t_connector c ON dl.ConnectorID = c.Connector_ID
            WHERE dl.DiagramID = ?
        """, (diagram_id,))

        connectors = []
        for row in cursor.fetchall():
            connectors.append({
                'connector_id': row['Connector_ID'],
                'connector_type': row['Connector_Type'],
                'source_id': row['Start_Object_ID'],
                'target_id': row['End_Object_ID'],
                'source_card': row['SourceCard'] or '',
                'target_card': row['DestCard'] or '',
                'source_role': row['SourceRole'] or '',
                'target_role': row['DestRole'] or '',
                'name': row['Name'] or ''
            })

        return connectors

    def _calculate_position(self, obj_data: Dict) -> str:
        """
        Calculate Graphviz position from EA coordinates

        EA coordinates:
        - Origin appears to be top-left
        - X increases right (positive values)
        - Y is negative at top, less negative going down
        - More negative Y = higher up in diagram

        Graphviz neato coordinates:
        - Origin at bottom-left
        - X increases right, Y increases up
        - Units in points (1/72 inch)
        - Append "!" to fix position
        """
        # Calculate center position
        center_x = (obj_data['left'] + obj_data['right']) / 2.0
        center_y = (obj_data['top'] + obj_data['bottom']) / 2.0

        # Scale factor to convert EA units to points (adjust as needed)
        scale = 1.0

        x_pos = center_x * scale
        # Don't invert Y - EA coordinates work directly with Graphviz
        # (more negative Y in EA = lower Y in Graphviz = higher in visual output)
        y_pos = center_y * scale

        # Return position with "!" to fix it
        return f"{x_pos},{y_pos}!"

    def _format_node_label(self, obj_data: Dict, diagram_props: Dict) -> str:
        """Format node label for Graphviz with optional attributes and operations"""
        # Check if this is an actor - use stick figure
        if obj_data['object_type'] == 'Actor':
            # Use Unicode stick figure character
            stick_figure = "🧍"  # Standing person emoji
            label = f"{stick_figure}\n{obj_data['name']}"
            if obj_data['stereotype']:
                label = f"<<{obj_data['stereotype']}>>\n{label}"
            return label

        # Check if this is a class-like object
        is_class = obj_data['object_type'] in ('Class', 'Interface', 'Enumeration')

        # Build HTML-like label for structured display
        if is_class and ('attributes' in obj_data or 'operations' in obj_data):
            parts = ['<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">']

            # Header with stereotype and name
            if obj_data['stereotype']:
                parts.append(f'<TR><TD>&lt;&lt;{obj_data["stereotype"]}&gt;&gt;</TD></TR>')
            parts.append(f'<TR><TD><B>{obj_data["name"]}</B></TD></TR>')

            # Attributes section
            if not diagram_props.get('hide_attributes', False) and 'attributes' in obj_data:
                attrs = obj_data['attributes']
                if attrs:
                    parts.append('<TR><TD ALIGN="LEFT">')
                    for attr in attrs[:5]:  # Limit to first 5 to avoid huge boxes
                        parts.append(f'{attr}<BR/>')
                    if len(attrs) > 5:
                        parts.append('...<BR/>')
                    parts.append('</TD></TR>')

            # Operations section
            if not diagram_props.get('hide_operations', False) and 'operations' in obj_data:
                ops = obj_data['operations']
                if ops:
                    parts.append('<TR><TD ALIGN="LEFT">')
                    for op in ops[:5]:  # Limit to first 5
                        parts.append(f'{op}<BR/>')
                    if len(ops) > 5:
                        parts.append('...<BR/>')
                    parts.append('</TD></TR>')

            parts.append('</TABLE>>')
            return ''.join(parts)
        else:
            # Simple label for non-class objects or when features are hidden
            label = obj_data['name']
            if obj_data['stereotype']:
                label = f"<<{obj_data['stereotype']}>>\n{label}"
            return label

    def _get_node_style(self, object_type: str) -> Tuple[str, str]:
        """Get node shape and fill color based on object type"""
        styles = {
            'Class': ('box', 'lightblue'),
            'Interface': ('box', 'lightyellow'),
            'Enumeration': ('box', 'lightgray'),
            'Component': ('component', 'lightgreen'),
            'Actor': ('plaintext', 'none'),  # Stick figure representation
            'UseCase': ('ellipse', 'lightcyan'),
        }

        return styles.get(object_type, ('box', 'white'))

    def _format_edge_label(self, conn: Dict) -> str:
        """Format edge label with cardinality and role information"""
        parts = []

        if conn['name']:
            parts.append(conn['name'])

        if conn['source_card'] or conn['target_card']:
            card = f"{conn['source_card'] or '*'}..{conn['target_card'] or '*'}"
            parts.append(card)

        if conn['source_role'] or conn['target_role']:
            if conn['source_role']:
                parts.append(f"from: {conn['source_role']}")
            if conn['target_role']:
                parts.append(f"to: {conn['target_role']}")

        return '\n'.join(parts) if parts else ''

    def _get_edge_style(self, connector_type: str) -> Dict:
        """Get edge style based on connector type"""
        styles = {
            'Generalization': {'arrowhead': 'empty', 'style': 'solid'},
            'Realisation': {'arrowhead': 'empty', 'style': 'dashed'},
            'Realization': {'arrowhead': 'empty', 'style': 'dashed'},
            'Association': {'arrowhead': 'none', 'dir': 'both', 'arrowtail': 'none'},
            'Aggregation': {'arrowhead': 'odiamond', 'style': 'solid'},
            'Composition': {'arrowhead': 'diamond', 'style': 'solid'},
            'Dependency': {'arrowhead': 'vee', 'style': 'dashed'},
        }

        return styles.get(connector_type, {'arrowhead': 'normal', 'style': 'solid'})

    def _get_diagram_properties(self, diagram_id: int) -> Dict:
        """Get diagram display properties from PDATA field"""
        cursor = self.extractor.conn.cursor()

        cursor.execute("""
            SELECT ShowDetails, PDATA
            FROM t_diagram
            WHERE Diagram_ID = ?
        """, (diagram_id,))

        row = cursor.fetchone()
        if not row:
            return {'hide_attributes': True, 'hide_operations': True}

        # Parse PDATA field which contains semicolon-separated key=value pairs
        pdata_dict = {}
        if row['PDATA']:
            for item in row['PDATA'].split(';'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    pdata_dict[key] = value

        # HideAtts=0 means show attributes, HideAtts=1 means hide
        # Get from PDATA dict, default to showing (0)
        hide_attributes = int(pdata_dict.get('HideAtts', '0')) == 1
        hide_operations = int(pdata_dict.get('HideOps', '0')) == 1

        return {
            'hide_attributes': hide_attributes,
            'hide_operations': hide_operations,
            'show_details': row['ShowDetails'] == 1 if row['ShowDetails'] is not None else False,
            'pdata': pdata_dict
        }

    def _enrich_objects_with_features(self, objects: Dict, diagram_props: Dict) -> None:
        """Add attributes and operations to objects based on diagram properties"""
        for obj_id, obj_data in objects.items():
            # Only add features for class-like objects
            if obj_data['object_type'] not in ('Class', 'Interface', 'Enumeration'):
                continue

            # Fetch attributes if not hidden
            if not diagram_props.get('hide_attributes', False):
                attributes = self._get_object_attributes(obj_id)
                obj_data['attributes'] = attributes

            # Fetch operations if not hidden
            if not diagram_props.get('hide_operations', False):
                operations = self._get_object_operations(obj_id)
                obj_data['operations'] = operations

    def _get_object_attributes(self, object_id: int) -> List[str]:
        """Get formatted attributes for an object"""
        cursor = self.extractor.conn.cursor()

        cursor.execute("""
            SELECT Name, Type, Scope
            FROM t_attribute
            WHERE Object_ID = ?
            ORDER BY Pos
        """, (object_id,))

        attributes = []
        for row in cursor.fetchall():
            # Format: name: type
            attr_type = row['Type'] or ''
            attr_str = f"{row['Name']}: {attr_type}" if attr_type else row['Name']
            attributes.append(attr_str)

        return attributes

    def _get_object_operations(self, object_id: int) -> List[str]:
        """Get formatted operations for an object"""
        cursor = self.extractor.conn.cursor()

        cursor.execute("""
            SELECT Name, Type, Scope
            FROM t_operation
            WHERE Object_ID = ?
            ORDER BY Pos
        """, (object_id,))

        operations = []
        for row in cursor.fetchall():
            # Format: name(): returnType
            return_type = row['Type'] or ''
            op_str = f"{row['Name']}(): {return_type}" if return_type else f"{row['Name']}()"
            operations.append(op_str)

        return operations

    def render_all_diagrams(self) -> List[Tuple[str, Path]]:
        """
        Render all diagrams in the model

        Returns:
            List of tuples (diagram_name, png_path)
        """
        cursor = self.extractor.conn.cursor()

        cursor.execute("""
            SELECT d.Diagram_ID, d.Name, d.Diagram_Type, p.Name as Package
            FROM t_diagram d
            LEFT JOIN t_package p ON d.Package_ID = p.Package_ID
            ORDER BY p.Name, d.Name
        """)

        rendered_diagrams = []
        for row in cursor.fetchall():
            diagram_id = row['Diagram_ID']
            diagram_name = row['Name']

            try:
                png_path = self.render_diagram(diagram_id, diagram_name)
                rendered_diagrams.append((diagram_name, png_path))
            except Exception as e:
                logger.warning(f"Skipping diagram {diagram_name}: {e}")
                continue

        logger.info(f"Rendered {len(rendered_diagrams)} diagrams")
        return rendered_diagrams
