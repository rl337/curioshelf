#!/usr/bin/env python3
"""
Comprehensive tests for .curioshelf config file behavior
"""

import json
import tempfile
import os
from pathlib import Path
import pytest


def get_build_test_dir(test_name: str) -> Path:
    """Get a test directory in the build/ folder"""
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)
    test_dir = build_dir / test_name
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    return test_dir
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from curioshelf.config import CurioShelfConfig


class TestCurioShelfConfigComprehensive:
    """Comprehensive tests for CurioShelfConfig behavior"""
    
    def test_config_without_existing_file(self):
        """Test config behavior when no .curioshelf file exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create config - should not create file
                config = CurioShelfConfig()
                
                # Verify default values
                assert config.get("remember_recent_projects", True) == True
                assert config.get("max_recent_projects", 10) == 10
                assert config.get_recent_projects() == []
                
                # Create a real project directory in build/
                project_dir = get_build_test_dir("test_project1")
                (project_dir / "curioshelf.json").write_text('{"name": "Test Project 1"}')
                
                # Add a project - should not save to file
                config.add_recent_project(project_dir, "Test Project 1")
                
                # Verify it's in memory
                recent = config.get_recent_projects()
                assert len(recent) == 1
                assert recent[0]["name"] == "Test Project 1"
                assert recent[0]["path"] == str(project_dir)
                
                # Verify no file was created
                assert not Path(".curioshelf").exists()
                assert not (Path.home() / ".curioshelf").exists()
                
            finally:
                os.chdir(original_cwd)
    
    def test_config_with_existing_file(self):
        """Test config behavior when .curioshelf file exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create initial config file
                initial_config = {
                    "remember_recent_projects": True,
                    "max_recent_projects": 5,
                    "recent_projects": [
                        {
                            "path": "/existing/project1",
                            "name": "Existing Project 1",
                            "last_opened": "1234567890"
                        }
                    ]
                }
                
                with open(".curioshelf", "w") as f:
                    json.dump(initial_config, f)
                
                # Create the existing project directory
                existing_project_dir = Path("existing_project1")
                existing_project_dir.mkdir()
                (existing_project_dir / "curioshelf.json").write_text('{"name": "Existing Project 1"}')
                
                # Update the config to use the real path
                initial_config["recent_projects"][0]["path"] = str(existing_project_dir)
                with open(".curioshelf", "w") as f:
                    json.dump(initial_config, f)
                
                # Create config - should load from file
                config = CurioShelfConfig()
                
                # Verify loaded values
                assert config.get("remember_recent_projects", True) == True
                assert config.get("max_recent_projects", 10) == 5
                
                recent = config.get_recent_projects()
                assert len(recent) == 1
                assert recent[0]["name"] == "Existing Project 1"
                assert recent[0]["path"] == "existing_project1"
                
                # Create a real project directory
                project_dir = get_build_test_dir("test_project2")
                (project_dir / "curioshelf.json").write_text('{"name": "Test Project 2"}')
                
                # Add a new project - should save to file
                config.add_recent_project(project_dir, "Test Project 2")
                
                # Verify it's in memory
                recent = config.get_recent_projects()
                assert len(recent) == 2
                assert recent[0]["name"] == "Test Project 2"  # Should be first (most recent)
                assert recent[1]["name"] == "Existing Project 1"
                
                # Verify file was updated
                with open(".curioshelf", "r") as f:
                    saved_config = json.load(f)
                
                assert len(saved_config["recent_projects"]) == 2
                assert saved_config["recent_projects"][0]["name"] == "Test Project 2"
                
            finally:
                os.chdir(original_cwd)
    
    def test_config_file_in_home_directory(self):
        """Test config behavior when file is in home directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory (no .curioshelf here)
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create config file in home directory
                # Create a real project directory for home test
                home_project_dir = Path("home_project1")
                home_project_dir.mkdir()
                (home_project_dir / "curioshelf.json").write_text('{"name": "Home Project 1"}')
                
                home_config = {
                    "remember_recent_projects": True,
                    "max_recent_projects": 3,
                    "recent_projects": [
                        {
                            "path": str(home_project_dir),
                            "name": "Home Project 1",
                            "last_opened": "1234567890"
                        }
                    ]
                }
                
                home_config_path = Path.home() / ".curioshelf"
                with open(home_config_path, "w") as f:
                    json.dump(home_config, f)
                
                try:
                    # Create config - should load from home directory
                    config = CurioShelfConfig()
                    
                    # Verify loaded values
                    assert config.get("max_recent_projects", 10) == 3
                    
                    recent = config.get_recent_projects()
                    assert len(recent) == 1
                    assert recent[0]["name"] == "Home Project 1"
                    
                    # Create a real project directory in build/
                    project_dir = get_build_test_dir("test_project3")
                    (project_dir / "curioshelf.json").write_text('{"name": "Test Project 3"}')
                    
                    # Add a project - should save to home directory file
                    config.add_recent_project(project_dir, "Test Project 3")
                    
                    # Verify file was updated
                    with open(home_config_path, "r") as f:
                        saved_config = json.load(f)
                    
                    assert len(saved_config["recent_projects"]) == 2
                    assert saved_config["recent_projects"][0]["name"] == "Test Project 3"
                    
                finally:
                    # Clean up home directory file
                    if home_config_path.exists():
                        home_config_path.unlink()
                        
            finally:
                os.chdir(original_cwd)
    
    def test_recent_projects_limits(self):
        """Test that recent projects respect the max limit"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create initial config with max_recent_projects = 3
                initial_config = {
                    "remember_recent_projects": True,
                    "max_recent_projects": 3,
                    "recent_projects": []
                }
                
                with open(".curioshelf", "w") as f:
                    json.dump(initial_config, f)
                
                config = CurioShelfConfig()
                
                # Add 5 projects
                for i in range(5):
                    project_dir = get_build_test_dir(f"test_project{i}")
                    (project_dir / "curioshelf.json").write_text(f'{{"name": "Test Project {i}"}}')
                    config.add_recent_project(project_dir, f"Test Project {i}")
                
                # Should only keep 3 most recent
                recent = config.get_recent_projects()
                assert len(recent) == 3
                assert recent[0]["name"] == "Test Project 4"  # Most recent
                assert recent[1]["name"] == "Test Project 3"
                assert recent[2]["name"] == "Test Project 2"
                
            finally:
                os.chdir(original_cwd)
    
    def test_duplicate_project_handling(self):
        """Test that adding duplicate projects moves them to the top"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create real project directories in build/
                project1_dir = get_build_test_dir("test_project1")
                (project1_dir / "curioshelf.json").write_text('{"name": "Test Project 1"}')
                
                project2_dir = get_build_test_dir("test_project2")
                (project2_dir / "curioshelf.json").write_text('{"name": "Test Project 2"}')
                
                # Create initial config
                initial_config = {
                    "remember_recent_projects": True,
                    "max_recent_projects": 5,
                    "recent_projects": [
                        {
                            "path": str(project1_dir),
                            "name": "Test Project 1",
                            "last_opened": "1234567890"
                        },
                        {
                            "path": str(project2_dir),
                            "name": "Test Project 2",
                            "last_opened": "1234567891"
                        }
                    ]
                }
                
                with open(".curioshelf", "w") as f:
                    json.dump(initial_config, f)
                
                config = CurioShelfConfig()
                
                # Create project1 directory in build/
                project1_dir = get_build_test_dir("test_project1")
                (project1_dir / "curioshelf.json").write_text('{"name": "Test Project 1"}')
                
                # Add project1 again (should move to top)
                config.add_recent_project(project1_dir, "Test Project 1")
                
                recent = config.get_recent_projects()
                assert len(recent) == 2
                assert recent[0]["name"] == "Test Project 1"  # Should be first now
                assert recent[1]["name"] == "Test Project 2"
                
            finally:
                os.chdir(original_cwd)
    
    def test_invalid_project_filtering(self):
        """Test that invalid projects are filtered out"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create a real project directory in build/
                project2_dir = get_build_test_dir("test_project2")
                (project2_dir / "curioshelf.json").write_text('{"name": "Test Project 2"}')
                
                # Create initial config with mix of valid and invalid projects
                initial_config = {
                    "remember_recent_projects": True,
                    "max_recent_projects": 5,
                    "recent_projects": [
                        {
                            "path": "/nonexistent/project1",
                            "name": "Nonexistent Project 1",
                            "last_opened": "1234567890"
                        },
                        {
                            "path": str(project2_dir),
                            "name": "Test Project 2",
                            "last_opened": "1234567891"
                        }
                    ]
                }
                
                with open(".curioshelf", "w") as f:
                    json.dump(initial_config, f)
                
                config = CurioShelfConfig()
                
                # Should filter out nonexistent project
                recent = config.get_recent_projects()
                assert len(recent) == 1
                assert recent[0]["name"] == "Test Project 2"
                
            finally:
                os.chdir(original_cwd)
    
    def test_config_without_recent_projects_key(self):
        """Test config behavior when recent_projects key is missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create config file without recent_projects key
                initial_config = {
                    "remember_recent_projects": True,
                    "max_recent_projects": 5
                }
                
                with open(".curioshelf", "w") as f:
                    json.dump(initial_config, f)
                
                config = CurioShelfConfig()
                
                # Should return empty list
                recent = config.get_recent_projects()
                assert recent == []
                
                # Create a real project directory in build/
                project_dir = get_build_test_dir("test_project1")
                (project_dir / "curioshelf.json").write_text('{"name": "Test Project 1"}')
                
                # Should be able to add projects
                config.add_recent_project(project_dir, "Test Project 1")
                recent = config.get_recent_projects()
                assert len(recent) == 1
                
            finally:
                os.chdir(original_cwd)
    
    def test_config_corrupted_file(self):
        """Test config behavior when file is corrupted"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create corrupted config file
                with open(".curioshelf", "w") as f:
                    f.write("invalid json content")
                
                # Should not crash, should use defaults
                config = CurioShelfConfig()
                
                # Should have default values
                assert config.get("remember_recent_projects", True) == True
                assert config.get_recent_projects() == []
                
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
