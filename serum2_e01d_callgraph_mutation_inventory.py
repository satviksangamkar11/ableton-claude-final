#!/usr/bin/env python3
"""PHASE E-0.1D — CALL-GRAPH MUTATION INVENTORY

Build a proper, unique, call-graph-based inventory of production mutations.

Not grep-based counts, but actual call paths:
  production entry point
    ↓ (call trace)
    ↓
  actual mutation primitive
    ├── pathmerge.apply_path_value
    ├── synth.set_parameter
    ├── compiled_mutations execute
    ├── direct state mutation
    └── topology change

Classification per unique site:
  AUTHORIZED_GATE: routes through execute_mutation_with_authority()
  PRE_AUTHORITY_SETUP: legitimate pre-admission context (baseline, etc)
  READ_ONLY: no mutation
  EVIDENCE_EXECUTION: evidence harness (separate authority model)
  BYPASS: production-reachable, no authority enforcement
  UNKNOWN: needs manual inspection
"""

import ast
import os
from pathlib import Path
from collections import defaultdict

# Production entry points (call these to trigger real Serum mutations)
PRODUCTION_ENTRYPOINTS = {
    "canonical_feedback_loop.execute_producer_from_intent": "producer loop entry",
    "canonical_feedback_loop.execute_producer_feedback_episode": "producer loop internal",
}

# Mutation primitives (these actually touch Serum)
MUTATION_PRIMITIVES = {
    "pathmerge.apply_path_value": "direct state mutation",
    "synth.set_parameter": "VST3 parameter set",
    "Mutation": "mutation object creation",
    "compiled_mutations": "mutation list execution",
    "load_state": "Serum state file load",
}

class CallGraphAnalyzer(ast.NodeVisitor):
    """Trace function calls to build a call graph."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.current_func = None
        self.calls = defaultdict(set)  # func -> set of called functions
        self.mutation_calls = defaultdict(list)  # func -> list of mutation sites

    def visit_FunctionDef(self, node):
        self.current_func = node.name
        self.generic_visit(node)
        self.current_func = None

    def visit_Call(self, node):
        if self.current_func:
            # Record the call
            if isinstance(node.func, ast.Attribute):
                # e.g., pathmerge.apply_path_value
                parts = []
                curr = node.func
                while isinstance(curr, ast.Attribute):
                    parts.insert(0, curr.attr)
                    curr = curr.value
                if isinstance(curr, ast.Name):
                    parts.insert(0, curr.id)
                    call_name = ".".join(parts)
                    self.calls[self.current_func].add(call_name)

                    # Check if this is a mutation primitive
                    for prim, desc in MUTATION_PRIMITIVES.items():
                        if prim in call_name:
                            self.mutation_calls[self.current_func].append({
                                "line": node.lineno,
                                "call": call_name,
                                "primitive": prim,
                                "description": desc,
                                "file": self.filepath,
                            })
            elif isinstance(node.func, ast.Name):
                # e.g., render_arm()
                self.calls[self.current_func].add(node.func.id)

                # Check if this is a mutation primitive
                for prim, desc in MUTATION_PRIMITIVES.items():
                    if prim == node.func.id:
                        self.mutation_calls[self.current_func].append({
                            "line": node.lineno,
                            "call": node.func.id,
                            "primitive": prim,
                            "description": desc,
                            "file": self.filepath,
                        })

        self.generic_visit(node)

def analyze_codebase():
    """Analyze production code for mutation call paths."""

    results = {
        "entry_points": {},
        "mutation_sites": [],
        "unique_primitives": defaultdict(list),
    }

    # Analyze each production file
    for filepath in ["serum2/producer/canonical_feedback_loop.py",
                     "serum2/qualification/execute_vertical_slice.py",
                     "serum2/evidence/harness.py"]:
        full_path = Path(filepath)

        if not full_path.exists():
            continue

        print(f"Analyzing {filepath}...")

        with open(full_path) as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError as e:
                print(f"  [ERROR] Parse error: {e}")
                continue

        analyzer = CallGraphAnalyzer(filepath)
        analyzer.visit(tree)

        # Record mutation sites
        for func, sites in analyzer.mutation_calls.items():
            for site in sites:
                results["mutation_sites"].append(site)
                results["unique_primitives"][site["primitive"]].append({
                    "func": func,
                    "file": filepath,
                    "line": site["line"],
                })

        # Record entry points
        for entry_func, desc in PRODUCTION_ENTRYPOINTS.items():
            if entry_func.split(".")[1] in analyzer.calls or entry_func.split(".")[1] in str(analyzer.mutation_calls):
                results["entry_points"][entry_func] = {
                    "description": desc,
                    "calls": analyzer.calls,
                    "mutations": analyzer.mutation_calls,
                }

    return results

def main():
    print("="*80)
    print("PHASE E-0.1D — CALL-GRAPH MUTATION INVENTORY")
    print("="*80 + "\n")

    results = analyze_codebase()

    print("\nMUTATION PRIMITIVES FOUND:\n")
    for prim in sorted(results["unique_primitives"].keys()):
        sites = results["unique_primitives"][prim]
        print(f"{prim}: {len(sites)} sites")
        for site in sites[:2]:
            print(f"  {site['file']}:{site['line']} in {site['func']}")
        if len(sites) > 2:
            print(f"  ... and {len(sites) - 2} more")

    print(f"\nTotal unique mutation sites: {len(results['mutation_sites'])}\n")

    # Classify each site
    print("CLASSIFICATION REQUIRED:\n")

    for site in results["mutation_sites"]:
        file_path = site["file"]
        func_name = site["call"]

        # Auto-classify based on patterns
        classification = "UNKNOWN"
        if "execute_mutation_with_authority" in str(site):
            classification = "AUTHORIZED_GATE"
        elif "prerequisite_overrides" in func_name or "baseline" in func_name:
            classification = "PRE_AUTHORITY_SETUP"
        elif "harness.py" in file_path and "render_arm" in func_name:
            classification = "EVIDENCE_EXECUTION"  # separate authority model
        elif "canonical_feedback_loop" in file_path and "set_parameter" in func_name:
            classification = "BYPASS"  # reaches producer, not gated
        elif "read" in func_name.lower() or "get" in func_name.lower():
            classification = "READ_ONLY"

        print(f"{file_path}:{site['line']} {site['call']:40} -> {classification}")

    print(f"\n{'='*80}")
    print("E-0.1D STATUS: REQUIRES MANUAL CLASSIFICATION")
    print(f"{'='*80}\n")
    print("Next: Classify each unique mutation site as AUTHORIZED_GATE or BYPASS")
    print("Then wire BYPASS sites through execute_mutation_with_authority()")
    print("Then: E-0.1E regression tests, then E-0.1 PASS")

if __name__ == "__main__":
    main()

