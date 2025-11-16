# Class: ClassGenerator

[Home](../../index.md) > [Classes](../index.md) > [Generators](index.md) > ClassGenerator

**Package:** generators

**Version: 1.0 | Modified: 2025-11-16 19:19:33 | GUID: {B7DF01E9-2016-4132-810F-1F31387E1E0D}**

**Description:** Generates class and module documentation

## Diagrams

### generators

![generators](../../diagrams/generators.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, extractor: unknown, output_dir: Path, template_dir: Path, diagram_guid_to_png: Dict[str, str] | void |  Initialize the class generator  Args:     extractor: SparxExtractor instance with extracted data     output_dir: Output directory for documentation     template_dir: Directory containing templates (optional)     diagram_guid_to_png: Mapping of diagram GUIDs to PNG file paths |
| _generate_enumerations_section | self: unknown | str | Generate enumerations section for the index |
| _generate_single_class | self: unknown, cls: unknown, class_file: Path | str | Generate documentation for a single class |
| _get_class_diagrams | self: unknown, object_id: int | List[tuple] |  Get diagrams that contain a specific class  Args:     object_id: The object ID of the class  Returns:     List of (diagram_guid, diagram_name) tuples |
| _get_package_diagrams | self: unknown, package_names: List[str] | List[tuple] |  Get diagrams for given package names  Args:     package_names: List of package names to find diagrams for  Returns:     List of (diagram_guid, diagram_name) tuples |
| generate | self: unknown | void | Generate class and module documentation |

