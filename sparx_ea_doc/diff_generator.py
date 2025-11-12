#!/usr/bin/env python3
"""
Documentation Diff Generator

This module tracks changes between documentation versions and generates
visual diff markup showing additions, deletions, and modifications.
"""

import json
import shutil
import difflib
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class DiffGenerator:
    """Generates visual diff markup for documentation changes"""

    def __init__(self, docs_dir: Path, history_dir: Path = None, diff_output_dir: Path = None):
        """
        Initialize the diff generator

        Args:
            docs_dir: Current documentation directory
            history_dir: Directory to store version history (default: docs_history)
            diff_output_dir: Directory for diff-annotated output (default: docs_diff)
        """
        self.docs_dir = Path(docs_dir)
        self.history_dir = Path(history_dir) if history_dir else Path("docs_history")
        self.diff_output_dir = Path(diff_output_dir) if diff_output_dir else Path("docs_diff")
        self.manifest_file = self.history_dir / "manifest.json"

        # Create directories if they don't exist
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # Load or create manifest
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        """Load version manifest or create new one"""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        return {
            'versions': [],
            'created': datetime.now().isoformat(),
            'last_updated': None
        }

    def _save_manifest(self):
        """Save version manifest"""
        self.manifest['last_updated'] = datetime.now().isoformat()
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _get_all_files(self, directory: Path) -> Dict[str, str]:
        """Get all markdown files with their checksums"""
        files = {}
        if not directory.exists():
            return files

        for file_path in sorted(directory.rglob('*.md')):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(directory))
                files[rel_path] = self._calculate_checksum(file_path)

        return files

    def save_current_version(self, description: str = "") -> str:
        """
        Save current documentation as a new version

        Args:
            description: Optional description of this version

        Returns:
            Version ID (timestamp)
        """
        # Generate version ID
        version_id = datetime.now().strftime("v_%Y%m%d_%H%M%S")
        version_dir = self.history_dir / version_id

        # Copy current docs to version directory
        if self.docs_dir.exists():
            shutil.copytree(self.docs_dir, version_dir)

            # Calculate file checksums
            files = self._get_all_files(version_dir)

            # Update manifest
            version_info = {
                'version_id': version_id,
                'timestamp': datetime.now().isoformat(),
                'description': description,
                'file_count': len(files),
                'files': files
            }
            self.manifest['versions'].append(version_info)
            self._save_manifest()

            return version_id
        else:
            raise FileNotFoundError(f"Documentation directory not found: {self.docs_dir}")

    def get_latest_version(self) -> Optional[Dict]:
        """Get the most recent version from history"""
        if not self.manifest['versions']:
            return None
        return self.manifest['versions'][-1]

    def get_previous_version(self) -> Optional[Dict]:
        """Get the second most recent version (before latest)"""
        if len(self.manifest['versions']) < 2:
            return None
        return self.manifest['versions'][-2]

    def _generate_line_diff(self, old_content: str, new_content: str) -> List[str]:
        """
        Generate line-by-line diff with visual markup

        Returns:
            List of HTML-formatted lines showing the diff
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(old_lines, new_lines, lineterm='')
        diff_lines = list(diff)

        if not diff_lines:
            # No changes
            return new_lines

        # Process unified diff into visual markup
        result = []
        in_change_block = False

        for line in diff_lines:
            if line.startswith('---') or line.startswith('+++'):
                continue
            elif line.startswith('@@'):
                if in_change_block:
                    result.append('\n')
                in_change_block = True
                continue
            elif line.startswith('-'):
                # Deletion
                content = line[1:]
                result.append(f'<span style="background-color: #ffcccc; text-decoration: line-through;">{content}</span>')
            elif line.startswith('+'):
                # Addition
                content = line[1:]
                result.append(f'<span style="background-color: #ccffcc;">{content}</span>')
            else:
                # Context (unchanged)
                if line.startswith(' '):
                    result.append(line[1:])
                else:
                    result.append(line)

        return result

    def _generate_file_diff(self, old_file: Path, new_file: Path) -> Tuple[str, Dict]:
        """
        Generate diff for a single file

        Returns:
            (diff_content, metadata)
        """
        # Read both files
        with open(old_file, 'r', encoding='utf-8') as f:
            old_content = f.read()
        with open(new_file, 'r', encoding='utf-8') as f:
            new_content = f.read()

        # Calculate statistics
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()

        # Generate diff using difflib
        diff = difflib.unified_diff(old_lines, new_lines, lineterm='')
        diff_list = list(diff)

        # Count changes
        additions = sum(1 for line in diff_list if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff_list if line.startswith('-') and not line.startswith('---'))

        metadata = {
            'old_lines': len(old_lines),
            'new_lines': len(new_lines),
            'additions': additions,
            'deletions': deletions,
            'has_changes': additions > 0 or deletions > 0
        }

        if not metadata['has_changes']:
            # No changes, return original
            return new_content, metadata

        # Generate visual diff
        diff_lines = self._generate_line_diff(old_content, new_content)

        # Create header
        header = f"""<!-- DIFF TRACKING -->
<!-- Previous version had {metadata['old_lines']} lines -->
<!-- Current version has {metadata['new_lines']} lines -->
<!-- Changes: +{metadata['additions']} additions, -{metadata['deletions']} deletions -->

---

**📊 Document Changes:**
- **Lines before:** {metadata['old_lines']}
- **Lines after:** {metadata['new_lines']}
- **Additions:** <span style="color: green;">+{metadata['additions']}</span>
- **Deletions:** <span style="color: red;">-{metadata['deletions']}</span>

