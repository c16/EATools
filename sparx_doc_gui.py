#!/usr/bin/env python3
"""
Sparx Enterprise Architect Documentation Generator - GUI
Interactive GUI for selective document generation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
from pathlib import Path
import logging
import threading
import tempfile
from datetime import datetime
from typing import Dict, List, Set, Optional

from sparx_ea_doc.extractor import SparxExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SelectiveFileWriter:
    """
    Wraps file operations to allow selective writing based on file selection
    """

    def __init__(self, output_dir: Path, selected_files: Set[str]):
        """
        Initialize selective file writer

        Args:
            output_dir: Base output directory
            selected_files: Set of relative file paths that should be written
        """
        self.output_dir = Path(output_dir)
        self.selected_files = selected_files
        self.original_open = None

    def __enter__(self):
        """Enable selective writing by patching the open function"""
        import builtins
        self.original_open = builtins.open
        builtins.open = self._selective_open
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original open function"""
        import builtins
        builtins.open = self.original_open

    def _selective_open(self, file, mode='r', *args, **kwargs):
        """
        Selective open that only allows writing to selected files

        Args:
            file: File path to open
            mode: File mode
        """
        # If not writing mode, allow normally
        if 'w' not in mode and 'a' not in mode:
            return self.original_open(file, mode, *args, **kwargs)

        # Check if this file should be written
        file_path = Path(file)

        try:
            # Get relative path from output directory
            rel_path = file_path.relative_to(self.output_dir)
            rel_path_str = str(rel_path).replace('\\', '/')

            # If not selected, create a dummy file object
            if rel_path_str not in self.selected_files:
                return open('/dev/null', mode, *args, **kwargs)

        except ValueError:
            # Not relative to output_dir, allow normally
            pass

        # Selected file or outside output_dir - write normally
        return self.original_open(file, mode, *args, **kwargs)


