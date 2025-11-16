# Class: EADiagramExtractor

[Home](../../index.md) > [Classes](../index.md) > [Eatools](index.md) > EADiagramExtractor

**Package:** EATools

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {769377FB-C6AB-4c36-9541-5242C67A7C3F}**

**Description:** Extract all diagrams from EA repository

## Diagrams

### EATools

![EATools](../../diagrams/eatools.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, repo_path: unknown, output_dir: unknown | void | - |
| connect | self: unknown | void | Connect to EA repository |
| disconnect | self: unknown | void | Close repository connection |
| export_diagram | self: unknown, diagram: unknown, package_name: unknown | void | Export a single diagram using the best available method |
| extract | self: unknown | void | Main extraction process |
| format_date | self: unknown, date: unknown | void | Format date for filename |
| process_package | self: unknown, package: unknown, level: unknown | void | Recursively process package and all sub-packages |