---

"""

        diff_content = header + ''.join(diff_lines)

        return diff_content, metadata

    def generate_diff_documentation(self, compare_with: str = "latest") -> Dict:
        """
        Generate diff-annotated documentation comparing current with a previous version

        Args:
            compare_with: "latest" for most recent, or specific version_id

        Returns:
            Dictionary with statistics about the diff
        """
        # Get version to compare with
        if compare_with == "latest":
            prev_version = self.get_latest_version()
        else:
            prev_version = next((v for v in self.manifest['versions'] if v['version_id'] == compare_with), None)

        if not prev_version:
            raise ValueError(f"No previous version found to compare with")

        prev_version_dir = self.history_dir / prev_version['version_id']

        if not prev_version_dir.exists():
            raise FileNotFoundError(f"Previous version directory not found: {prev_version_dir}")

        # Create diff output directory
        self.diff_output_dir.mkdir(parents=True, exist_ok=True)

        # Get file lists
        prev_files = self._get_all_files(prev_version_dir)
        current_files = self._get_all_files(self.docs_dir)

        # Track statistics
        stats = {
            'previous_version': prev_version['version_id'],
            'previous_timestamp': prev_version['timestamp'],
            'files_added': [],
            'files_removed': [],
            'files_modified': [],
            'files_unchanged': [],
            'total_additions': 0,
            'total_deletions': 0
        }

        prev_file_set = set(prev_files.keys())
        current_file_set = set(current_files.keys())

        # Files added
        stats['files_added'] = sorted(current_file_set - prev_file_set)

        # Files removed
        stats['files_removed'] = sorted(prev_file_set - current_file_set)

        # Files potentially modified or unchanged
        common_files = prev_file_set & current_file_set

        for rel_path in sorted(common_files):
            prev_file = prev_version_dir / rel_path
            current_file = self.docs_dir / rel_path
            output_file = self.diff_output_dir / rel_path

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            if prev_files[rel_path] != current_files[rel_path]:
                # File was modified
                diff_content, metadata = self._generate_file_diff(prev_file, current_file)
                stats['files_modified'].append(rel_path)
                stats['total_additions'] += metadata['additions']
                stats['total_deletions'] += metadata['deletions']

                # Write diff file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(diff_content)
            else:
                # File unchanged
                stats['files_unchanged'].append(rel_path)
                # Copy unchanged file
                shutil.copy2(current_file, output_file)

        # Copy new files
        for rel_path in stats['files_added']:
            current_file = self.docs_dir / rel_path
            output_file = self.diff_output_dir / rel_path
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Read file and add "NEW" marker
            with open(current_file, 'r', encoding='utf-8') as f:
                content = f.read()

            new_marker = """<!-- NEW FILE -->
**🆕 This is a new file in this version**

---

"""
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(new_marker + content)

        # Create diff summary report
        self._create_diff_summary(stats)

        return stats

    def _create_diff_summary(self, stats: Dict):
        """Create a summary report of all changes"""
        summary_content = f"""# Documentation Changes Summary

**Compared with:** {stats['previous_version']}
**Previous version timestamp:** {stats['previous_timestamp']}
**Comparison date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Overview

| Metric | Count |
|--------|-------|
| Files Added | {len(stats['files_added'])} |
| Files Removed | {len(stats['files_removed'])} |
| Files Modified | {len(stats['files_modified'])} |
| Files Unchanged | {len(stats['files_unchanged'])} |
| **Total Files** | **{len(stats['files_added']) + len(stats['files_removed']) + len(stats['files_modified']) + len(stats['files_unchanged'])}** |

## Change Statistics

- **Total Additions:** <span style="color: green;">+{stats['total_additions']} lines</span>
- **Total Deletions:** <span style="color: red;">-{stats['total_deletions']} lines</span>

---

"""

        if stats['files_added']:
            summary_content += "## 🆕 New Files\n\n"
            for f in stats['files_added']:
                summary_content += f"- [{f}]({f})\n"
            summary_content += "\n"

        if stats['files_removed']:
            summary_content += "## 🗑️ Removed Files\n\n"
            for f in stats['files_removed']:
                summary_content += f"- {f}\n"
            summary_content += "\n"

        if stats['files_modified']:
            summary_content += "## ✏️ Modified Files\n\n"
            for f in stats['files_modified']:
                summary_content += f"- [{f}]({f})\n"
            summary_content += "\n"

        summary_content += """---

## Legend

- <span style="background-color: #ccffcc;">Green highlight</span> = Added content
- <span style="background-color: #ffcccc; text-decoration: line-through;">Red strikethrough</span> = Removed content
- Regular text = Unchanged content

---

*Generated by Sparx EA Documentation Diff Generator*
"""

        summary_file = self.diff_output_dir / "CHANGES.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)

    def list_versions(self) -> List[Dict]:
        """List all stored versions"""
        return self.manifest['versions']

    def cleanup_old_versions(self, keep_last_n: int = 5):
        """
        Remove old versions, keeping only the most recent N versions

        Args:
            keep_last_n: Number of recent versions to keep
        """
        if len(self.manifest['versions']) <= keep_last_n:
            return

        # Get versions to remove
        versions_to_remove = self.manifest['versions'][:-keep_last_n]

        for version in versions_to_remove:
            version_dir = self.history_dir / version['version_id']
            if version_dir.exists():
                shutil.rmtree(version_dir)

        # Update manifest
        self.manifest['versions'] = self.manifest['versions'][-keep_last_n:]
        self._save_manifest()
