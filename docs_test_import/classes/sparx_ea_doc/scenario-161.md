# Class: Scenario

[Home](../../index.md) > [Classes](../index.md) > [Sparx Ea Doc](index.md) > Scenario

**Package:** sparx_ea_doc

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {50C69582-A61E-43c7-BD1C-D6BF767B40E7}**

**Description:** Use case scenario

## Diagrams

### sparx_ea_doc

![sparx_ea_doc](../../diagrams/sparx_ea_doc.png)


## Attributes

| Name | Type | Default | Const | Description |
|------|------|---------|-------|-------------|
| name | str | - | No | - |
| scenario_type | str | - | No | Basic Path, Exception, Alternate, etc. |
| steps | List[str] | field(default_factory=list) | No | - |
| notes | str | '' | No | - |
| ea_guid | str | '' | No | - |
| extensions | List[Tuple[int, str, str]] | field(default_factory=list) | No | [(step_index, level, extension_guid), ...] |

