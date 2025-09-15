"""
Project creation and loading dialogs for CurioShelf
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QFileDialog, QMessageBox,
    QGroupBox, QTabWidget, QListWidget, QListWidgetItem, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from pathlib import Path
from typing import Optional

from curioshelf.project_manager import ProjectManager, ProjectInfo


class ProjectDialog(QDialog):
    """Main project dialog with tabs for create/load/import"""
    
    project_created = Signal(Path, ProjectInfo)  # project_path, project_info
    project_loaded = Signal(Path)  # project_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_manager = ProjectManager()
        self.setup_ui()
        self.setWindowTitle("Project Management")
        self.setModal(True)
        self.resize(600, 500)
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Create tabs
        self.create_tab = CreateProjectTab(self)
        self.load_tab = LoadProjectTab(self)
        self.import_tab = ImportProjectTab(self)
        
        tab_widget.addTab(self.create_tab, "Create New Project")
        tab_widget.addTab(self.load_tab, "Load Existing Project")
        tab_widget.addTab(self.import_tab, "Import Project")
        
        # Connect signals
        self.create_tab.project_created.connect(self.project_created.emit)
        self.load_tab.project_loaded.connect(self.project_loaded.emit)
        self.import_tab.project_loaded.connect(self.project_loaded.emit)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class CreateProjectTab(QDialog):
    """Tab for creating new projects"""
    
    project_created = Signal(Path, ProjectInfo)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the create project UI"""
        layout = QVBoxLayout(self)
        
        # Project details group
        details_group = QGroupBox("Project Details")
        details_layout = QFormLayout(details_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter project name")
        details_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Enter project description (optional)")
        details_layout.addRow("Description:", self.description_edit)
        
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Enter author name (optional)")
        details_layout.addRow("Author:", self.author_edit)
        
        layout.addWidget(details_group)
        
        # Project location group
        location_group = QGroupBox("Project Location")
        location_layout = QVBoxLayout(location_group)
        
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select project directory")
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        path_layout.addWidget(browse_btn)
        
        location_layout.addLayout(path_layout)
        layout.addWidget(location_group)
        
        # Create button
        create_btn = QPushButton("Create Project")
        create_btn.clicked.connect(self.create_project)
        create_btn.setMinimumHeight(40)
        layout.addWidget(create_btn)
    
    def browse_directory(self):
        """Browse for project directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Project Directory"
        )
        if directory:
            self.path_edit.setText(directory)
    
    def create_project(self):
        """Create the new project"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a project name")
            return
        
        project_path = Path(self.path_edit.text().strip())
        if not project_path:
            QMessageBox.warning(self, "Error", "Please select a project directory")
            return
        
        # Create project info
        project_info = ProjectInfo(
            name=name,
            description=self.description_edit.toPlainText().strip(),
            author=self.author_edit.text().strip()
        )
        
        # Create project directory
        full_project_path = project_path / name
        if full_project_path.exists():
            reply = QMessageBox.question(
                self, "Directory Exists",
                f"Directory '{full_project_path}' already exists. Overwrite?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Create the project
        if self.parent().project_manager.create_project(full_project_path, project_info):
            self.project_created.emit(full_project_path, project_info)
            QMessageBox.information(self, "Success", f"Project '{name}' created successfully!")
            self.parent().accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to create project")


class LoadProjectTab(QDialog):
    """Tab for loading existing projects"""
    
    project_loaded = Signal(Path)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.refresh_project_list()
    
    def setup_ui(self):
        """Setup the load project UI"""
        layout = QVBoxLayout(self)
        
        # Recent projects group
        recent_group = QGroupBox("Recent Projects")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.itemDoubleClicked.connect(self.load_selected_project)
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_group)
        
        # Browse for project
        browse_group = QGroupBox("Browse for Project")
        browse_layout = QVBoxLayout(browse_group)
        
        browse_btn = QPushButton("Browse for Project Directory...")
        browse_btn.clicked.connect(self.browse_project)
        browse_layout.addWidget(browse_btn)
        
        layout.addWidget(browse_group)
        
        # Load button
        load_btn = QPushButton("Load Selected Project")
        load_btn.clicked.connect(self.load_selected_project)
        load_btn.setMinimumHeight(40)
        layout.addWidget(load_btn)
    
    def refresh_project_list(self):
        """Refresh the list of recent projects"""
        # For now, just show a placeholder
        # In a real implementation, this would read from a recent projects file
        self.recent_list.clear()
        self.recent_list.addItem("No recent projects found")
    
    def browse_project(self):
        """Browse for a project directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Project Directory"
        )
        if directory:
            project_path = Path(directory)
            if self.parent().project_manager.load_project(project_path):
                self.project_loaded.emit(project_path)
                self.parent().accept()
            else:
                QMessageBox.warning(self, "Error", "Selected directory is not a valid CurioShelf project")
    
    def load_selected_project(self):
        """Load the selected project"""
        current_item = self.recent_list.currentItem()
        if current_item and current_item.text() != "No recent projects found":
            # In a real implementation, this would load the project path from the item data
            pass


class ImportProjectTab(QDialog):
    """Tab for importing projects from zip files"""
    
    project_loaded = Signal(Path)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the import project UI"""
        layout = QVBoxLayout(self)
        
        # Import file group
        import_group = QGroupBox("Import Project File")
        import_layout = QVBoxLayout(import_group)
        
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("Select project zip file")
        file_layout.addWidget(self.file_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_zip_file)
        file_layout.addWidget(browse_btn)
        
        import_layout.addLayout(file_layout)
        layout.addWidget(import_group)
        
        # Extract location group
        location_group = QGroupBox("Extract To")
        location_layout = QVBoxLayout(location_group)
        
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select extraction directory")
        path_layout.addWidget(self.path_edit)
        
        browse_path_btn = QPushButton("Browse...")
        browse_path_btn.clicked.connect(self.browse_extract_directory)
        path_layout.addWidget(browse_path_btn)
        
        location_layout.addLayout(path_layout)
        layout.addWidget(location_group)
        
        # Import button
        import_btn = QPushButton("Import Project")
        import_btn.clicked.connect(self.import_project)
        import_btn.setMinimumHeight(40)
        layout.addWidget(import_btn)
    
    def browse_zip_file(self):
        """Browse for zip file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Project Zip File", "", "Zip Files (*.zip)"
        )
        if file_path:
            self.file_edit.setText(file_path)
    
    def browse_extract_directory(self):
        """Browse for extract directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Extract Directory"
        )
        if directory:
            self.path_edit.setText(directory)
    
    def import_project(self):
        """Import the project"""
        zip_path = Path(self.file_edit.text().strip())
        extract_path = Path(self.path_edit.text().strip())
        
        if not zip_path.exists():
            QMessageBox.warning(self, "Error", "Please select a valid zip file")
            return
        
        if not extract_path:
            QMessageBox.warning(self, "Error", "Please select an extraction directory")
            return
        
        # Import the project
        if self.parent().project_manager.import_project(zip_path, extract_path):
            # Find the extracted project directory
            # For now, assume it's the first subdirectory
            project_dirs = [d for d in extract_path.iterdir() if d.is_dir()]
            if project_dirs:
                self.project_loaded.emit(project_dirs[0])
                QMessageBox.information(self, "Success", "Project imported successfully!")
                self.parent().accept()
            else:
                QMessageBox.warning(self, "Error", "No project directory found in zip file")
        else:
            QMessageBox.critical(self, "Error", "Failed to import project")
