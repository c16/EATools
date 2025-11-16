# Class: DiffGenerator

[Home](../../index.md) > [Classes](../index.md) > [Sparx Ea Doc](index.md) > DiffGenerator

**Package:** sparx_ea_doc

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {6D354BCF-3371-4767-9C0B-55F275DB4BD3}**

**Description:** Generates visual diff markup for documentation changes

## Diagrams

### sparx_ea_doc

![sparx_ea_doc](../../diagrams/sparx_ea_doc.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, docs_dir: Path, history_dir: Path, diff_output_dir: Path | void |  Initialize the diff generator  Args:     docs_dir: Current documentation directory     history_dir: Directory to store version history (default: docs_history)     diff_output_dir: Directory for diff-annotated output (default: docs_diff) |
| _calculate_checksum | self: unknown, file_path: Path | str | Calculate SHA256 checksum of a file |
| _create_diff_summary | self: unknown, stats: Dict | void | Create a summary report of all changes |
| _generate_file_diff | self: unknown, old_file: Path, new_file: Path | Tuple[str, Dict] |  Generate diff for a single file  Returns:     (diff_content, metadata) |
| _generate_line_diff | self: unknown, old_content: str, new_content: str | List[str] |  Generate line-by-line diff with visual markup  Returns:     List of HTML-formatted lines showing the diff |
| _get_all_files | self: unknown, directory: Path | Dict[str, str] | Get all markdown files with their checksums |
| _load_manifest | self: unknown | Dict | Load version manifest or create new one |
| _save_manifest | self: unknown | void | Save version manifest |
| cleanup_old_versions | self: unknown, keep_last_n: int | void |  Remove old versions, keeping only the most recent N versions  Args:     keep_last_n: Number of recent versions to keep |
| generate_diff_documentation | self: unknown, compare_with: str | Dict |  Generate diff-annotated documentation comparing current with a previous version  Args:     compare_with: "latest" for most recent, or specific version_id  Returns:     Dictionary with statistics about the diff |
| get_latest_version | self: unknown | Optional[Dict] | Get the most recent version from history |
| get_previous_version | self: unknown | Optional[Dict] | Get the second most recent version (before latest) |
| list_versions | self: unknown | List[Dict] | List all stored versions |
| save_current_version | self: unknown, description: str | str |  Save current documentation as a new version  Args:     description: Optional description of this version  Returns:     Version ID (timestamp) |

