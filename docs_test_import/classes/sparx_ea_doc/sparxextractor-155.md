# Class: SparxExtractor

[Home](../../index.md) > [Classes](../index.md) > [Sparx Ea Doc](index.md) > SparxExtractor

**Package:** sparx_ea_doc

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {F6DF38F7-0065-4e5f-A070-801A5B5D8E14}**

**Description:** Handles extraction of data from Sparx EA SQLite database

## Diagrams

### sparx_ea_doc

![sparx_ea_doc](../../diagrams/sparx_ea_doc.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, qea_path: Path | void |  Initialize the extractor  Args:     qea_path: Path to the .qea SQLite database file |
| close_db | self: unknown | void | Close database connection |
| connect_db | self: unknown | sqlite3.Connection | Establish connection to the SQLite database |
| extract_all | self: unknown | void | Main extraction orchestrator |
| extract_attributes | self: unknown | void | Extract attributes for classes and components |
| extract_classes | self: unknown | void | Extract classes, interfaces, and enumerations |
| extract_components | self: unknown | void | Extract components |
| extract_connectors | self: unknown | void | Extract relationships between elements |
| extract_constraints | self: unknown | void | Extract constraints (pre-conditions, post-conditions, etc.) |
| extract_diagrams | self: unknown | void | Extract diagram-to-object mappings |
| extract_operations | self: unknown | void | Extract operations/methods for classes and components |
| extract_packages | self: unknown | void | Extract package information |
| extract_requirements | self: unknown | void | Extract requirements and their relationships to use cases |
| extract_scenarios | self: unknown | void | Extract scenarios for use cases |
| extract_state_machines | self: unknown | void | Extract state machines and states |
| extract_use_cases | self: unknown | void | Extract use cases and actors |
| get_connectors_for_element | self: unknown, element_id: int, connector_type: Optional[str] | List[Connector] | Get all connectors involving a specific element |
| get_diagrams_for_element | self: unknown, element_id: int | List[str] | Get all diagram GUIDs that contain a specific element |
| get_objects_on_diagram | self: unknown, diagram_guid: str | List[tuple] | Get all objects (id, name, type) that appear on a specific diagram |

