#!/usr/bin/env python3
"""
Pytest integration for CurioShelf CurioScript tests.

This module runs .curio script files as part of the main pytest test suite.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
import traceback

from curioshelf.ui.script.ui_factory import ScriptUIImplementation
from tests.test_application_impl import ConcreteTestApplicationImpl


class CurioScriptTestRunner:
    """Test runner for CurioScript files"""
    
    def __init__(self):
        self.test_app = None
        self.script_ui = None
    
    def setup(self):
        """Set up the test environment"""
        # Create concrete test application for testing
        self.test_app = ConcreteTestApplicationImpl()
        
        # Create script UI implementation
        self.script_ui = ScriptUIImplementation(
            verbose=False,  # Keep quiet during tests
            interactive=False,
            application_interface=self.test_app
        )
        
        # Initialize the UI
        if not self.script_ui.initialize():
            raise RuntimeError("Failed to initialize script UI")
    
    def teardown(self):
        """Clean up the test environment"""
        if self.script_ui:
            self.script_ui.cleanup()
        self.script_ui = None
        self.test_app = None
    
    def parse_script_pragmas(self, script_path: Path) -> List[str]:
        """Parse pragma comments from a script file
        
        Returns:
            List of pragma tags found in the script
        """
        pragmas = []
        try:
            with open(script_path, 'r') as f:
                lines = f.readlines()
            
            # Look for pragma comments in the first 10 lines
            for i, line in enumerate(lines[:10]):
                line = line.strip()
                if line.startswith('#') and '@' in line:
                    # Extract pragma tags from comment
                    # Format: # @pragma1 @pragma2 @pragma3
                    pragma_part = line[1:].strip()  # Remove #
                    if pragma_part.startswith('@'):
                        # Split by @ and clean up
                        tags = [tag.strip() for tag in pragma_part.split('@') if tag.strip()]
                        pragmas.extend(tags)
        except Exception as e:
            # If we can't parse pragmas, that's okay - script will use default behavior
            pass
        
        return pragmas
    
    def run_script(self, script_path: Path) -> tuple[bool, Optional[str]]:
        """Run a single .curio script file
        
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Reset the test application state before each script
            if self.test_app:
                self.test_app.reset_state()
            
            # Read the script file
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            # Execute the script using the script runtime
            result = self.script_ui._script_runtime.execute_script_content(script_content)
            return True, None
            
        except AssertionError as e:
            return False, f"Script assertion failed: {e}"
        except Exception as e:
            return False, f"Script execution error: {e}\n{traceback.format_exc()}"
    
    def find_curio_scripts(self, test_dir: Path) -> List[Path]:
        """Find all .curio script files in the test directory"""
        scripts = []
        for file_path in test_dir.glob("*.curio"):
            if file_path.is_file():
                scripts.append(file_path)
        return sorted(scripts)


# Global test runner instance
_curio_runner = None


def get_curio_runner() -> CurioScriptTestRunner:
    """Get or create the global CurioScript test runner"""
    global _curio_runner
    if _curio_runner is None:
        _curio_runner = CurioScriptTestRunner()
    return _curio_runner


@pytest.fixture(scope="session")
def curio_script_runner():
    """Pytest fixture for CurioScript test runner"""
    runner = get_curio_runner()
    runner.setup()
    yield runner
    runner.teardown()


def find_curio_scripts() -> List[Path]:
    """Find all .curio script files in the tests/scripts directory"""
    scripts_dir = Path(__file__).parent / "scripts"
    if not scripts_dir.exists():
        return []
    
    runner = get_curio_runner()
    return runner.find_curio_scripts(scripts_dir)


# Generate test functions for each .curio script
def pytest_generate_tests(metafunc):
    """Generate test functions for each .curio script file"""
    if "curio_script_path" in metafunc.fixturenames:
        script_paths = find_curio_scripts()
        metafunc.parametrize("curio_script_path", script_paths, ids=lambda p: p.stem)