class DocumentTreeBuilder:
    """
    Builds the document tree structure by analyzing what would be generated
    """

    def __init__(self, extractor: SparxExtractor):
        self.extractor = extractor

    def build_tree_structure(self) -> Dict:
        """Build the complete tree structure of all possible documents"""
        tree = {
            'index.md': {'type': 'file', 'path': 'index.md'},
            'use-cases': {'type': 'folder', 'children': {}},
            'requirements': {'type': 'folder', 'children': {}},
            'state-machines': {'type': 'folder', 'children': {}},
            'components': {'type': 'folder', 'children': {}},
            'classes': {'type': 'folder', 'children': {}},
            'diagrams': {'type': 'folder', 'children': {}},
            'reports': {
                'type': 'folder',
                'children': {
                    'quality-report.md': {'type': 'file', 'path': 'reports/quality-report.md'},
                    'dependencies.md': {'type': 'file', 'path': 'reports/dependencies.md'}
                }
            }
        }

        # Add use cases
        tree['use-cases']['children']['index.md'] = {'type': 'file', 'path': 'use-cases/index.md'}
        tree['use-cases']['children']['actors.md'] = {'type': 'file', 'path': 'use-cases/actors.md'}

        for uc in self.extractor.use_cases:
            filename = f"{uc.name.lower().replace(' ', '-')}.md"
            tree['use-cases']['children'][filename] = {
                'type': 'file',
                'path': f'use-cases/{filename}',
                'title': uc.name
            }

        # Add requirements
        tree['requirements']['children']['index.md'] = {'type': 'file', 'path': 'requirements/index.md'}

        for req in self.extractor.requirements:
            filename = f"{req.name.lower().replace(' ', '-')}.md"
            tree['requirements']['children'][filename] = {
                'type': 'file',
                'path': f'requirements/{filename}',
                'title': req.name
            }

        # Add state machines
        tree['state-machines']['children']['index.md'] = {'type': 'file', 'path': 'state-machines/index.md'}

        for sm in self.extractor.state_machines:
            filename = f"sm-{sm.name.lower().replace(' ', '-')}.md"
            tree['state-machines']['children'][filename] = {
                'type': 'file',
                'path': f'state-machines/{filename}',
                'title': sm.name
            }

        # Add components
        tree['components']['children']['index.md'] = {'type': 'file', 'path': 'components/index.md'}
        tree['components']['children']['interfaces.md'] = {'type': 'file', 'path': 'components/interfaces.md'}

        for comp in self.extractor.components:
            filename = f"comp-{comp.name.lower().replace(' ', '-')}.md"
            tree['components']['children'][filename] = {
                'type': 'file',
                'path': f'components/{filename}',
                'title': comp.name
            }

        # Add classes by package
        tree['classes']['children']['index.md'] = {'type': 'file', 'path': 'classes/index.md'}

        # Group classes by package
        classes_by_package = {}
        for cls in self.extractor.classes:
            pkg = cls.package_name or 'root'
            if pkg not in classes_by_package:
                classes_by_package[pkg] = []
            classes_by_package[pkg].append(cls)

        for pkg_name, classes in sorted(classes_by_package.items()):
            pkg_dirname = pkg_name.lower().replace(' ', '-')

            if pkg_dirname not in tree['classes']['children']:
                tree['classes']['children'][pkg_dirname] = {'type': 'folder', 'children': {}}

            # Add package index.md
            tree['classes']['children'][pkg_dirname]['children']['index.md'] = {
                'type': 'file',
                'path': f'classes/{pkg_dirname}/index.md',
                'title': f'{pkg_name} Package Index'
            }

            for cls in sorted(classes, key=lambda x: x.name):
                filename = f"{cls.name.lower().replace(' ', '-')}.md"
                tree['classes']['children'][pkg_dirname]['children'][filename] = {
                    'type': 'file',
                    'path': f'classes/{pkg_dirname}/{filename}',
                    'title': cls.name
                }

        # Add reports index
        tree['reports']['children']['index.md'] = {'type': 'file', 'path': 'reports/index.md'}

        # Add diagrams (PNG files)
        # Query diagrams from database
        self.extractor.connect_db()
        try:
            cursor = self.extractor.conn.cursor()
            cursor.execute("""
                SELECT d.ea_guid, d.Name, p.Name as Package_Name
                FROM t_diagram d
                LEFT JOIN t_package p ON d.Package_ID = p.Package_ID
                ORDER BY d.Name
            """)

            for row in cursor.fetchall():
                diagram_name = row['Name']
                package_name = row['Package_Name'] or 'root'

                # Generate filename (same as DiagramRenderer)
                from sparx_ea_doc.utils import sanitize_filename
                safe_name = sanitize_filename(diagram_name.lower().replace(' ', '_'))
                filename = f"{safe_name}.png"

                tree['diagrams']['children'][filename] = {
                    'type': 'file',
                    'path': f'diagrams/{filename}',
                    'title': diagram_name
                }
        finally:
            self.extractor.close_db()

        return tree


