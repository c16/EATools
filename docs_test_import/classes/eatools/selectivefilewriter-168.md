# Class: SelectiveFileWriter

[Home](../../index.md) > [Classes](../index.md) > [Eatools](index.md) > SelectiveFileWriter

**Package:** EATools

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {05428C7E-9C1B-4dd1-8847-9FD5794F0EC1}**

**Description:** Wraps file operations to allow selective writing based on file selection

## Diagrams

### EATools

![EATools](../../diagrams/eatools.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __enter__ | self: unknown | void | Enable selective writing by patching the open function |
| __exit__ | self: unknown, exc_type: unknown, exc_val: unknown, exc_tb: unknown | void | Restore original open function |
| __init__ | self: unknown, output_dir: Path, selected_files: Set[str] | void |  Initialize selective file writer  Args:     output_dir: Base output directory     selected_files: Set of relative file paths that should be written |
| _selective_open | self: unknown, file: unknown, mode: unknown, args: unknown, kwargs: unknown | void |  Selective open that only allows writing to selected files  Args:     file: File path to open     mode: File mode |

