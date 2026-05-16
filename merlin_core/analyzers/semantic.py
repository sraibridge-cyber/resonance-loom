#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERLIN CORE — SEMANTIC ANALYZER
AST-based analysis for Python.
Heuristic-based for JS/TS.
Zero external dependencies.
"""
import ast, math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

@dataclass
class SemanticFinding:
    rule_id: str
    severity: str
    message: str
    suggestion: str

class SemanticAnalyzer:
    """Semantic analysis using AST (Python) or heuristics (JS/TS)."""

    def analyze(self, code: str, language: str) -> List[SemanticFinding]:
        if language.lower() == "python":
            return self._analyze_python(code)
        else:
            return self._analyze_heuristic(code, language)

    def _analyze_python(self, code: str) -> List[SemanticFinding]:
        findings = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            findings.append(SemanticFinding("SEM001", "error", "Python syntax error", "Fix syntax before analysis"))
            return findings

        visitor = PythonVisitor()
        visitor.visit(tree)
        findings.extend(visitor.findings)
        return findings

    def _analyze_heuristic(self, code: str, language: str) -> List[SemanticFinding]:
        findings = []
        tokens = code.split()
        lines = code.split("\n")
        
        if language.lower() in ("javascript", "typescript"):
            if "function" not in code and "=>" not in code:
                findings.append(SemanticFinding("SEM101", "info", "No function definitions found", "Consider functional decomposition"))
            if "try" not in code and "catch" not in code:
                findings.append(SemanticFinding("SEM102", "warning", "No error handling found", "Add try/catch blocks"))
            if code.count("{") != code.count("}"):
                findings.append(SemanticFinding("SEM103", "error", "Mismatched braces", "Balance {} pairs"))
        
        cyclomatic = self._estimate_cyclomatic(code)
        if cyclomatic > 10:
            findings.append(SemanticFinding("SEM104", "warning", f"Cyclomatic complexity ~{cyclomatic}", "Break into smaller functions"))
        
        long_functions = [l for l in lines if "function" in l and len(l) > 200]
        if long_functions:
            findings.append(SemanticFinding("SEM105", "info", f"{len(long_functions)} long function signature(s)", "Keep function signatures short"))
        
        return findings

    def _estimate_cyclomatic(self, code: str) -> int:
        decisions = sum(1 for kw in ("if", "elif", "for", "while", "except", "and", "or", "case", "switch")
                       if kw in code)
        return max(1, decisions)

    def analyze_complexity(self, code: str) -> Dict[str, float]:
        lines = code.strip().split("\n")
        non_empty = [l for l in lines if l.strip()]
        tokens = code.split()
        
        halstead_volume = len(tokens) * math.log2(max(len(set(tokens)), 2))
        avg_line_len = sum(len(l) for l in non_empty) / max(len(non_empty), 1)
        maintainability = max(0, 100 - (halstead_volume / 100) - (len(non_empty) / 10) - (avg_line_len / 5))
        
        return {
            "lines": len(non_empty),
            "halstead_volume": round(halstead_volume, 2),
            "avg_line_length": round(avg_line_len, 2),
            "maintainability": round(maintainability, 2)
        }

class PythonVisitor(ast.NodeVisitor):
    def __init__(self):
        self.findings = []
        self.functions = []
        self.in_loop = False

    def visit_FunctionDef(self, node):
        func_len = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
        if func_len > 50:
            self.findings.append(SemanticFinding("SEM201", "info", f"Function '{node.name}' is {func_len} lines — consider splitting", f"Rename '{node.name}' or decompose"))
        if len(node.args.args) > 6:
            self.findings.append(SemanticFinding("SEM202", "warning", f"Function '{node.name}' has {len(node.args.args)} parameters", "Reduce parameter count, use object/dict"))
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.iter, ast.Call) and hasattr(node.iter.func, 'id') and node.iter.func.id == 'range':
            pass
        self.generic_visit(node)

    def visit_Try(self, node):
        if len(node.handlers) == 1 and node.handlers[0].type is None:
            self.findings.append(SemanticFinding("SEM203", "error", "Bare except clause", "Catch specific exception type"))
        self.generic_visit(node)

if __name__ == "__main__":
    analyzer = SemanticAnalyzer()
    test = """
def long_function(a, b, c, d, e, f, g, h):
    x = a + b
    y = c + d
    z = e + f
    return x + y + z + g + h

def another():
    try:
        eval("1+1")
    except:
        pass
"""
    findings = analyzer.analyze(test, "python")
    for f in findings:
        print(f"[{f.rule_id}] [{f.severity}] {f.message}")
    metrics = analyzer.analyze_complexity(test)
    print(metrics)
