# Class: StateMachineGenerator

[Home](../../index.md) > [Classes](../index.md) > [Generators](index.md) > StateMachineGenerator

**Package:** generators

**Version: 1.0 | Modified: 2025-11-16 19:19:33 | GUID: {260C9A62-4C17-42aa-9DCE-F09C284C06AD}**

**Description:** Generates state machine documentation

## Diagrams

### generators

![generators](../../diagrams/generators.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, extractor: unknown, output_dir: Path, template_dir: Path, diagram_guid_to_png: Dict[str, str] | void |  Initialize the state machine generator  Args:     extractor: SparxExtractor instance with extracted data     output_dir: Output directory for documentation     template_dir: Directory containing templates (optional)     diagram_guid_to_png: Mapping of diagram GUIDs to PNG file paths |
| _generate_single_state_machine | self: unknown, sm: unknown, sm_file: Path | str | Generate documentation for a single state machine |
| _generate_with_template | self: unknown, sm: unknown, breadcrumbs: str | str | Generate state machine documentation using template |
| _get_package_diagrams | self: unknown, package_names: List[str] | List[tuple] |  Get diagrams for given package names  Args:     package_names: List of package names to find diagrams for  Returns:     List of (diagram_guid, diagram_name) tuples |
| generate | self: unknown | void | Generate state machine documentation |