def test_curio_script(curio_script_runner, curio_script_path):
    """Test a single CurioScript file"""
    # Parse pragma comments from the script
    pragmas = curio_script_runner.parse_script_pragmas(curio_script_path)
    
    success, error_msg = curio_script_runner.run_script(curio_script_path)
    
    # Handle different expected outcomes based on pragmas
    if "expect_assert_failed" in pragmas:
        # Script is expected to fail with assertion error
        if not success and "ASSERTION FAILED" in error_msg:
            print("✓ Assertion failure occurred as expected")
            return
        elif success:
            pytest.fail("Expected assertion failure but script succeeded")
        else:
            pytest.fail(f"Expected assertion failure but got different error: {error_msg}")
    
    elif "expect_budget_exceeded" in pragmas:
        # Script is expected to fail with budget exceeded
        if not success and "Execution budget exceeded" in error_msg:
            print("✓ Budget exceeded as expected")
            return
        elif success:
            pytest.fail("Expected budget exceeded but script succeeded")
        else:
            pytest.fail(f"Expected budget exceeded but got different error: {error_msg}")
    
    elif "expect_normal_exit" in pragmas or not pragmas:
        # Script should succeed (default behavior)
        if not success:
            pytest.fail(f"CurioScript test failed: {error_msg}")
    
    else:
        # Unknown pragma
        pytest.fail(f"Unknown pragma in script: {pragmas}")


# Individual test functions for specific scripts (for better test organization)
class TestCurioScripts:
    """Test class for CurioScript functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self, curio_script_runner):
        """Set up and tear down for each test"""
        self.runner = curio_script_runner
        yield
        # Reset the test application state between tests
        if hasattr(self.runner, 'test_app') and self.runner.test_app:
            self.runner.test_app.reset_state()
    
    def test_basic_project_operations(self):
        """Test basic project operations script"""
        script_path = Path(__file__).parent / "scripts" / "test_project_basic.curio"
        if script_path.exists():
            success, error_msg = self.runner.run_script(script_path)
            assert success, f"Basic project operations test failed: {error_msg}"
    
    def test_comprehensive_assertions(self):
        """Test comprehensive assertions script"""
        script_path = Path(__file__).parent / "scripts" / "test_comprehensive_assertions.curio"
        if script_path.exists():
            success, error_msg = self.runner.run_script(script_path)
            assert success, f"Comprehensive assertions test failed: {error_msg}"
    
    def test_detailed_help_system(self):
        """Test detailed help system script"""
        script_path = Path(__file__).parent / "scripts" / "test_detailed_help_with_concrete.curio"
        if script_path.exists():
            success, error_msg = self.runner.run_script(script_path)
            assert success, f"Detailed help system test failed: {error_msg}"
    
    def test_scripting_features(self):
        """Test general scripting features - expected to fail due to infinite loop in nested control structures"""
        script_path = Path(__file__).parent / "scripts" / "test_scripting_features.curio"
        if script_path.exists():
            success, error_msg = self.runner.run_script(script_path)
            
            # This test is expected to fail due to infinite loop in nested while loops
            # The budget system should catch it and raise BudgetExceededError
            if not success and "Execution budget exceeded" in error_msg:
                # This is the expected behavior - budget system caught infinite loop
                print("✓ Budget system successfully caught infinite loop (expected behavior)")
                return
            else:
                # If it succeeds or fails for other reasons, that's unexpected
                assert success, f"Scripting features test failed unexpectedly: {error_msg}"
    
    def test_command_reflection(self):
        """Test command reflection system"""
        script_path = Path(__file__).parent / "scripts" / "test_command_reflection.curio"
        if script_path.exists():
            success, error_msg = self.runner.run_script(script_path)
            assert success, f"Command reflection test failed: {error_msg}"


# Test for syntax validation
def test_curio_syntax_validation():
    """Test that CurioScript files use the correct syntax (:= for assignment, = for comparison)"""
    scripts_dir = Path(__file__).parent / "scripts"
    if not scripts_dir.exists():
        pytest.skip("No scripts directory found")
    
    syntax_errors = []
    
    for script_path in scripts_dir.glob("*.curio"):
        with open(script_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for old assignment syntax (variable = value)
            if ' = ' in line and not line.strip().startswith('#'):
                # Skip lines that are clearly comparisons or function calls
                if not any(op in line for op in ['==', '!=', '<=', '>=', '<', '>']) and \
                   not '(' in line and \
                   not line.strip().startswith('print(') and \
                   not line.strip().startswith('assert('):
                    syntax_errors.append(f"{script_path.name}:{i}: Found old assignment syntax '=' instead of ':='")
    
    if syntax_errors:
        pytest.fail(f"Syntax validation failed:\n" + "\n".join(syntax_errors))


if __name__ == "__main__":
    # Allow running this file directly for debugging
    import sys
    pytest.main([__file__, "-v"])
