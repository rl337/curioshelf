#!/usr/bin/env python3
"""
Test runner for CurioShelf

This script provides easy ways to run different test suites for different
UI implementations and test types.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="CurioShelf Test Runner")
    parser.add_argument(
        "--ui-type", 
        choices=["all", "qt", "script", "headless"], 
        default="all",
        help="Type of UI tests to run (default: all)"
    )
    parser.add_argument(
        "--test-type",
        choices=["all", "unit", "integration", "e2e"],
        default="all", 
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--coverage",
        action="store_true", 
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["poetry", "run", "pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=curioshelf", "--cov-report=html", "--cov-report=term"])
    
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Add UI type filters
    if args.ui_type == "qt":
        # Run Qt-specific tests (exclude script UI tests)
        cmd.extend(["--ignore=tests/test_script_ui.py", "--ignore=tests/test_ui_unified_pytest.py"])
    elif args.ui_type == "script":
        # Run script UI tests
        cmd.extend(["-m", "script"])
    elif args.ui_type == "headless":
        # Run headless tests (exclude Qt and script UI tests)
        cmd.extend(["--ignore=tests/test_script_ui.py", "--ignore=tests/test_ui_unified_pytest.py"])
    # "all" means no UI filter
    
    # Add test type filters
    if args.test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif args.test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif args.test_type == "e2e":
        cmd.extend(["tests/e2e/"])
    # "all" means no test type filter
    
    # Run the tests
    success = run_command(cmd, f"Running {args.ui_type} {args.test_type} tests")
    
    if success:
        print(f"\n✅ All {args.ui_type} {args.test_type} tests passed!")
        return 0
    else:
        print(f"\n❌ Some {args.ui_type} {args.test_type} tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())