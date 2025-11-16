# Class: DiagramRenderer

[Home](../../index.md) > [Classes](../index.md) > [Sparx Ea Doc](index.md) > DiagramRenderer

**Package:** sparx_ea_doc

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {8D7AFD0D-097C-4d71-B7D9-601AB895C8DF}**

**Description:** Renders Sparx EA diagrams to PNG using Graphviz

## Diagrams

### sparx_ea_doc

![sparx_ea_doc](../../diagrams/sparx_ea_doc.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, extractor: unknown, output_dir: Path, ea_diagrams_dir: str | void |  Initialize the diagram renderer  Args:     extractor: SparxExtractor instance with database connection     output_dir: Output directory for rendered diagrams     ea_diagrams_dir: Directory containing EA-exported diagrams (optional) |
| _calculate_edge_intersection | self: unknown, src_x: unknown, src_y: unknown, tgt_x: unknown, tgt_y: unknown, tgt_left: unknown, tgt_top: unknown, tgt_right: unknown, tgt_bottom: unknown | void |  Calculate where a line from source to target center intersects with target rectangle edge  Returns: (intersection_x, intersection_y) |
| _calculate_position | self: unknown, obj_data: Dict, diagram_dims: Dict | str |  Calculate Graphviz position from EA coordinates for pixel-perfect layout  EA coordinates: - Origin at top-left (0, 0) - X increases right (positive values) - Y is negative, with more negative = higher up in diagram - Units are in pixels  Graphviz neato coordinates: - Origin at bottom-left - X increases right, Y increases up - Units in points (1/72 inch) - Append "!" to fix position  For pixel-perfect rendering: - Convert EA pixels to inches (96 DPI) - Invert Y-axis (EA: negative up, Graphviz: positive up) |
| _draw_actor_pil | self: unknown, draw: unknown, obj_data: Dict, font: unknown | void | Draw an actor as a stick figure |
| _draw_arrow_head | self: unknown, draw: unknown, x1: unknown, y1: unknown, x2: unknown, y2: unknown, size: unknown | void | Draw an arrow head at (x2, y2) pointing from (x1, y1) |
| _draw_box_pil | self: unknown, draw: unknown, obj_data: Dict, font: unknown | void | Draw a generic box |
| _draw_class_pil | self: unknown, draw: unknown, obj_data: Dict, fonts: Dict, diagram_props: Dict | void | Draw a class/interface/enumeration with compartments |
| _draw_component_pil | self: unknown, draw: unknown, obj_data: Dict, fonts: Dict | void | Draw a component |
| _draw_connectors_pil | self: unknown, draw: unknown, connectors: List[Dict], objects: Dict, font: unknown | void | Draw connectors between objects |
| _draw_dashed_line | self: unknown, draw: unknown, x1: unknown, y1: unknown, x2: unknown, y2: unknown, dash_length: unknown | void | Draw a dashed line |
| _draw_diamond_arrow | self: unknown, draw: unknown, x1: unknown, y1: unknown, x2: unknown, y2: unknown, size: unknown, filled: unknown | void | Draw a diamond arrow head (for aggregation/composition) |
| _draw_state_pil | self: unknown, draw: unknown, obj_data: Dict, font: unknown | void | Draw a state machine state |
| _draw_triangle_arrow | self: unknown, draw: unknown, x1: unknown, y1: unknown, x2: unknown, y2: unknown, size: unknown, filled: unknown | void | Draw a triangle arrow head (for generalization/realization) |
| _draw_usecase_pil | self: unknown, draw: unknown, obj_data: Dict, font: unknown | void | Draw a use case as an ellipse |
| _enrich_objects_with_features | self: unknown, objects: Dict, diagram_props: Dict | None | Add attributes and operations to objects based on diagram properties |
| _find_ea_exported_diagram | self: unknown, diagram_id: int | Path |  Find EA-exported diagram by GUID  Args:     diagram_id: The diagram ID  Returns:     Path to EA-exported diagram if found, None otherwise |
| _format_edge_label | self: unknown, conn: Dict | str | Format edge label with cardinality and role information |
| _format_node_label | self: unknown, obj_data: Dict, diagram_props: Dict | str | Format node label for Graphviz with optional attributes and operations |
| _get_diagram_connectors | self: unknown, diagram_id: int | List[Dict] | Get all connectors in a diagram |
| _get_diagram_dimensions | self: unknown, diagram_id: int | Dict | Get diagram dimensions from EA |
| _get_diagram_objects | self: unknown, diagram_id: int | Dict | Get all objects in a diagram with position information |
| _get_diagram_properties | self: unknown, diagram_id: int | Dict | Get diagram display properties from PDATA field |
| _get_diagram_type | self: unknown, diagram_id: int | str | Get the diagram type |
| _get_diagram_type | self: unknown, diagram_props: Dict | str | Determine diagram type prefix from properties |
| _get_edge_style | self: unknown, connector_type: str | Dict | Get edge style based on connector type |
| _get_node_style | self: unknown, object_type: str | Tuple[str, str] | Get node shape and fill color based on object type |
| _get_object_attributes | self: unknown, object_id: int | List[str] | Get formatted attributes for an object |
| _get_object_operations | self: unknown, object_id: int | List[str] | Get formatted operations for an object |
| _get_state_activities | self: unknown, object_id: int | Dict[str, list] | Get entry, do, and exit activities for a state |
| _render_diagram_pil | self: unknown, diagram_id: int, diagram_name: str | Path |  Render diagram using PIL for pixel-perfect layout matching EA  Args:     diagram_id: The diagram ID     diagram_name: The name of the diagram  Returns:     Path to the generated PNG file |
| _use_ea_exported_diagram | self: unknown, source_path: Path, diagram_name: str | Path |  Copy EA-exported diagram to output directory  Args:     source_path: Path to EA-exported diagram     diagram_name: Name of the diagram  Returns:     Path to copied diagram in output directory |
| render_all_diagrams | self: unknown | List[Tuple[str, Path]] |  Render all diagrams in the model  Returns:     List of tuples (diagram_name, png_path) |
| render_diagram | self: unknown, diagram_id: int, diagram_name: str, package_name: str | Path |  Render a single diagram to PNG with pixel-perfect layout  Args:     diagram_id: The diagram ID from t_diagram table     diagram_name: The name of the diagram     package_name: The package this diagram belongs to (ignored for now)  Returns:     Path to the generated PNG file |

