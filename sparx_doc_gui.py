#!/usr/bin/env python3
"""
Sparx Enterprise Architect Documentation Generator - GUI
Interactive GUI for selective document generation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import logging
from typing import Dict, List, Set, Optional
import threading

from sparx_ea_doc.extractor import SparxExtractor
from sparx_ea_doc.selective_generator import SelectiveGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentTreeBuilder:
    """
    Builds the document tree structure by inspecting what would be generated
    """

    def __init__(self, extractor):
        self.extractor = extractor

    def build_tree_structure(self) -> Dict:
        """Build the complete tree structure of all possible documents"""
        tree = {
            'index.md': {'type': 'file', 'path': 'index.md'},
            'use-cases': {
                'type': 'folder',
                'children': {}
            },
            'state-machines': {
                'type': 'folder',
                'children': {}
            },
            'components': {
                'type': 'folder',
                'children': {}
            },
            'classes': {
                'type': 'folder',
                'children': {}
            },
            'reports': {
                'type': 'folder',
                'children': {
                    'quality-report.md': {'type': 'file', 'path': 'reports/quality-report.md'},
                    'dependencies.md': {'type': 'file', 'path': 'reports/dependencies.md'}
                }
            }
        }

        # Add use cases
        tree['use-cases']['children']['index.md'] = {
            'type': 'file',
            'path': 'use-cases/index.md'
        }
        tree['use-cases']['children']['actors.md'] = {
            'type': 'file',
            'path': 'use-cases/actors.md'
        }

        for uc in self.extractor.use_cases:
            filename = f"{uc.name.lower().replace(' ', '-')}.md"
            tree['use-cases']['children'][filename] = {
                'type': 'file',
                'path': f'use-cases/{filename}',
                'title': uc.name
            }

        # Add state machines
        tree['state-machines']['children']['index.md'] = {
            'type': 'file',
            'path': 'state-machines/index.md'
        }

        for sm in self.extractor.state_machines:
            filename = f"sm-{sm.name.lower().replace(' ', '-')}.md"
            tree['state-machines']['children'][filename] = {
                'type': 'file',
                'path': f'state-machines/{filename}',
                'title': sm.name
            }

        # Add components
        tree['components']['children']['index.md'] = {
            'type': 'file',
            'path': 'components/index.md'
        }
        tree['components']['children']['interfaces.md'] = {
            'type': 'file',
            'path': 'components/interfaces.md'
        }

        for comp in self.extractor.components:
            filename = f"comp-{comp.name.lower().replace(' ', '-')}.md"
            tree['components']['children'][filename] = {
                'type': 'file',
                'path': f'components/{filename}',
                'title': comp.name
            }

        # Add classes (organized by package)
        tree['classes']['children']['index.md'] = {
            'type': 'file',
            'path': 'classes/index.md'
        }

        # Group classes by package
        classes_by_package = {}
        for cls in self.extractor.classes:
            package_name = cls.package_name if cls.package_name else 'root'
            if package_name not in classes_by_package:
                classes_by_package[package_name] = []
            classes_by_package[package_name].append(cls)

        for package_name, classes in classes_by_package.items():
            safe_package = package_name.lower().replace(' ', '-')

            if safe_package not in tree['classes']['children']:
                tree['classes']['children'][safe_package] = {
                    'type': 'folder',
                    'children': {}
                }

            for cls in classes:
                filename = f"{cls.name.lower().replace(' ', '-')}.md"
                tree['classes']['children'][safe_package]['children'][filename] = {
                    'type': 'file',
                    'path': f'classes/{safe_package}/{filename}',
                    'title': cls.name
                }

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

        # Button bar
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=2)

        # Tree view with scrollbar
        tree_scroll_frame = ttk.Frame(left_frame)
        tree_scroll_frame.pack(fill=tk.BOTH, expand=True)

        tree_scrollbar = ttk.Scrollbar(tree_scroll_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_scroll_frame, yscrollcommand=tree_scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        tree_scrollbar.config(command=self.tree.yview)

        self.tree.bind('<Button-1>', self.on_tree_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Right panel - Markdown preview
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="Document Preview", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)

        self.preview_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=('Courier', 10))
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # Bottom frame for actions
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)

        self.generate_button = ttk.Button(
            bottom_frame,
            text="Generate Selected Documents",
            command=self.generate_documentation,
            state=tk.DISABLED
        )
        self.generate_button.pack(side=tk.RIGHT)

        self.status_label = ttk.Label(bottom_frame, text="Ready", foreground="blue")
        self.status_label.pack(side=tk.LEFT)

        # Progress bar
        self.progress = ttk.Progressbar(bottom_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    def open_file(self):
        """Open a .qea file and load its structure"""
        filename = filedialog.askopenfilename(
            title="Select Sparx EA .qea File",
            filetypes=[("QEA Files", "*.qea"), ("All Files", "*.*")]
        )

        if filename:
            self.qea_path = Path(filename)
            self.file_label.config(text=self.qea_path.name, foreground="black")
            self.load_model()

    def load_model(self):
        """Load the model and build the document tree"""
        if not self.qea_path:
            return

        self.status_label.config(text="Loading model...", foreground="blue")
        self.progress.start()
        self.root.update()

        try:
            # Extract model data
            self.extractor = SparxExtractor(self.qea_path)
            self.extractor.extract_all()

            # Build document tree structure
            builder = DocumentTreeBuilder(self.extractor)
            self.tree_structure = builder.build_tree_structure()

            # Populate tree view
            self.populate_tree()

            # Select all by default
            self.select_all()

            self.status_label.config(text="Model loaded successfully", foreground="green")
            self.generate_button.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.status_label.config(text="Error loading model", foreground="red")
            logger.error(f"Error loading model: {e}", exc_info=True)

        finally:
            self.progress.stop()

    def populate_tree(self):
        """Populate the tree view with document structure"""
        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add columns
        self.tree['columns'] = ('path',)
        self.tree.column('#0', width=400)
        self.tree.column('path', width=0, stretch=False)

        # Hide path column (used internally)
        self.tree['displaycolumns'] = ()

        # Add items recursively
        def add_items(parent, structure, prefix=''):
            for name, item in structure.items():
                if item['type'] == 'folder':
                    # Add folder
                    folder_id = self.tree.insert(
                        parent,
                        'end',
                        text=f"☐ {name}/",
                        values=(f"{prefix}{name}/",),
                        tags=('folder',)
                    )
                    # Add children
                    if 'children' in item:
                        add_items(folder_id, item['children'], f"{prefix}{name}/")
                else:
                    # Add file
                    title = item.get('title', name)
                    self.tree.insert(
                        parent,
                        'end',
                        text=f"☐ {title}",
                        values=(item['path'],),
                        tags=('file',)
                    )

        add_items('', self.tree_structure)

        # Expand all nodes
        def expand_all(item=''):
            children = self.tree.get_children(item)
            for child in children:
                self.tree.item(child, open=True)
                expand_all(child)

        expand_all()

    def on_tree_click(self, event):
        """Handle tree item clicks for toggling checkboxes"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "tree":
            item = self.tree.identify_row(event.y)
            if item:
                self.toggle_item(item)

    def toggle_item(self, item):
        """Toggle checkbox for an item"""
        text = self.tree.item(item, 'text')
        is_checked = text.startswith('☑')

        # Toggle check state
        new_text = text.replace('☑', '☐') if is_checked else text.replace('☐', '☑')
        self.tree.item(item, text=new_text)

        # Update selected files
        path = self.tree.item(item, 'values')[0]
        tags = self.tree.item(item, 'tags')

        if 'file' in tags:
            if is_checked:
                self.selected_files.discard(path)
            else:
                self.selected_files.add(path)
        elif 'folder' in tags:
            # Toggle all children
            self.toggle_children(item, not is_checked)

        self.update_status()

    def toggle_children(self, parent, checked):
        """Recursively toggle all children of a folder"""
        for child in self.tree.get_children(parent):
            text = self.tree.item(child, 'text')
            new_text = text.replace('☐', '☑') if checked else text.replace('☑', '☐')
            self.tree.item(child, text=new_text)

            path = self.tree.item(child, 'values')[0]
            tags = self.tree.item(child, 'tags')

            if 'file' in tags:
                if checked:
                    self.selected_files.add(path)
                else:
                    self.selected_files.discard(path)
            elif 'folder' in tags:
                self.toggle_children(child, checked)

    def on_tree_select(self, event):
        """Handle tree item selection for preview"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            path = self.tree.item(item, 'values')[0]
            tags = self.tree.item(item, 'tags')

            if 'file' in tags:
                self.show_preview(path)

    def show_preview(self, file_path):
        """Show preview of a document"""
        self.preview_text.delete('1.0', tk.END)

        # Generate actual preview content
        try:
            preview = self._generate_preview_content(file_path)
            if preview:
                self.preview_text.insert('1.0', preview)
            else:
                self.preview_text.insert('1.0', f"Preview of: {file_path}\n\nNo preview available.")
        except Exception as e:
            self.preview_text.insert('1.0', f"Preview of: {file_path}\n\nError generating preview:\n{str(e)}")

    def _generate_preview_content(self, file_path: str) -> Optional[str]:
        """Generate preview content for a specific file"""
        from sparx_ea_doc.generators import (
            UseCaseGenerator,
            StateMachineGenerator,
            ComponentGenerator,
            ClassGenerator
        )
        from tempfile import TemporaryDirectory

        # Determine document type from path
        parts = file_path.split('/')

        if not self.extractor:
            return None

        try:
            if file_path == 'index.md':
                # Generate main index preview
                from datetime import datetime
                preview = "# Sparx Enterprise Architect Model Documentation\n\n"
                preview += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                preview += "## Documentation Sections\n\n"
                if self.extractor.use_cases:
                    preview += f"### [Use Cases](use-cases/index.md)\n\nContains {len(self.extractor.use_cases)} use cases.\n\n"
                if self.extractor.state_machines:
                    preview += f"### [State Machines](state-machines/index.md)\n\nContains {len(self.extractor.state_machines)} state machines.\n\n"
                if self.extractor.components:
                    preview += f"### [Components](components/index.md)\n\nContains {len(self.extractor.components)} components.\n\n"
                if self.extractor.classes:
                    preview += f"### [Classes](classes/index.md)\n\nContains {len(self.extractor.classes)} classes.\n\n"
                return preview

            elif parts[0] == 'use-cases':
                # Use case preview
                if parts[1] == 'actors.md':
                    preview = "# Actors\n\nThis document lists all actors in the system.\n\n"
                    for actor in self.extractor.actors[:5]:  # Show first 5
                        preview += f"## {actor.name}\n\n"
                        if actor.stereotype:
                            preview += f"**Stereotype:** <<{actor.stereotype}>>\n\n"
                        preview += f"**Description:** {actor.clean_note() or 'No description available'}\n\n"
                    if len(self.extractor.actors) > 5:
                        preview += f"\n... and {len(self.extractor.actors) - 5} more actors\n"
                    return preview

                elif parts[1] == 'index.md':
                    preview = "# Use Cases\n\nThis document provides an overview of all use cases in the system.\n\n"
                    preview += "## Use Case List\n\n"
                    for uc in self.extractor.use_cases:
                        preview += f"- {uc.name}\n"
                    return preview

                else:
                    # Individual use case
                    uc_name = parts[1].replace('.md', '').replace('-', ' ')
                    for uc in self.extractor.use_cases:
                        if uc.name.lower().replace(' ', '-') == parts[1].replace('.md', ''):
                            with TemporaryDirectory() as temp_dir:
                                temp_path = Path(temp_dir)
                                gen = UseCaseGenerator(self.extractor, temp_path)
                                return gen._generate_single_use_case(uc)

            elif parts[0] == 'state-machines':
                if parts[1] == 'index.md':
                    preview = "# State Machines\n\nThis document provides an overview of all state machines in the system.\n\n"
                    preview += "## State Machine List\n\n"
                    for sm in self.extractor.state_machines:
                        preview += f"- {sm.name}\n"
                    return preview
                else:
                    # Individual state machine
                    for sm in self.extractor.state_machines:
                        if f"sm-{sm.name.lower().replace(' ', '-')}" == parts[1].replace('.md', ''):
                            with TemporaryDirectory() as temp_dir:
                                temp_path = Path(temp_dir)
                                gen = StateMachineGenerator(self.extractor, temp_path)
                                return gen._generate_single_state_machine(sm)

            elif parts[0] == 'components':
                if parts[1] == 'index.md':
                    preview = "# Components\n\nThis document provides an overview of all components in the system.\n\n"
                    preview += "## Component List\n\n"
                    for comp in self.extractor.components:
                        preview += f"- {comp.name}\n"
                    return preview
                elif parts[1] == 'interfaces.md':
                    preview = "# Component Interfaces\n\n"
                    for iface in self.extractor.interfaces[:5]:
                        preview += f"## {iface.name}\n\n"
                        preview += f"**Description:** {iface.clean_note() or 'No description available'}\n\n"
                    return preview
                else:
                    # Individual component
                    for comp in self.extractor.components:
                        if f"comp-{comp.name.lower().replace(' ', '-')}" == parts[1].replace('.md', ''):
                            with TemporaryDirectory() as temp_dir:
                                temp_path = Path(temp_dir)
                                gen = ComponentGenerator(self.extractor, temp_path)
                                return gen._generate_single_component(comp)

            elif parts[0] == 'classes':
                if parts[1] == 'index.md':
                    preview = "# Classes and Modules\n\nThis document provides an overview of all classes in the system.\n\n"
                    preview += "## Packages\n\n"
                    packages = set(cls.package_name for cls in self.extractor.classes)
                    for pkg in sorted(packages):
                        preview += f"### {pkg}\n\n"
                        pkg_classes = [cls for cls in self.extractor.classes if cls.package_name == pkg]
                        for cls in sorted(pkg_classes, key=lambda x: x.name):
                            preview += f"- {cls.name}\n"
                        preview += "\n"
                    return preview
                elif len(parts) == 3:
                    # Individual class
                    for cls in self.extractor.classes:
                        if cls.name.lower().replace(' ', '-') == parts[2].replace('.md', ''):
                            with TemporaryDirectory() as temp_dir:
                                temp_path = Path(temp_dir)
                                gen = ClassGenerator(self.extractor, temp_path)
                                return gen._generate_single_class(cls)

            elif parts[0] == 'reports':
                if parts[1] == 'quality-report.md':
                    return "# Quality Report\n\n(Quality report preview would be generated here)\n\nThis report shows documentation coverage and quality metrics."
                elif parts[1] == 'dependencies.md':
                    return "# Dependencies Report\n\n(Dependencies report preview would be generated here)\n\nThis report shows relationships between components."

        except Exception as e:
            logger.error(f"Error generating preview for {file_path}: {e}")
            return f"# Preview Error\n\nCould not generate preview:\n{str(e)}"

        return None

    def select_all(self):
        """Select all documents"""
        def select_items(parent=''):
            for item in self.tree.get_children(parent):
                text = self.tree.item(item, 'text')
                new_text = text.replace('☐', '☑')
                self.tree.item(item, text=new_text)

                path = self.tree.item(item, 'values')[0]
                tags = self.tree.item(item, 'tags')

                if 'file' in tags:
                    self.selected_files.add(path)

                select_items(item)

        select_items()
        self.update_status()

    def deselect_all(self):
        """Deselect all documents"""
        def deselect_items(parent=''):
            for item in self.tree.get_children(parent):
                text = self.tree.item(item, 'text')
                new_text = text.replace('☑', '☐')
                self.tree.item(item, text=new_text)

                deselect_items(item)

        deselect_items()
        self.selected_files.clear()
        self.update_status()

    def update_status(self):
        """Update status label with selection count"""
        count = len(self.selected_files)
        self.status_label.config(
            text=f"{count} document(s) selected",
            foreground="blue"
        )

    def generate_documentation(self):
        """Generate selected documentation"""
        if not self.selected_files:
            messagebox.showwarning("No Selection", "Please select at least one document to generate.")
            return

        # Ask for output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return

        output_path = Path(output_dir)

        # Run generation in a thread to avoid blocking UI
        def generate_thread():
            try:
                self.status_label.config(text="Generating documentation...", foreground="blue")
                self.progress.start()
                self.generate_button.config(state=tk.DISABLED)

                # Generate documentation
                generator = SelectiveGenerator(self.extractor, output_path, self.selected_files)
                generator.generate_all(progress_callback=self.update_progress)

                self.root.after(0, lambda: self.generation_complete(output_path))

            except Exception as e:
                self.root.after(0, lambda: self.generation_error(str(e)))

        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()

    def update_progress(self, message):
        """Update progress message"""
        self.root.after(0, lambda: self.status_label.config(text=message))

    def generation_complete(self, output_path):
        """Called when generation is complete"""
        self.progress.stop()
        self.generate_button.config(state=tk.NORMAL)
        self.status_label.config(text="Generation complete!", foreground="green")

        messagebox.showinfo(
            "Success",
            f"Documentation generated successfully!\n\nOutput directory: {output_path}"
        )

    def generation_error(self, error_msg):
        """Called when generation fails"""
        self.progress.stop()
        self.generate_button.config(state=tk.NORMAL)
        self.status_label.config(text="Generation failed", foreground="red")

        messagebox.showerror("Error", f"Failed to generate documentation:\n\n{error_msg}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SparxDocGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
