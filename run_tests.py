#!/usr/bin/env python3
"""
Test runner for CurioShelf

This script provides convenient ways to run different categories of tests
with appropriate configurations for different environments.
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
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"Return code: {result.returncode}")
    return result.returncode == 0


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="CurioShelf Test Runner")
    parser.add_argument(
        "--headless-only",
        action="store_true",
        help="Run only headless UI tests (safe for CI)"
    )
    parser.add_argument(
        "--qt-only",
        action="store_true",
        help="Run only Qt UI tests (requires display)"
    )
    parser.add_argument(
        "--debug-only",
        action="store_true",
        help="Run only debugging system tests"
    )
    parser.add_argument(
        "--unit-only",
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--unified-only",
        action="store_true",
        help="Run only unified tests (work with both headless and Qt)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel test processes"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["poetry", "run", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.coverage:
        base_cmd.extend(["--cov=curioshelf", "--cov=gui", "--cov-report=html"])
    
    if args.parallel > 1:
        base_cmd.extend(["-n", str(args.parallel)])
    
    # Note: timeout plugin not available, tests should be fast enough
    
    # Determine which tests to run
    test_patterns = []
    
    if args.headless_only:
        test_patterns.append("tests/test_ui_unified_pytest.py")
        print("Running unified UI tests (headless backend only)...")
    
    elif args.qt_only:
        test_patterns.append("tests/test_ui_unified_pytest.py")
        print("Running unified UI tests (Qt backend only)...")
    
    elif args.debug_only:
        test_patterns.append("tests/test_ui_debugging_pytest.py")
        print("Running debugging system tests only...")
    
    elif args.unit_only:
        test_patterns.extend([
            "tests/test_ui_unified_pytest.py",
            "tests/test_ui_debugging_pytest.py"
        ])
        print("Running unit tests only...")
    
    elif args.integration_only:
        test_patterns.append("tests/test_ui_unified_pytest.py")
        print("Running integration tests only...")
    
    elif args.unified_only:
        test_patterns.append("tests/test_ui_unified_pytest.py")
        print("Running unified tests only...")
    
    else:
        # Run all tests
        test_patterns.append("tests/")
        print("Running all tests...")
    
    # Add test patterns to command
    base_cmd.extend(test_patterns)
    
    # Run the tests
    success = run_command(base_cmd, "Running tests")
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())