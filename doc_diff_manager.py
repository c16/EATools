#!/usr/bin/env python3
"""
Documentation Diff Manager

Standalone utility for managing documentation version history and generating diffs.

Usage:
    # List all versions
    python doc_diff_manager.py list

    # Generate diff between latest version and current docs
    python doc_diff_manager.py generate

    # Generate diff between specific versions
    python doc_diff_manager.py generate --from v_20251110_120000

    # Compare two specific versions
    python doc_diff_manager.py compare v_20251110_120000 v_20251110_130000

    # Clean up old versions (keep last 5)
    python doc_diff_manager.py cleanup --keep 5

    # Show version details
    python doc_diff_manager.py info v_20251110_120000
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from sparx_ea_doc.diff_generator import DiffGenerator


def list_versions(diff_gen: DiffGenerator):
    """List all stored versions"""
    versions = diff_gen.list_versions()

    if not versions:
        print("No versions found in history.")
        print("Run documentation generator with --track-changes to create versions.")
        return

    print("=" * 80)
    print("Documentation Version History")
    print("=" * 80)
    print(f"\nTotal versions: {len(versions)}\n")

    for i, version in enumerate(versions, 1):
        timestamp = datetime.fromisoformat(version['timestamp'])
        print(f"{i}. {version['version_id']}")
        print(f"   Timestamp:   {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Files:       {version['file_count']}")
        if version.get('description'):
            print(f"   Description: {version['description']}")
        print()


def show_version_info(diff_gen: DiffGenerator, version_id: str):
    """Show detailed information about a specific version"""
    versions = diff_gen.list_versions()
    version = next((v for v in versions if v['version_id'] == version_id), None)

    if not version:
        print(f"❌ Error: Version '{version_id}' not found")
        return 1

    timestamp = datetime.fromisoformat(version['timestamp'])

    print("=" * 80)
    print(f"Version: {version['version_id']}")
    print("=" * 80)
    print(f"\nTimestamp:   {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Files:       {version['file_count']}")
    if version.get('description'):
        print(f"Description: {version['description']}")

    print("\nFiles in this version:")
    print("-" * 80)
    for filename in sorted(version['files'].keys()):
        checksum = version['files'][filename][:8]  # Show first 8 chars
        print(f"  {filename} ({checksum}...)")

    return 0


def generate_diff(diff_gen: DiffGenerator, from_version: str = "latest"):
    """Generate diff documentation"""
    print("=" * 80)
    print("Generating Diff Documentation")
    print("=" * 80)

    try:
        stats = diff_gen.generate_diff_documentation(compare_with=from_version)

        print(f"\n✅ Diff generation complete!\n")
        print(f"Compared with: {stats['previous_version']}")
        print(f"Previous timestamp: {stats['previous_timestamp']}\n")

        print("Change Summary:")
        print("-" * 80)
        print(f"  Files Added:     {len(stats['files_added'])}")
        print(f"  Files Removed:   {len(stats['files_removed'])}")
        print(f"  Files Modified:  {len(stats['files_modified'])}")
        print(f"  Files Unchanged: {len(stats['files_unchanged'])}")
        print(f"  Total Additions: +{stats['total_additions']} lines")
        print(f"  Total Deletions: -{stats['total_deletions']} lines")
        print("-" * 80)

        if stats['files_added']:
            print(f"\n🆕 New files ({len(stats['files_added'])}):")
            for f in stats['files_added'][:10]:
                print(f"   + {f}")
            if len(stats['files_added']) > 10:
                print(f"   ... and {len(stats['files_added']) - 10} more")

        if stats['files_removed']:
            print(f"\n🗑️  Removed files ({len(stats['files_removed'])}):")
            for f in stats['files_removed'][:10]:
                print(f"   - {f}")
            if len(stats['files_removed']) > 10:
                print(f"   ... and {len(stats['files_removed']) - 10} more")

        if stats['files_modified']:
            print(f"\n✏️  Modified files ({len(stats['files_modified'])}):")
            for f in stats['files_modified'][:10]:
                print(f"   • {f}")
            if len(stats['files_modified']) > 10:
                print(f"   ... and {len(stats['files_modified']) - 10} more")

        print(f"\n📁 Diff documentation saved to: {diff_gen.diff_output_dir}")
        print(f"📊 View changes summary: {diff_gen.diff_output_dir / 'CHANGES.md'}")

        return 0

    except Exception as e:
        print(f"\n❌ Error generating diff: {e}")
        return 1


def cleanup_versions(diff_gen: DiffGenerator, keep: int = 5):
    """Clean up old versions"""
    versions_before = len(diff_gen.list_versions())

    if versions_before <= keep:
        print(f"Currently have {versions_before} version(s), no cleanup needed (keeping last {keep})")
        return 0

    print(f"Cleaning up old versions (keeping last {keep})...")
    diff_gen.cleanup_old_versions(keep_last_n=keep)

    versions_after = len(diff_gen.list_versions())
    removed = versions_before - versions_after

    print(f"✅ Removed {removed} old version(s)")
    print(f"   Remaining versions: {versions_after}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Manage documentation version history and generate diffs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all versions
  python doc_diff_manager.py list

  # Generate diff with latest version
  python doc_diff_manager.py generate

  # Generate diff with specific version
  python doc_diff_manager.py generate --from v_20251110_120000

  # Show version details
  python doc_diff_manager.py info v_20251110_120000

  # Clean up (keep last 5)
  python doc_diff_manager.py cleanup --keep 5
        """
    )

    parser.add_argument(
        'command',
        choices=['list', 'generate', 'info', 'cleanup'],
        help='Command to execute'
    )

    parser.add_argument(
        'version',
        nargs='?',
        help='Version ID (for info command)'
    )

    parser.add_argument(
        '--docs-dir',
        default='docs',
        help='Documentation directory (default: docs)'
    )

    parser.add_argument(
        '--history-dir',
        default='docs_history',
        help='Version history directory (default: docs_history)'
    )

    parser.add_argument(
        '--diff-dir',
        default='docs_diff',
        help='Diff output directory (default: docs_diff)'
    )

    parser.add_argument(
        '--from',
        dest='from_version',
        default='latest',
        help='Version to compare from (default: latest)'
    )

    parser.add_argument(
        '--keep',
        type=int,
        default=5,
        help='Number of versions to keep during cleanup (default: 5)'
    )

    args = parser.parse_args()

    # Initialize diff generator
    diff_gen = DiffGenerator(
        docs_dir=Path(args.docs_dir),
        history_dir=Path(args.history_dir),
        diff_output_dir=Path(args.diff_dir)
    )

    # Execute command
    if args.command == 'list':
        list_versions(diff_gen)
        return 0

    elif args.command == 'info':
        if not args.version:
            print("❌ Error: Version ID required for 'info' command")
            print("Usage: python doc_diff_manager.py info <version_id>")
            return 1
        return show_version_info(diff_gen, args.version)

    elif args.command == 'generate':
        return generate_diff(diff_gen, from_version=args.from_version)

    elif args.command == 'cleanup':
        return cleanup_versions(diff_gen, keep=args.keep)

    return 0


if __name__ == '__main__':
    sys.exit(main())
