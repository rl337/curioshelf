"""
Qt implementation of project dialog for creating and opening projects
"""

from typing import Optional, Callable
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QPushButton, QListWidget, QLabel, QFileDialog,
    QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer

from curioshelf.projects.structure import ProjectStructureManager, ProjectMetadata
from curioshelf.config import config


class QtProjectDialog(QDialog):
    """Qt implementation of project dialog"""
    
    # Signals
    project_created = Signal(Path, ProjectMetadata)
    project_loaded = Signal(Path)
    
    def __init__(self, parent=None, mode="create"):
        super().__init__(parent)
        self.mode = mode
        self.project_manager = ProjectStructureManager()
        
        # UI components
        self.project_name_input = None
        self.project_path_input = None
        self.browse_btn = None
        self.create_btn = None
        self.open_btn = None
        self.existing_projects_list = None
        
        # Auto-completion timer
        self.auto_complete_timer = QTimer()
        self.auto_complete_timer.setSingleShot(True)
        self.auto_complete_timer.timeout.connect(self._update_project_path)
        
        self.setup_ui()
        self.refresh()
    
    def set_mode(self, mode: str) -> None:
        """Set the dialog mode (create or open)"""
        self.mode = mode
        self._update_ui_for_mode()
    
    def _update_ui_for_mode(self) -> None:
        """Update UI elements based on the current mode"""
        if self.mode == "open":
            if hasattr(self, 'new_project_group'):
                self.new_project_group.setVisible(False)
            if hasattr(self, 'existing_projects_group'):
                self.existing_projects_group.setVisible(True)
        else:
            if hasattr(self, 'new_project_group'):
                self.new_project_group.setVisible(True)
            if hasattr(self, 'existing_projects_group'):
                self.existing_projects_group.setVisible(False)
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Project Management")
        self.setModal(True)
        self.resize(500, 400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create New Project section
        self.new_project_group = QGroupBox("Create New Project")
        new_project_layout = QFormLayout()
        
        self.project_name_input = QLineEdit()
        self.project_name_input.setObjectName("project_name")
        self.project_name_input.setPlaceholderText("Enter project name")
        self.project_name_input.textChanged.connect(self._on_project_name_changed)
        new_project_layout.addRow("Project Name:", self.project_name_input)
        
        self.project_path_input = QLineEdit()
        self.project_path_input.setObjectName("project_path")
        self.project_path_input.setPlaceholderText("Select project directory")
        # Set default project directory
        default_dir = config.get_default_project_directory()
        self.project_path_input.setText(str(default_dir))
        new_project_layout.addRow("Project Path:", self.project_path_input)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setObjectName("browse")
        self.browse_btn.clicked.connect(self.browse_directory)
        new_project_layout.addRow("", self.browse_btn)
        
        self.create_btn = QPushButton("Create Project")
        self.create_btn.setObjectName("create")
        self.create_btn.clicked.connect(self.create_project)
        new_project_layout.addRow("", self.create_btn)
        
        self.new_project_group.setLayout(new_project_layout)
        main_layout.addWidget(self.new_project_group)
        
        # Open Existing Project section
        self.existing_projects_group = QGroupBox("Open Existing Project")
        open_project_layout = QVBoxLayout()
        
        self.existing_projects_list = QListWidget()
        self.existing_projects_list.setObjectName("project_list")
        self.existing_projects_list.itemDoubleClicked.connect(self.open_selected_project)
        open_project_layout.addWidget(QLabel("Recent Projects:"))
        open_project_layout.addWidget(self.existing_projects_list)
        
        # Button layout for open actions
        button_layout = QHBoxLayout()
        
        self.open_btn = QPushButton("Open Selected Project")
        self.open_btn.setObjectName("open")
        self.open_btn.clicked.connect(self.open_selected_project)
        button_layout.addWidget(self.open_btn)
        
        self.browse_open_btn = QPushButton("Browse...")
        self.browse_open_btn.setObjectName("browse_open")
        self.browse_open_btn.clicked.connect(self.browse_for_project)
        button_layout.addWidget(self.browse_open_btn)
        
        open_project_layout.addLayout(button_layout)
        
        self.existing_projects_group.setLayout(open_project_layout)
        main_layout.addWidget(self.existing_projects_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # Update UI for mode
        self._update_ui_for_mode()
    
    def _on_project_name_changed(self, text: str):
        """Handle project name text changes for auto-completion"""
        if config.get("auto_complete_project_path", True):
            # Restart the timer to debounce rapid changes
            self.auto_complete_timer.stop()
            self.auto_complete_timer.start(300)  # 300ms delay
    
    def _update_project_path(self):
        """Update the project path based on the project name"""
        project_name = self.project_name_input.text().strip()
        if project_name:
            suggested_path = config.get_project_path_for_name(project_name)
            self.project_path_input.setText(str(suggested_path))
    
    def browse_directory(self):
        """Browse for project directory"""
        # Start from the current path or default directory
        current_path = self.project_path_input.text().strip()
        if not current_path:
            current_path = str(config.get_default_project_directory())
        
        directory = QFileDialog.getExistingDirectory(
            self, "Select Project Directory", current_path
        )
        if directory:
            self.project_path_input.setText(directory)
    
    def browse_for_project(self):
        """Browse for an existing project directory"""
        # Start from the default project directory
        default_dir = str(config.get_default_project_directory())
        project_path = QFileDialog.getExistingDirectory(
            self, "Open Project Directory", default_dir, QFileDialog.ShowDirsOnly
        )
        if project_path:
            project_path = Path(project_path)
            # Check if this directory contains a curioshelf.json file
            config_file = project_path / "curioshelf.json"
            if not config_file.exists():
                QMessageBox.warning(self, "Error", "Selected directory does not contain a CurioShelf project (curioshelf.json not found).")
                return
            
            try:
                # Load the project
                structure = self.project_manager.load_project(project_path)
                if structure is None:
                    QMessageBox.critical(self, "Error", "Failed to load project structure.")
                    return
                
                # Emit signal
                self.project_loaded.emit(project_path)
                
                # Close dialog
                self.accept()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project: {e}")
    
    def create_project(self):
        """Create a new project"""
        name = self.project_name_input.text().strip()
        path = self.project_path_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a project name.")
            return
        
        if not path:
            QMessageBox.warning(self, "Error", "Please select a project directory.")
            return
        
        try:
            project_path = Path(path)
            project_info = ProjectMetadata(
                name=name,
                description=f"Project created by user",
                author="User"
            )
            
            # Create the project
            self.project_manager.create_project(project_path, project_info)
            
            # Emit signal
            self.project_created.emit(project_path, project_info)
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
    
    def open_selected_project(self):
        """Open the selected project"""
        current_item = self.existing_projects_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a project to open.")
            return
        
        project_data = current_item.data(Qt.UserRole)
        if not project_data:
            QMessageBox.warning(self, "Error", "No project data available.")
            return
        
        project_path = Path(project_data)
        
        try:
            # Load the project
            structure = self.project_manager.load_project(project_path)
            if structure is None:
                QMessageBox.critical(self, "Error", "Failed to load project structure.")
                return
            
            # Emit signal
            self.project_loaded.emit(project_path)
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open project: {e}")
    
    def refresh(self):
        """Refresh the dialog content"""
        # Load recent projects
        if self.existing_projects_list:
            self.existing_projects_list.clear()
            # TODO: Load recent projects from settings
            # For now, just add a placeholder
            item = self.existing_projects_list.addItem("No recent projects")
            if item:
                item.setData(Qt.UserRole, "")
