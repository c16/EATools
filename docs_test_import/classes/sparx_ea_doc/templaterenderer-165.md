# Class: TemplateRenderer

[Home](../../index.md) > [Classes](../index.md) > [Sparx Ea Doc](index.md) > TemplateRenderer

**Package:** sparx_ea_doc

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {DBBFB169-F499-4768-A4DB-0B10A59137EC}**

**Description:** Renders documentation templates with data

## Diagrams

### sparx_ea_doc

![sparx_ea_doc](../../diagrams/sparx_ea_doc.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, template_dir: Path | void |  Initialize the template renderer  Args:     template_dir: Directory containing template files |
| _process_conditionals | self: unknown, content: str, data: Dict[str, Any] | str |  Process conditional sections <if_xxx>...</if_xxx>  Args:     content: Template content     data: Data dictionary  Returns:     Content with conditionals processed |
| _process_loops | self: unknown, content: str, data: Dict[str, Any] | str |  Process repeating sections <for_each_xxx>...</for_each_xxx>  Args:     content: Template content     data: Data dictionary with lists  Returns:     Content with loops processed |
| _replace_placeholders | self: unknown, content: str, data: Dict[str, Any] | str |  Replace simple placeholders <placeholder_name> with values  Args:     content: Content with placeholders     data: Data dictionary  Returns:     Content with placeholders replaced |
| load_template | self: unknown, template_name: str | str |  Load a template file  Args:     template_name: Name of the template file (e.g., 'use_case_template.md')  Returns:     Template content as string |
| render | self: unknown, template_content: str, data: Dict[str, Any] | str |  Render a template with the provided data  Args:     template_content: Template string with placeholders     data: Dictionary of data to fill into template  Returns:     Rendered content |

