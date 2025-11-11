"""
Diagram rendering module for Sparx Enterprise Architect diagrams.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import graphviz
from PIL import Image, ImageDraw, ImageFont

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

    def render_diagram(self, diagram_id: int, diagram_name: str, package_name: str = None) -> Path:
        """
        Render a single diagram to PNG with pixel-perfect layout

        Args:
            diagram_id: The diagram ID from t_diagram table
            diagram_name: The name of the diagram
            package_name: The package this diagram belongs to (ignored for now)

        Returns:
            Path to the generated PNG file
        """
        logger.info(f"Rendering diagram: {diagram_name} (ID: {diagram_id})")

        # Use PIL-based pixel-perfect rendering for all diagrams
        return self._render_diagram_pil(diagram_id, diagram_name)

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

    def _calculate_position(self, obj_data: Dict, diagram_dims: Dict) -> str:
        """
        Calculate Graphviz position from EA coordinates for pixel-perfect layout

        EA coordinates:
        - Origin at top-left (0, 0)
        - X increases right (positive values)
        - Y is negative, with more negative = higher up in diagram
        - Units are in pixels

        Graphviz neato coordinates:
        - Origin at bottom-left
        - X increases right, Y increases up
        - Units in points (1/72 inch)
        - Append "!" to fix position

        For pixel-perfect rendering:
        - Convert EA pixels to inches (96 DPI)
        - Invert Y-axis (EA: negative up, Graphviz: positive up)
        """
        # Calculate center position in EA coordinates
        center_x = (obj_data['left'] + obj_data['right']) / 2.0
        center_y = (obj_data['top'] + obj_data['bottom']) / 2.0

        # EA Y coordinates are negative with more negative being higher up
        # We need to flip this so that higher Y means higher up in Graphviz
        # Transform: graphviz_y = -ea_y
        # This makes more negative EA values (like -778) become positive high values
        y_flipped = -center_y

        # Convert from pixels to inches at 96 DPI
        x_inches = center_x / 96.0
        y_inches = y_flipped / 96.0

        # Return position with "!" to fix it
        return f"{x_inches},{y_inches}!"

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

    def _get_diagram_dimensions(self, diagram_id: int) -> Dict:
        """Get diagram dimensions from EA"""
        cursor = self.extractor.conn.cursor()

        cursor.execute("""
            SELECT cx, cy, Scale
            FROM t_diagram
            WHERE Diagram_ID = ?
        """, (diagram_id,))

        row = cursor.fetchone()
        if not row:
            # Default dimensions if not found
            return {'width': 800, 'height': 600, 'scale': 100}

        return {
            'width': row['cx'] or 800,
            'height': row['cy'] or 600,
            'scale': row['Scale'] or 100
        }

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
            package_name = row['Package']

            try:
                png_path = self.render_diagram(diagram_id, diagram_name, package_name)
                rendered_diagrams.append((diagram_name, png_path))
            except Exception as e:
                logger.warning(f"Skipping diagram {diagram_name}: {e}")
                continue

        logger.info(f"Rendered {len(rendered_diagrams)} diagrams")
        return rendered_diagrams

    def _get_diagram_type(self, diagram_id: int) -> str:
        """Get the diagram type"""
        cursor = self.extractor.conn.cursor()
        cursor.execute("SELECT Diagram_Type FROM t_diagram WHERE Diagram_ID = ?", (diagram_id,))
        row = cursor.fetchone()
        return row['Diagram_Type'] if row else ''

    def _render_diagram_pil(self, diagram_id: int, diagram_name: str) -> Path:
        """
        Render diagram using PIL for pixel-perfect layout matching EA

        Args:
            diagram_id: The diagram ID
            diagram_name: The name of the diagram

        Returns:
            Path to the generated PNG file
        """
        # Get diagram dimensions
        diagram_dims = self._get_diagram_dimensions(diagram_id)
        diagram_props = self._get_diagram_properties(diagram_id)
        width = diagram_dims['width']
        height = diagram_dims['height']

        # Create white canvas
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)

        # Try to load decent fonts
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
            font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
        except:
            font = ImageFont.load_default()
            font_bold = font
            font_small = font

        # Get objects and connectors
        objects = self._get_diagram_objects(diagram_id)
        connectors = self._get_diagram_connectors(diagram_id)

        # Enrich objects with attributes and operations if needed
        if not diagram_props.get('hide_attributes', False) or not diagram_props.get('hide_operations', False):
            self._enrich_objects_with_features(objects, diagram_props)

        # Draw connectors first (so they appear behind shapes)
        self._draw_connectors_pil(draw, connectors, objects, font_small)

        # Draw objects
        fonts = {'normal': font, 'bold': font_bold, 'small': font_small}
        for obj_id, obj_data in objects.items():
            obj_type = obj_data['object_type']

            if obj_type == 'Actor':
                self._draw_actor_pil(draw, obj_data, font)
            elif obj_type == 'UseCase':
                self._draw_usecase_pil(draw, obj_data, font)
            elif obj_type in ('Class', 'Interface', 'Enumeration'):
                self._draw_class_pil(draw, obj_data, fonts, diagram_props)
            elif obj_type == 'Component':
                self._draw_component_pil(draw, obj_data, fonts)
            elif obj_type in ('State', 'StateNode', 'Pseudostate'):
                self._draw_state_pil(draw, obj_data, font)
            else:
                # Generic box for unknown types
                self._draw_box_pil(draw, obj_data, font)

        # Save to file in single diagrams directory
        filename_base = diagram_name.lower().replace(' ', '_')
        output_path = self.diagrams_dir / f"{filename_base}.png"
        image.save(output_path, 'PNG')

        logger.info(f"Diagram rendered successfully: {output_path}")
        return output_path

    def _draw_actor_pil(self, draw, obj_data: Dict, font):
        """Draw an actor as a stick figure"""
        # EA coordinates: Y is negative, more negative = higher up
        # We need to flip: display_y = -ea_y
        left = obj_data['left']
        right = obj_data['right']
        top = -obj_data['top']  # Flip Y
        bottom = -obj_data['bottom']  # Flip Y

        # Swap if needed (bottom should be > top in display coordinates)
        if top > bottom:
            top, bottom = bottom, top

        center_x = (left + right) // 2
        width = right - left
        height = bottom - top

        # Draw stick figure
        # Head (circle at top)
        head_radius = width // 4
        head_y = top + head_radius + 5
        draw.ellipse([center_x - head_radius, head_y - head_radius,
                     center_x + head_radius, head_y + head_radius],
                    outline='black', fill='white', width=2)

        # Body (vertical line)
        body_top = head_y + head_radius
        body_bottom = top + int(height * 0.6)
        draw.line([center_x, body_top, center_x, body_bottom], fill='black', width=2)

        # Arms (horizontal line)
        arm_y = body_top + int((body_bottom - body_top) * 0.3)
        arm_span = width // 2
        draw.line([center_x - arm_span, arm_y, center_x + arm_span, arm_y], fill='black', width=2)

        # Legs (two lines from body bottom)
        leg_span = width // 3
        leg_bottom = bottom - 15
        draw.line([center_x, body_bottom, center_x - leg_span, leg_bottom], fill='black', width=2)
        draw.line([center_x, body_bottom, center_x + leg_span, leg_bottom], fill='black', width=2)

        # Draw name below
        name = obj_data['name']
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = center_x - text_width // 2
        text_y = bottom - 10
        draw.text((text_x, text_y), name, fill='black', font=font)

    def _draw_usecase_pil(self, draw, obj_data: Dict, font):
        """Draw a use case as an ellipse"""
        # EA coordinates: Y is negative, more negative = higher up
        left = obj_data['left']
        right = obj_data['right']
        top = -obj_data['top']  # Flip Y
        bottom = -obj_data['bottom']  # Flip Y

        # Swap if needed
        if top > bottom:
            top, bottom = bottom, top

        # Draw ellipse
        draw.ellipse([left, top, right, bottom],
                    outline='black', fill='lightcyan', width=2)

        # Draw name in center
        name = obj_data['name']
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        center_x = (left + right) // 2
        center_y = (top + bottom) // 2

        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2

        draw.text((text_x, text_y), name, fill='black', font=font)

    def _draw_box_pil(self, draw, obj_data: Dict, font):
        """Draw a generic box"""
        left = obj_data['left']
        right = obj_data['right']
        top = -obj_data['top']
        bottom = -obj_data['bottom']

        if top > bottom:
            top, bottom = bottom, top

        draw.rectangle([left, top, right, bottom],
                      outline='black', fill='lightblue', width=2)

        # Draw name
        name = obj_data['name']
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        center_x = (left + right) // 2
        center_y = (top + bottom) // 2

        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2

        draw.text((text_x, text_y), name, fill='black', font=font)

    def _draw_class_pil(self, draw, obj_data: Dict, fonts: Dict, diagram_props: Dict):
        """Draw a class/interface/enumeration with compartments"""
        left = obj_data['left']
        right = obj_data['right']
        top = -obj_data['top']
        bottom = -obj_data['bottom']

        if top > bottom:
            top, bottom = bottom, top

        obj_type = obj_data['object_type']

        # Determine colors
        if obj_type == 'Interface':
            fill_color = (255, 255, 224)  # Light yellow
        elif obj_type == 'Enumeration':
            fill_color = (211, 211, 211)  # Light gray
        else:
            fill_color = (173, 216, 230)  # Light blue

        # Draw outer rectangle
        draw.rectangle([left, top, right, bottom],
                      outline='black', fill=fill_color, width=2)

        # Draw compartments
        y_pos = top + 5
        font = fonts['normal']
        font_bold = fonts['bold']
        font_small = fonts['small']

        # Stereotype if present
        if obj_data.get('stereotype'):
            stereotype_text = f"<<{obj_data['stereotype']}>>"
            bbox = draw.textbbox((0, 0), stereotype_text, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_x = (left + right) // 2 - text_width // 2
            draw.text((text_x, y_pos), stereotype_text, fill='black', font=font_small)
            y_pos += bbox[3] - bbox[1] + 3

        # Class name (bold)
        name = obj_data['name']
        bbox = draw.textbbox((0, 0), name, font=font_bold)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (left + right) // 2 - text_width // 2
        draw.text((text_x, y_pos), name, fill='black', font=font_bold)
        y_pos += text_height + 5

        # Separator line after name
        draw.line([left, y_pos, right, y_pos], fill='black', width=1)
        y_pos += 5

        # Attributes
        if not diagram_props.get('hide_attributes', False) and 'attributes' in obj_data:
            attrs = obj_data['attributes']
            for attr in attrs[:10]:  # Limit to 10
                draw.text((left + 5, y_pos), attr, fill='black', font=font_small)
                bbox = draw.textbbox((0, 0), attr, font=font_small)
                y_pos += bbox[3] - bbox[1] + 2
            if attrs:
                y_pos += 3
                draw.line([left, y_pos, right, y_pos], fill='black', width=1)
                y_pos += 5

        # Operations
        if not diagram_props.get('hide_operations', False) and 'operations' in obj_data:
            ops = obj_data['operations']
            for op in ops[:10]:  # Limit to 10
                draw.text((left + 5, y_pos), op, fill='black', font=font_small)
                bbox = draw.textbbox((0, 0), op, font=font_small)
                y_pos += bbox[3] - bbox[1] + 2

    def _draw_component_pil(self, draw, obj_data: Dict, fonts: Dict):
        """Draw a component"""
        left = obj_data['left']
        right = obj_data['right']
        top = -obj_data['top']
        bottom = -obj_data['bottom']

        if top > bottom:
            top, bottom = bottom, top

        # Draw main rectangle
        draw.rectangle([left, top, right, bottom],
                      outline='black', fill=(144, 238, 144), width=2)  # Light green

        # Draw component icon (two small rectangles on the left side)
        icon_width = 15
        icon_height = 8
        icon_x = left - icon_width
        icon_y1 = top + 10
        icon_y2 = top + 25

        draw.rectangle([icon_x, icon_y1, left, icon_y1 + icon_height],
                      outline='black', fill='white', width=1)
        draw.rectangle([icon_x, icon_y2, left, icon_y2 + icon_height],
                      outline='black', fill='white', width=1)

        # Draw name in center
        name = obj_data['name']
        font = fonts['bold']
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        center_x = (left + right) // 2
        center_y = (top + bottom) // 2

        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2

        draw.text((text_x, text_y), name, fill='black', font=font)

    def _draw_state_pil(self, draw, obj_data: Dict, font):
        """Draw a state machine state"""
        left = obj_data['left']
        right = obj_data['right']
        top = -obj_data['top']
        bottom = -obj_data['bottom']

        if top > bottom:
            top, bottom = bottom, top

        # Draw rounded rectangle for state
        radius = 10
        draw.rounded_rectangle([left, top, right, bottom],
                              radius=radius,
                              outline='black', fill=(255, 250, 205), width=2)  # Light yellow

        # Draw name at top
        name = obj_data['name']
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (left + right) // 2 - text_width // 2
        draw.text((text_x, top + 5), name, fill='black', font=font)

    def _draw_connectors_pil(self, draw, connectors: List[Dict], objects: Dict, font):
        """Draw connectors between objects"""
        for conn in connectors:
            source_id = conn['source_id']
            target_id = conn['target_id']

            if source_id not in objects or target_id not in objects:
                continue

            source = objects[source_id]
            target = objects[target_id]

            # Calculate center points
            src_x = (source['left'] + source['right']) // 2
            src_y = -(source['top'] + source['bottom']) // 2  # Flip Y

            tgt_x = (target['left'] + target['right']) // 2
            tgt_y = -(target['top'] + target['bottom']) // 2  # Flip Y

            # Determine line style based on connector type
            conn_type = conn['connector_type']

            # Draw line
            if conn_type in ('Dependency', 'Usage'):
                # Dashed line
                self._draw_dashed_line(draw, src_x, src_y, tgt_x, tgt_y)
            elif conn_type in ('Realisation', 'Realization'):
                # Dashed line for realization
                self._draw_dashed_line(draw, src_x, src_y, tgt_x, tgt_y)
            else:
                # Solid line for associations, generalizations, etc.
                draw.line([src_x, src_y, tgt_x, tgt_y], fill='black', width=1)

            # Draw arrowhead at target based on type
            if conn_type in ('Generalization', 'Realisation', 'Realization'):
                # Hollow triangle
                self._draw_triangle_arrow(draw, src_x, src_y, tgt_x, tgt_y, filled=False)
            elif conn_type == 'Aggregation':
                # Hollow diamond
                self._draw_diamond_arrow(draw, src_x, src_y, tgt_x, tgt_y, filled=False)
            elif conn_type == 'Composition':
                # Filled diamond
                self._draw_diamond_arrow(draw, src_x, src_y, tgt_x, tgt_y, filled=True)
            elif conn_type in ('Dependency', 'Usage'):
                # Simple arrow
                self._draw_arrow_head(draw, src_x, src_y, tgt_x, tgt_y)
            elif conn_type in ('StateFlow', 'ControlFlow'):
                # Simple arrow
                self._draw_arrow_head(draw, src_x, src_y, tgt_x, tgt_y)
            # Association has no arrowhead by default

            # Draw label if present
            if conn.get('name'):
                label = conn['name']
                mid_x = (src_x + tgt_x) // 2
                mid_y = (src_y + tgt_y) // 2
                bbox = draw.textbbox((0, 0), label, font=font)
                text_width = bbox[2] - bbox[0]
                # Draw label above the line
                draw.text((mid_x - text_width // 2, mid_y - 15), label, fill='black', font=font)

    def _draw_dashed_line(self, draw, x1, y1, x2, y2, dash_length=5):
        """Draw a dashed line"""
        import math
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)

        if distance == 0:
            return

        dashes = int(distance / dash_length)
        for i in range(0, dashes, 2):
            start = i / dashes
            end = min((i + 1) / dashes, 1.0)
            sx = x1 + dx * start
            sy = y1 + dy * start
            ex = x1 + dx * end
            ey = y1 + dy * end
            draw.line([sx, sy, ex, ey], fill='black', width=1)

    def _draw_arrow_head(self, draw, x1, y1, x2, y2, size=8):
        """Draw an arrow head at (x2, y2) pointing from (x1, y1)"""
        import math

        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)

        if distance == 0:
            return

        # Normalize
        dx /= distance
        dy /= distance

        # Arrow points
        angle = math.pi / 6  # 30 degrees
        left_x = x2 - size * (dx * math.cos(angle) + dy * math.sin(angle))
        left_y = y2 - size * (dy * math.cos(angle) - dx * math.sin(angle))
        right_x = x2 - size * (dx * math.cos(angle) - dy * math.sin(angle))
        right_y = y2 - size * (dy * math.cos(angle) + dx * math.sin(angle))

        draw.line([x2, y2, left_x, left_y], fill='black', width=1)
        draw.line([x2, y2, right_x, right_y], fill='black', width=1)

    def _draw_triangle_arrow(self, draw, x1, y1, x2, y2, size=10, filled=False):
        """Draw a triangle arrow head (for generalization/realization)"""
        import math

        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)

        if distance == 0:
            return

        # Normalize
        dx /= distance
        dy /= distance

        # Triangle points
        angle = math.pi / 7  # Narrower angle for triangle
        left_x = x2 - size * (dx * math.cos(angle) + dy * math.sin(angle))
        left_y = y2 - size * (dy * math.cos(angle) - dx * math.sin(angle))
        right_x = x2 - size * (dx * math.cos(angle) - dy * math.sin(angle))
        right_y = y2 - size * (dy * math.cos(angle) + dx * math.sin(angle))

        # Draw triangle
        points = [(x2, y2), (left_x, left_y), (right_x, right_y)]
        if filled:
            draw.polygon(points, outline='black', fill='black')
        else:
            draw.polygon(points, outline='black', fill='white')

    def _draw_diamond_arrow(self, draw, x1, y1, x2, y2, size=8, filled=False):
        """Draw a diamond arrow head (for aggregation/composition)"""
        import math

        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)

        if distance == 0:
            return

        # Normalize
        dx /= distance
        dy /= distance

        # Perpendicular vector
        perp_x = -dy
        perp_y = dx

        # Diamond points
        tip = (x2, y2)
        mid_back_x = x2 - size * dx
        mid_back_y = y2 - size * dy
        left = (mid_back_x + size * 0.5 * perp_x, mid_back_y + size * 0.5 * perp_y)
        right = (mid_back_x - size * 0.5 * perp_x, mid_back_y - size * 0.5 * perp_y)
        back = (x2 - size * 2 * dx, y2 - size * 2 * dy)

        points = [tip, left, back, right]
        if filled:
            draw.polygon(points, outline='black', fill='black')
        else:
            draw.polygon(points, outline='black', fill='white')
