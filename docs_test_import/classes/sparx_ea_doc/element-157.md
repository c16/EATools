# Class: Element

[Home](../../index.md) > [Classes](../index.md) > [Sparx Ea Doc](index.md) > Element

**Package:** sparx_ea_doc

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {64ABBB1F-5D72-4b93-89A1-F06972BC5694}**

**Description:** Base class for model elements

## Diagrams

### sparx_ea_doc

![sparx_ea_doc](../../diagrams/sparx_ea_doc.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| clean_note | self: unknown | str | Remove HTML tags and clean up note text |
| parse_structured_note | self: unknown | Dict[str, str] |  Parse notes field for structured sections like: - Preconditions / Pre-conditions - Postconditions / Post-conditions - Main Flow / Scenario - Alternative Flows - Business Rules Returns dict with section names as keys |

## Attributes

| Name | Type | Default | Const | Description |
|------|------|---------|-------|-------------|
| object_id | int | - | No | - |
| name | str | - | No | - |
| object_type | str | - | No | - |
| note | str | - | No | - |
| stereotype | str | - | No | - |
| package_name | str | - | No | - |
| visibility | str | 'public' | No | - |
| alias | str | '' | No | - |
| version | str | '' | No | - |
| modified_date | str | '' | No | - |
| guid | str | '' | No | - |