class SparxDocGUI:
    """Main GUI application for Sparx documentation generator"""

    def __init__(self, root):
        self.root = root
        self.root.title("Sparx EA Documentation Generator")
        self.root.geometry("1200x800")

        self.qea_path = None
        self.extractor = None
        self.tree_structure = None
        self.selected_files = set()

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open .qea File...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Top frame for file selection
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="QEA File:").pack(side=tk.LEFT)
        self.file_label = ttk.Label(top_frame, text="No file selected", foreground="gray")
        self.file_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(top_frame, text="Browse...", command=self.open_file).pack(side=tk.LEFT)

        # Main content area - PanedWindow for resizable split
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Document tree
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Documents to Generate", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        ttk.Label(left_frame, text="(Double-click to toggle | Single-click to preview)",
                 font=('Arial', 9), foreground="gray").pack(anchor=tk.W)

        # Button bar
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=2)

        # Tree view with checkboxes
        tree_scroll = ttk.Scrollbar(left_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(left_frame, yscrollcommand=tree_scroll.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree.yview)

        # Bind events
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Right panel - Preview
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="Document Preview", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)

        self.preview_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD,
                                                      font=('Courier', 10))
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # Bottom frame for generation controls
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)

        self.generate_button = ttk.Button(bottom_frame, text="Generate Selected Documents",
                                         command=self.generate_documentation, state=tk.DISABLED)
        self.generate_button.pack(side=tk.RIGHT)

        # HTML generation checkbox
        self.generate_html_var = tk.BooleanVar(value=False)
        self.html_checkbox = ttk.Checkbutton(bottom_frame, text="Generate HTML",
                                             variable=self.generate_html_var)
        self.html_checkbox.pack(side=tk.RIGHT, padx=10)

        # EA Diagrams directory
        ea_frame = ttk.Frame(bottom_frame)
        ea_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(ea_frame, text="EA Diagrams:").pack(side=tk.LEFT)
        self.ea_diagrams_var = tk.StringVar(value="sample_diagrams")
        ea_entry = ttk.Entry(ea_frame, textvariable=self.ea_diagrams_var, width=20)
        ea_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(ea_frame, text="Browse...", command=self.browse_ea_diagrams, width=10).pack(side=tk.LEFT)

        self.status_label = ttk.Label(bottom_frame, text="Open a .qea file to begin", foreground="gray")
        self.status_label.pack(side=tk.LEFT)

        # Progress bar
        self.progress = ttk.Progressbar(bottom_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    def browse_ea_diagrams(self):
        """Browse for EA diagrams directory"""
        directory = filedialog.askdirectory(
            title="Select EA Diagrams Directory",
            initialdir=self.ea_diagrams_var.get() if self.ea_diagrams_var.get() else "."
        )
        if directory:
            self.ea_diagrams_var.set(directory)

    def open_file(self):
        """Open and load a .qea file"""
        filename = filedialog.askopenfilename(
            title="Select Sparx EA .qea File",
            filetypes=[("QEA Files", "*.qea"), ("All Files", "*.*")]
        )

        if not filename:
            return

        self.qea_path = Path(filename)
        self.file_label.config(text=str(self.qea_path.name), foreground="black")
        self.status_label.config(text="Loading model...", foreground="blue")

        # Load model in background thread
        thread = threading.Thread(target=self.load_model, daemon=True)
        thread.start()

    def load_model(self):
        """Load and extract model data"""
        try:
            # Extract data
            self.extractor = SparxExtractor(self.qea_path)
            self.extractor.extract_all()

            # Build tree structure
            builder = DocumentTreeBuilder(self.extractor)
            self.tree_structure = builder.build_tree_structure()

            # Update UI in main thread
            self.root.after(0, self.populate_tree)
            self.root.after(0, lambda: self.status_label.config(
                text=f"Loaded: {len(self.extractor.use_cases)} use cases, "
                     f"{len(self.extractor.classes)} classes, "
                     f"{len(self.extractor.components)} components",
                foreground="green"
            ))

        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load model:\n{e}"))
            self.root.after(0, lambda: self.status_label.config(text="Error loading model", foreground="red"))

    def populate_tree(self):
        """Populate the tree view with document structure"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add items from tree structure
        self._add_tree_items('', self.tree_structure)

        # Select all by default
        self.select_all()

        # Enable generate button
        self.generate_button.config(state=tk.NORMAL)

    def _add_tree_items(self, parent, items):
        """Recursively add items to tree"""
        for name, item in items.items():
            if item['type'] == 'file':
                # Add file with checkbox
                display_name = f"☑ {name}"
                node = self.tree.insert(parent, 'end', text=display_name,
                                       values=(item['path'], 'selected'))
                self.selected_files.add(item['path'])

            elif item['type'] == 'folder':
                # Add folder
                display_name = f"☑ {name}/"
                node = self.tree.insert(parent, 'end', text=display_name,
                                       values=('', 'selected'), open=False)

                # Add children
                if 'children' in item:
                    self._add_tree_items(node, item['children'])

    def on_tree_double_click(self, event):
        """Handle double-click to toggle selection"""
        item = self.tree.focus()
        if not item:
            return

        # Toggle selection
        values = self.tree.item(item, 'values')
        if len(values) < 2:
            return

        file_path = values[0]
        is_selected = values[1] == 'selected'

        if is_selected:
            # Deselect
            self._deselect_item(item, file_path)
        else:
            # Select
            self._select_item(item, file_path)

    def _select_item(self, item, file_path):
        """Select an item"""
        text = self.tree.item(item, 'text')
        new_text = text.replace('☐', '☑')
        self.tree.item(item, text=new_text, values=(file_path, 'selected'))

        if file_path:
            self.selected_files.add(file_path)

        # Select all children
        for child in self.tree.get_children(item):
            child_values = self.tree.item(child, 'values')
            if len(child_values) >= 1:
                self._select_item(child, child_values[0])

    def _deselect_item(self, item, file_path):
        """Deselect an item"""
        text = self.tree.item(item, 'text')
        new_text = text.replace('☑', '☐')
        self.tree.item(item, text=new_text, values=(file_path, 'deselected'))

        if file_path:
            self.selected_files.discard(file_path)

        # Deselect all children
        for child in self.tree.get_children(item):
            child_values = self.tree.item(child, 'values')
            if len(child_values) >= 1:
                self._deselect_item(child, child_values[0])

    def on_tree_select(self, event):
        """Handle tree selection for preview"""
        item = self.tree.focus()
        if not item:
            return

        values = self.tree.item(item, 'values')
        if len(values) < 1 or not values[0]:
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', "Select a document to preview")
            return

        file_path = values[0]
        is_selected = len(values) >= 2 and values[1] == 'selected'

        # Show preview
        preview = f"Preview of: {file_path}\n\n"
        preview += "Status: " + ("SELECTED" if is_selected else "NOT SELECTED") + " for generation\n\n"
        preview += "-" * 60 + "\n\n"
        preview += self._generate_preview(file_path)

        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert('1.0', preview)

    def _generate_preview(self, file_path: str) -> str:
        """Generate a preview of the document content"""
        if not self.extractor:
            return "No model loaded"

        parts = file_path.split('/')

        # Handle diagram images
        if file_path.endswith('.png'):
            diagram_name = parts[-1].replace('.png', '').replace('_', ' ').title()
            return f"📊 Diagram Image: {diagram_name}\n\n" \
                   f"Type: PNG Image\n" \
                   f"Location: {file_path}\n\n" \
                   f"This is a rendered UML diagram from the model.\n" \
                   f"The diagram will be generated as a PNG image and\n" \
                   f"embedded in the documentation.\n\n" \
                   f"Note: Image preview not available in this view.\n" \
                   f"The diagram will be visible when you open the\n" \
                   f"generated documentation in a markdown viewer."

        if file_path == 'index.md':
            return f"# Sparx Enterprise Architect Model Documentation\n\n" \
                   f"Generated: {self.extractor.use_cases[0].modified_date if self.extractor.use_cases else 'N/A'}\n\n" \
                   f"## Sections\n- Use Cases\n- Requirements\n- Components\n- Classes\n- Diagrams\n..."

        elif parts[0] == 'use-cases':
            if parts[1] == 'actors.md':
                preview = "# Actors\n\n"
                for actor in self.extractor.actors[:3]:
                    preview += f"## {actor.name}\n{actor.clean_note() or 'No description'}\n\n"
                return preview

            elif parts[1] == 'index.md':
                preview = "# Use Cases\n\n## Use Case List\n\n"
                for uc in self.extractor.use_cases[:5]:
                    preview += f"- {uc.name}\n"
                return preview

            else:
                # Individual use case
                for uc in self.extractor.use_cases:
                    if uc.name.lower().replace(' ', '-') == parts[1].replace('.md', ''):
                        return f"# {uc.name}\n\n**Package:** {uc.package_name}\n\n{uc.clean_note() or 'No description'}"

        elif parts[0] == 'requirements':
            if parts[1] == 'index.md':
                preview = "# Requirements\n\n## Requirements List\n\n"
                for req in self.extractor.requirements[:5]:
                    preview += f"- {req.name}\n"
                return preview
            else:
                # Individual requirement
                for req in self.extractor.requirements:
                    if req.name.lower().replace(' ', '-') == parts[1].replace('.md', ''):
                        return f"# {req.name}\n\n**Type:** {req.type}\n\n{req.clean_note() or 'No description'}"

        elif parts[0] == 'state-machines':
            if parts[1] == 'index.md':
                preview = "# State Machines\n\n## State Machine List\n\n"
                for sm in self.extractor.state_machines[:5]:
                    preview += f"- {sm.name}\n"
                return preview
            else:
                # Individual state machine
                for sm in self.extractor.state_machines:
                    if sm.name.lower().replace(' ', '-') == parts[1].replace('.md', '').replace('sm-', ''):
                        return f"# {sm.name}\n\n**Package:** {sm.package_name}\n\n{sm.clean_note() or 'No description'}"

        elif parts[0] == 'components':
            if parts[1] == 'index.md':
                preview = "# Components\n\n## Component List\n\n"
                for comp in self.extractor.components[:5]:
                    preview += f"- {comp.name}\n"
                return preview
            elif parts[1] == 'interfaces.md':
                return "# Component Interfaces\n\nProvided and required interfaces for all components."
            else:
                # Individual component
                for comp in self.extractor.components:
                    if comp.name.lower().replace(' ', '-') == parts[1].replace('.md', '').replace('comp-', ''):
                        return f"# {comp.name}\n\n**Package:** {comp.package_name}\n\n{comp.clean_note() or 'No description'}"

        elif parts[0] == 'classes':
            if parts[1] == 'index.md':
                preview = "# Classes and Modules\n\n## Class List\n\n"
                for cls in self.extractor.classes[:5]:
                    preview += f"- {cls.name} ({cls.package_name})\n"
                return preview
            elif len(parts) >= 3 and parts[2] == 'index.md':
                # Package index
                package_name = parts[1].title()
                preview = f"# {package_name} Package\n\n## Classes in this package:\n\n"
                for cls in self.extractor.classes:
                    if cls.package_name.lower() == parts[1]:
                        preview += f"- {cls.name}\n"
                return preview
            else:
                # Individual class
                class_name = parts[-1].replace('.md', '')
                for cls in self.extractor.classes:
                    if cls.name.lower().replace(' ', '-') == class_name:
                        attrs_count = len(cls.attributes) if cls.attributes else 0
                        ops_count = len(cls.operations) if cls.operations else 0
                        return f"# {cls.name}\n\n**Package:** {cls.package_name}\n**Type:** {cls.type}\n\n" \
                               f"Attributes: {attrs_count}\nOperations: {ops_count}\n\n" \
                               f"{cls.clean_note() or 'No description'}"

        elif parts[0] == 'reports':
            if parts[1] == 'index.md':
                return "# Reports\n\nQuality and analysis reports for the model."
            elif parts[1] == 'quality-report.md':
                return "# Quality Report\n\nDocumentation coverage and quality metrics for all model elements."
            elif parts[1] == 'dependencies.md':
                return "# Dependencies Report\n\nElement relationships and dependency analysis."

        return "(Preview not available for this document type)"

    def select_all(self):
        """Select all documents"""
        for item in self.tree.get_children():
            self._select_all_recursive(item)

    def _select_all_recursive(self, item):
        """Recursively select all items"""
        values = self.tree.item(item, 'values')
        if len(values) >= 1:
            self._select_item(item, values[0] if values[0] else '')

        for child in self.tree.get_children(item):
            self._select_all_recursive(child)

    def deselect_all(self):
        """Deselect all documents"""
        for item in self.tree.get_children():
            self._deselect_all_recursive(item)

    def _deselect_all_recursive(self, item):
        """Recursively deselect all items"""
        values = self.tree.item(item, 'values')
        if len(values) >= 1:
            self._deselect_item(item, values[0] if values[0] else '')

        for child in self.tree.get_children(item):
            self._deselect_all_recursive(child)

    def ask_create_folder(self, parent_dir: Path) -> Optional[Path]:
        """
        Ask user if they want to create a new folder in the selected directory

        Args:
            parent_dir: The parent directory selected by user

        Returns:
            Path to use for output (either parent_dir or new subdirectory),
            or None if cancelled
        """
        # Create a custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Output Directory")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()

        result = {'path': None}

        # Message
        ttk.Label(dialog, text="Selected directory:", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
        ttk.Label(dialog, text=str(parent_dir), font=('Arial', 9)).pack(pady=(0, 10))

        ttk.Label(dialog, text="Would you like to create a new folder for this documentation?").pack(pady=10)

        # Suggested folder name
        suggested_name = f"docs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        frame = ttk.Frame(dialog)
        frame.pack(pady=10, padx=20, fill=tk.X)

        ttk.Label(frame, text="New folder name:").pack(side=tk.LEFT)
        folder_entry = ttk.Entry(frame, width=30)
        folder_entry.insert(0, suggested_name)
        folder_entry.pack(side=tk.LEFT, padx=5)
        folder_entry.select_range(0, tk.END)
        folder_entry.focus()

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        def create_new_folder():
            folder_name = folder_entry.get().strip()
            if not folder_name:
                messagebox.showwarning("Invalid Name", "Please enter a folder name")
                return

            new_path = parent_dir / folder_name
            try:
                new_path.mkdir(parents=True, exist_ok=True)
                result['path'] = new_path
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder:\n{e}")

        def use_selected():
            result['path'] = parent_dir
            dialog.destroy()

        def cancel():
            result['path'] = None
            dialog.destroy()

        ttk.Button(button_frame, text="Create New Folder", command=create_new_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Use Selected Directory", command=use_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)

        # Handle Enter key
        def on_enter(event):
            create_new_folder()

        folder_entry.bind('<Return>', on_enter)

        # Wait for dialog to close
        dialog.wait_window()

        return result['path']

    def generate_documentation(self):
        """Generate selected documentation"""
        if not self.extractor:
            messagebox.showerror("Error", "No model loaded")
            return

        if not self.selected_files:
            messagebox.showwarning("Warning", "No documents selected")
            return

        # Ask for parent directory
        parent_dir = filedialog.askdirectory(title="Select Parent Directory for Documentation")
        if not parent_dir:
            return

        # Ask if user wants to create a new folder
        output_path = self.ask_create_folder(Path(parent_dir))
        if not output_path:
            return

        # Run generation in thread
        def generate_thread():
            try:
                self.status_label.config(text="Generating documentation...", foreground="blue")
                self.progress.start()
                self.generate_button.config(state=tk.DISABLED)

                # Import generators
                from sparx_ea_doc.generators import (
                    UseCaseGenerator,
                    StateMachineGenerator,
                    ComponentGenerator,
                    ClassGenerator,
                    RequirementGenerator
                )
                from sparx_ea_doc.quality_reporter import QualityReporter
                from sparx_ea_doc.diagram_renderer import DiagramRenderer
                from datetime import datetime

                # Use SelectiveFileWriter to filter file writes
                with SelectiveFileWriter(output_path, self.selected_files):
                    # Reopen database connection for generators
                    self.extractor.connect_db()

                    try:
                        # Render diagrams first
                        diagram_guid_to_png = {}
                        ea_diagrams_dir = self.ea_diagrams_var.get() if self.ea_diagrams_var.get() else None
                        diagram_renderer = DiagramRenderer(self.extractor, output_path, ea_diagrams_dir)

                        # Get all diagrams
                        cursor = self.extractor.conn.cursor()
                        cursor.execute("""
                            SELECT d.Diagram_ID, d.ea_guid, d.Name, p.Name as Package_Name
                            FROM t_diagram d
                            LEFT JOIN t_package p ON d.Package_ID = p.Package_ID
                            ORDER BY d.Name
                        """)

                        diagram_count = 0
                        for row in cursor.fetchall():
                            diagram_id = row['Diagram_ID']
                            diagram_guid = row['ea_guid']
                            diagram_name = row['Name']
                            package_name = row['Package_Name']

                            try:
                                # Render the diagram
                                png_path = diagram_renderer.render_diagram(diagram_id, diagram_name, package_name)
                                relative_path = png_path.relative_to(output_path)
                                diagram_guid_to_png[diagram_guid] = str(relative_path)
                                diagram_count += 1
                            except Exception as e:
                                logger.warning(f"Failed to render diagram {diagram_name}: {e}")

                        logger.info(f"Rendered {diagram_count} diagrams")

                        # Initialize generators with diagram mappings
                        uc_generator = UseCaseGenerator(self.extractor, output_path, diagram_guid_to_png=diagram_guid_to_png)
                        req_generator = RequirementGenerator(self.extractor, output_path)
                        sm_generator = StateMachineGenerator(self.extractor, output_path, diagram_guid_to_png=diagram_guid_to_png)
                        comp_generator = ComponentGenerator(self.extractor, output_path, diagram_guid_to_png=diagram_guid_to_png)
                        class_generator = ClassGenerator(self.extractor, output_path, diagram_guid_to_png=diagram_guid_to_png)

                        # Generate all documentation
                        uc_generator.generate()
                        req_generator.generate()
                        sm_generator.generate()
                        comp_generator.generate()
                        class_generator.generate()

                        # Generate quality reports
                        quality_reporter = QualityReporter(self.extractor, output_path, {})
                        quality_reporter.perform_quality_checks()
                        quality_reporter.generate_quality_report()
                        quality_reporter.generate_dependencies_report()

                        # Generate reports index
                        self._generate_reports_index(output_path, quality_reporter)

                        # Generate main index
                        self._generate_index(output_path, quality_reporter)

                    finally:
                        self.extractor.close_db()

                # Generate HTML if requested
                if self.generate_html_var.get():
                    try:
                        from sparx_ea_doc.html_generator import HTMLGenerator

                        logger.info("Generating HTML documentation...")
                        html_gen = HTMLGenerator(output_path)
                        stats = html_gen.generate_all()

                        logger.info(f"HTML generation complete: {stats['converted']} files converted")

                    except ImportError as e:
                        logger.error(f"HTML generation requires markdown library: {e}")
                        logger.error("Install with: pip install markdown")
                    except Exception as e:
                        logger.error(f"HTML generation failed: {e}", exc_info=True)

                self.root.after(0, lambda: self.generation_complete(output_path))

            except Exception as e:
                logger.error(f"Generation failed: {e}", exc_info=True)
                self.root.after(0, lambda: self.generation_error(str(e)))

        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()

    def _generate_reports_index(self, output_dir: Path, quality_reporter):
        """Generate reports index document"""
        reports_dir = output_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)

        index_content = "# Reports\n\n"
        index_content += "This section contains quality and analysis reports for the model.\n\n"

        index_content += "## Available Reports\n\n"
        index_content += "- [Quality Report](quality-report.md) - Documentation coverage and quality metrics\n"
        index_content += "- [Dependencies](dependencies.md) - Element relationships and dependency analysis\n\n"

        index_content += "## Summary\n\n"
        if quality_reporter.quality_metrics:
            total_elements = quality_reporter.quality_metrics.get('total_elements', 0)
            undocumented = len(quality_reporter.quality_metrics.get('undocumented_elements', []))
            doc_rate = quality_reporter.quality_metrics.get('documentation_rate', 0)

            index_content += f"- **Total Elements:** {total_elements}\n"
            index_content += f"- **Undocumented Elements:** {undocumented}\n"
            index_content += f"- **Documentation Rate:** {doc_rate:.1f}%\n\n"

        with open(reports_dir / 'index.md', 'w') as f:
            f.write(index_content)

    def _generate_index(self, output_dir: Path, quality_reporter):
        """Generate main index/navigation document"""
        from datetime import datetime

        index_content = "# Sparx Enterprise Architect Model Documentation\n\n"
        index_content += f"**Source File:** {self.qea_path.name}\n\n"
        index_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        index_content += "## Overview\n\n"
        index_content += "This documentation was automatically generated from the Sparx Enterprise Architect model. "
        index_content += "Navigate through the sections below to explore different aspects of the system architecture.\n\n"

        # Model Statistics
        index_content += "## Model Statistics\n\n"
        index_content += f"- **Total Elements:** {quality_reporter.quality_metrics['total_elements']}\n"
        index_content += f"- **Total Packages:** {len(self.extractor.packages)}\n"
        index_content += f"- **Total Relationships:** {len(self.extractor.connectors)}\n\n"

        # Documentation Sections
        index_content += "## Documentation Sections\n\n"

        if self.extractor.use_cases:
            index_content += f"### [Use Cases](use-cases/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.use_cases)} use cases"
            if self.extractor.actors:
                index_content += f" and {len(self.extractor.actors)} actors"
            index_content += ".\n\n"

        if self.extractor.requirements:
            index_content += f"### [Requirements](requirements/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.requirements)} requirements.\n\n"

        if self.extractor.state_machines:
            index_content += f"### [State Machines](state-machines/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.state_machines)} state machines.\n\n"

        if self.extractor.components:
            index_content += f"### [Components](components/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.components)} components"
            if self.extractor.interfaces:
                index_content += f" and {len(self.extractor.interfaces)} interfaces"
            index_content += ".\n\n"

        if self.extractor.classes:
            index_content += f"### [Classes and Modules](classes/index.md)\n\n"
            index_content += f"Contains {len(self.extractor.classes)} classes"
            if self.extractor.interfaces:
                index_content += f", {len(self.extractor.interfaces)} interfaces"
            if self.extractor.enumerations:
                index_content += f", and {len(self.extractor.enumerations)} enumerations"
            index_content += ".\n\n"

        # Reports
        index_content += "### [Reports](reports/quality-report.md)\n\n"
        index_content += "Quality metrics and dependency analysis.\n\n"
        index_content += f"- [Quality Report](reports/quality-report.md)\n"
        index_content += f"- [Dependencies](reports/dependencies.md)\n\n"

        with open(output_dir / 'index.md', 'w') as f:
            f.write(index_content)

    def generation_complete(self, output_path):
        """Handle successful generation"""
        self.progress.stop()
        self.generate_button.config(state=tk.NORMAL)
        self.status_label.config(
            text=f"Generated {len(self.selected_files)} documents to {output_path}",
            foreground="green"
        )
        messagebox.showinfo("Success",
                          f"Documentation generated successfully!\n\n"
                          f"Generated {len(self.selected_files)} documents\n"
                          f"Output: {output_path}")

    def generation_error(self, error_msg):
        """Handle generation error"""
        self.progress.stop()
        self.generate_button.config(state=tk.NORMAL)
        self.status_label.config(text="Generation failed", foreground="red")
        messagebox.showerror("Error", f"Documentation generation failed:\n{error_msg}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SparxDocGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
