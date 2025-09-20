#!/usr/bin/env python3
"""Debug script to test foreach runtime execution"""

import sys
sys.path.append('.')

from curioshelf.ui.script.script_runtime import ScriptRuntime
from curioshelf.ui.script.simple_parser import SimpleCurioParser

# Create a simple test
runtime = ScriptRuntime(verbose=True)

# Set up a variable
runtime.state_machine.set_variable('max_test_assets', 3)

# Test foreach parsing and execution
parser = SimpleCurioParser()
script_content = """
foreach (i in range(max_test_assets)):
    print("Loop iteration:", i)
"""

statements = parser.parse_script(script_content)
print("Parsed statements:")
for i, stmt in enumerate(statements):
    print(f"Statement {i}: {stmt}")

# Look at the foreach statement
foreach_stmt = statements[0]
print(f"\nForeach statement:")
print(f"  Variable: {foreach_stmt.get('variable')}")
print(f"  Iterable: {foreach_stmt.get('iterable')}")
print(f"  Iterable type: {type(foreach_stmt.get('iterable'))}")

# Try to evaluate the iterable
try:
    iterable = runtime._evaluate_expression(foreach_stmt['iterable'])
    print(f"Evaluated iterable: {iterable}")
    print(f"Iterable type: {type(iterable)}")
except Exception as e:
    print(f"Error evaluating iterable: {e}")
    import traceback
    traceback.print_exc()
