#!/usr/bin/env python3
"""
Enterprise Architect Diagram Extractor - Final Working Version
Extracts all diagrams from EA repository (.qea) with proper recursive search
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

try:
    import win32com.client
    import pythoncom
except ImportError:
    print("Error: pywin32 required. Install with: pip install pywin32")
    sys.exit(1)


class EADiagramExtractor:
    """Extract all diagrams from EA repository"""
    
    def __init__(self, repo_path, output_dir="diagrams"):
        self.repo_path = Path(repo_path).absolute()
        self.output_dir = Path(output_dir)
        self.repository = None
        self.project = None
        self.success_count = 0
        self.fail_count = 0
        self.total_count = 0
        
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository not found: {self.repo_path}")
        
        if not str(self.repo_path).lower().endswith('.qea'):
            print("Warning: File doesn't have .qea extension")
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Repository: {self.repo_path}")
        print(f"Output: {self.output_dir.absolute()}\n")
    
    def connect(self):
        """Connect to EA repository"""
        try:
            # Initialize COM
            pythoncom.CoInitialize()
            
            print("Connecting to Enterprise Architect...")
            ea = win32com.client.Dispatch("EA.App")
            self.repository = ea.Repository
            
            # Open repository
            if not self.repository.OpenFile(str(self.repo_path)):
                print("Failed to open repository")
                return False
            
            # Get project interface
            self.project = self.repository.GetProjectInterface()
            
            print(f"Connected successfully")
            print(f"Repository type: {self.repository.RepositoryType()}\n")
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def format_date(self, date):
        """Format date for filename"""
        if not date:
            return "nodate"
        
        date_str = str(date)
        
        # Try parsing common EA date formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y%m%d_%H%M%S")
            except:
                continue
        
        # Fallback: clean up for filename
        cleaned = date_str.replace(" ", "_").replace(":", "").replace("-", "").replace("/", "")
        return cleaned if cleaned else "nodate"
    
    def export_diagram(self, diagram, package_name=""):
        """Export a single diagram using the best available method"""
        self.total_count += 1
        
        try:
            # Get diagram info
            diagram_name = diagram.Name
            diagram_guid = str(diagram.DiagramGUID)
            diagram_type = diagram.Type
            modified_date = self.format_date(diagram.ModifiedDate)
            
            # Clean GUID for filename (remove braces)
            clean_guid = diagram_guid.strip('{}')
            
            # Generate filename
            filename = f"{clean_guid}-{modified_date}.png"
            filepath = self.output_dir / filename
            
            # Try Method 1: Direct export with GUID
            success = False
            method_used = ""
            
            try:
                # PutDiagramImageToFile(GUID, FilePath, ImageType)
                # ImageType: 0=EMF, 1=BMP, 2=GIF, 3=PNG, 4=JPG
                success = self.project.PutDiagramImageToFile(
                    diagram_guid,     # GUID with braces
                    str(filepath),    # Full path as string
                    3                 # PNG format
                )
                if success and filepath.exists():
                    method_used = "direct"
                else:
                    success = False
            except:
                success = False
            
            # Try Method 2: Clipboard method if direct failed
            if not success:
                try:
                    # Open diagram
                    self.repository.OpenDiagram(diagram.DiagramID)
                    
                    # Put on clipboard
                    self.project.PutDiagramImageOnClipboard(diagram_guid, 0)
                    
                    # Save from clipboard
                    success = self.project.SaveDiagramImageToFile(str(filepath))
                    
                    # Close diagram
                    self.repository.CloseDiagram(diagram.DiagramID)
                    
                    if success and filepath.exists():
                        method_used = "clipboard"
                    else:
                        success = False
                        
                except:
                    success = False
                    try:
                        self.repository.CloseDiagram(diagram.DiagramID)
                    except:
                        pass
            
            # Report result
            if success and filepath.exists():
                self.success_count += 1
                size = filepath.stat().st_size
                print(f"  [{self.total_count:3d}] ✓ {diagram_name}")
                print(f"        → {filename} ({size:,} bytes) [{method_used}]")
            else:
                self.fail_count += 1
                print(f"  [{self.total_count:3d}] ✗ {diagram_name} - Export failed")
                
        except Exception as e:
            self.fail_count += 1
            print(f"  [{self.total_count:3d}] ✗ {diagram.Name} - Error: {str(e)[:50]}")
    
    def process_package(self, package, level=0):
        """Recursively process package and all sub-packages"""
        indent = "  " * level
        
        # Show package info
        diagram_count = package.Diagrams.Count
        subpackage_count = package.Packages.Count
        
        if diagram_count > 0 or subpackage_count > 0:
            print(f"{indent}📦 {package.Name}")
            if diagram_count > 0:
                print(f"{indent}   ({diagram_count} diagram{'s' if diagram_count != 1 else ''})")
        
        # Export diagrams in this package
        for i in range(diagram_count):
            diagram = package.Diagrams.GetAt(i)
            self.export_diagram(diagram, package.Name)
        
        # Process sub-packages recursively
        for i in range(subpackage_count):
            subpackage = package.Packages.GetAt(i)
            self.process_package(subpackage, level + 1)
    
    def extract(self):
        """Main extraction process"""
        if not self.connect():
            return False
        
        print("Searching for diagrams...\n")
        
        try:
            # Process all models
            models = self.repository.Models
            model_count = models.Count
            
            print(f"Found {model_count} model{'s' if model_count != 1 else ''}\n")
            
            for i in range(model_count):
                model = models.GetAt(i)
                print(f"📁 Model: {model.Name}")
                self.process_package(model, 1)
                print()  # Empty line between models
            
            # Summary
            print("="*60)
            print("EXTRACTION COMPLETE")
            print("="*60)
            print(f"Total diagrams found: {self.total_count}")
            print(f"Successfully exported: {self.success_count}")
            if self.fail_count > 0:
                print(f"Failed: {self.fail_count}")
            
            if self.success_count > 0:
                print(f"\nDiagrams saved to: {self.output_dir.absolute()}")
            
            return True
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return False
            
        finally:
            self.disconnect()
    
    def disconnect(self):
        """Close repository connection"""
        if self.repository:
            try:
                self.repository.CloseFile()
                self.repository.Exit()
                print("\nRepository connection closed")
            except:
                pass
            finally:
                self.repository = None
                self.project = None


def main():
    parser = argparse.ArgumentParser(
        description="Extract all diagrams from Enterprise Architect repository (.qea)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output format: {ea_guid}-{ModifiedDate}.png

Examples:
  %(prog)s repository.qea
  %(prog)s repository.qea -o extracted_diagrams
  %(prog)s "C:\\Projects\\MyProject.qea" -o "C:\\Diagrams"

Requirements:
  - Windows OS
  - Enterprise Architect installed
  - pywin32 package (pip install pywin32)
        """
    )
    
    parser.add_argument(
        "repository",
        help="Path to EA repository file (.qea format)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="diagrams",
        help="Output directory for diagrams (default: ./diagrams)"
    )
    
    args = parser.parse_args()
    
    try:
        print("="*60)
        print("Enterprise Architect Diagram Extractor")
        print("="*60)
        print()
        
        extractor = EADiagramExtractor(args.repository, args.output)
        
        if not extractor.extract():
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nExtraction cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()