#!/usr/bin/env python3
"""
CurioShelf Script Test Runner

This script runs .curio test files using the script UI implementation.
"""

import sys
import os
import traceback
from pathlib import Path
from typing import List, Optional

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from curioshelf.ui.script.ui_factory import ScriptUIImplementation
from curioshelf.mock_application import MockCurioShelfApplication


def run_curio_script(script_path: Path, verbose: bool = True) -> bool:
    """Run a single .curio script file"""
    print(f"\n{'='*60}")
    print(f"Running CurioScript: {script_path.name}")
    print(f"{'='*60}")
    
    # Create mock application for testing
    mock_app = MockCurioShelfApplication()
    
    # Create script UI implementation
    script_ui = ScriptUIImplementation(
        verbose=verbose,
        interactive=False,
        application_interface=mock_app
    )
    
    # Initialize the UI
    if not script_ui.initialize():
        print("Failed to initialize script UI")
        return False
    
    try:
        # Read the script file
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        print(f"Script content:\n{script_content}")
        print(f"\n{'-'*40}")
        print("EXECUTION OUTPUT:")
        print(f"{'-'*40}")
        
        # Execute the script using the script runtime
        try:
            result = script_ui._script_runtime.execute_script_content(script_content)
            if result is not None:
                print(f"Script result: {result}")
        except Exception as e:
            print(f"Script execution error: {e}")
            traceback.print_exc()
            return False
        
        print(f"\n{'-'*40}")
        print("SCRIPT COMPLETED")
        print(f"{'-'*40}")
        
        return True
        
    except Exception as e:
        print(f"Error running script {script_path}: {e}")
        return False
    
    finally:
        script_ui.cleanup()


def find_curio_scripts(test_dir: Path) -> List[Path]:
    """Find all .curio script files in the test directory"""
    scripts = []
    for file_path in test_dir.glob("*.curio"):
        if file_path.is_file():
            scripts.append(file_path)
    return sorted(scripts)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CurioShelf script tests")
    parser.add_argument("--script", "-s", help="Run specific script file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test-dir", "-d", default="tests/scripts", help="Test directory")
    
    args = parser.parse_args()
    
    test_dir = Path(args.test_dir)
    if not test_dir.exists():
        print(f"Test directory does not exist: {test_dir}")
        return 1
    
    if args.script:
        # Run specific script
        script_path = Path(args.script)
        if not script_path.exists():
            print(f"Script file does not exist: {script_path}")
            return 1
        
        success = run_curio_script(script_path, args.verbose)
        return 0 if success else 1
    else:
        # Run all scripts
        scripts = find_curio_scripts(test_dir)
        if not scripts:
            print(f"No .curio scripts found in {test_dir}")
            return 1
        
        print(f"Found {len(scripts)} script(s) to run:")
        for script in scripts:
            print(f"  - {script.name}")
        
        success_count = 0
        for script in scripts:
            success = run_curio_script(script, args.verbose)
            if success:
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"Test Results: {success_count}/{len(scripts)} scripts passed")
        print(f"{'='*60}")
        
        return 0 if success_count == len(scripts) else 1


if __name__ == "__main__":
    sys.exit(main())
