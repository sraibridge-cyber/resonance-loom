#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERLIN CORE — STATIC ANALYZER
Pattern-based linting for 7 languages.
Zero external dependencies.
"""
import re
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class StaticFinding:
    rule_id: str
    severity: str  # "error" | "warning" | "info"
    line: int
    message: str
    suggestion: str

class StaticAnalyzer:
    """Pattern-based static analysis across 7 languages."""

    RULES = {
        "python": [
            {"id": "PY001", "pattern": r"print\s*\(", "severity": "warning", "message": "print() found — use logging module", "suggestion": "import logging; logger.info(...)"},
            {"id": "PY002", "pattern": r"except\s*:\s*$", "severity": "error", "message": "Bare except — too broad", "suggestion": "except Exception as e: ..."},
            {"id": "PY003", "pattern": r"global\s+\w+", "severity": "warning", "message": "Global variable detected", "suggestion": "Pass as parameter or return value"},
            {"id": "PY004", "pattern": r"eval\s*\(", "severity": "error", "message": "eval() is dangerous — code injection risk", "suggestion": "Use ast.literal_eval or json.loads"},
            {"id": "PY005", "pattern": r"exec\s*\(", "severity": "error", "message": "exec() is dangerous — code injection risk", "suggestion": "Refactor to avoid dynamic execution"},
            {"id": "PY006", "pattern": r"if\s+__name__\s*==\s*['\"]__main__['\"]", "severity": "info", "message": "Main guard found — good practice", "suggestion": ""},
            {"id": "PY007", "pattern": r"from\s+\w+\s+import\s+\*", "severity": "warning", "message": "Wildcard import — namespace pollution", "suggestion": "Import specific names"},
            {"id": "PY008", "pattern": r"^\s*def\s+\w+\([^)]*\*[^*]", "severity": "warning", "message": "Complex parameter list", "suggestion": "Use *args and **kwargs sparingly"},
        ],
        "javascript": [
            {"id": "JS001", "pattern": r"var\s+\w+", "severity": "warning", "message": "var found — use const or let", "suggestion": "const for immutable, let for mutable"},
            {"id": "JS002", "pattern": r"==\s*(?!=)", "severity": "warning", "message": "Loose equality — use ===", "suggestion": "Use strict equality (===)"},
            {"id": "JS003", "pattern": r"console\.log", "severity": "warning", "message": "console.log found", "suggestion": "Use a proper logging library"},
            {"id": "JS004", "pattern": r"eval\s*\(", "severity": "error", "message": "eval() is dangerous", "suggestion": "Avoid dynamic code execution"},
            {"id": "JS005", "pattern": r"document\.write", "severity": "error", "message": "document.write is XSS risk", "suggestion": "Use DOM APIs (textContent, innerHTML sanitized)"},
        ],
        "typescript": [
            {"id": "TS001", "pattern": r":\s*any\b", "severity": "warning", "message": "TypeScript any type — use specific types", "suggestion": "Define proper interface or type"},
            {"id": "TS002", "pattern": r"@ts-ignore", "severity": "warning", "message": "@ts-ignore silences type checking", "suggestion": "Fix the type error properly"},
            {"id": "TS003", "pattern": r"var\s+\w+", "severity": "warning", "message": "var found — use const or let", "suggestion": "const for immutable, let for mutable"},
        ],
        "go": [
            {"id": "GO001", "pattern": r"fmt\.Print", "severity": "warning", "message": "fmt.Print found — use structured logging", "suggestion": "Use log/slog package"},
            {"id": "GO002", "pattern": r"panic\s*\(", "severity": "error", "message": "panic detected — handle gracefully", "suggestion": "Return error instead of panic"},
            {"id": "GO003", "pattern": r"^\s*//\+build", "severity": "info", "message": "Build tag found", "suggestion": ""},
        ],
        "java": [
            {"id": "JV001", "pattern": r"catch\s*\(\s*Exception\s*\)", "severity": "warning", "message": "Catching generic Exception", "suggestion": "Catch specific exception types"},
            {"id": "JV002", "pattern": r"System\.out\.print", "severity": "warning", "message": "System.out.print found", "suggestion": "Use a logging framework"},
            {"id": "JV003", "pattern": r"public\s+\w+\s+\w+\s*{", "severity": "info", "message": "Public class/method", "suggestion": "Apply principle of least privilege"},
        ],
        "rust": [
            {"id": "RS001", "pattern": r"\.unwrap\(\)", "severity": "warning", "message": "unwrap() can panic", "suggestion": "Use ? operator or proper error handling"},
            {"id": "RS002", "pattern": r"unsafe\s*{", "severity": "error", "message": "unsafe block — review carefully", "suggestion": "Isolate unsafe code, document invariants"},
        ],
        "c": [
            {"id": "C001", "pattern": r"gets\s*\(", "severity": "error", "message": "gets() is removed from C11 — buffer overflow", "suggestion": "Use fgets() instead"},
            {"id": "C002", "pattern": r"strcpy\s*\(", "severity": "warning", "message": "strcpy — no bounds checking", "suggestion": "Use strncpy or snprintf"},
            {"id": "C003", "pattern": r"malloc\s*\([^)]*\)(?!\s*\(char\*\))", "severity": "warning", "message": "malloc without cast", "suggestion": "Cast to (char*) or use sizeof"},
        ]
    }

    def analyze(self, code: str, language: str) -> List[StaticFinding]:
        findings = []
        rules = self.RULES.get(language.lower(), self.RULES["python"])
        lines = code.split("\n")
        
        for rule in rules:
            for i, line in enumerate(lines, 1):
                if re.search(rule["pattern"], line):
                    findings.append(StaticFinding(
                        rule_id=rule["id"],
                        severity=rule["severity"],
                        line=i,
                        message=rule["message"],
                        suggestion=rule["suggestion"]
                    ))
        
        return findings

    def get_summary(self, findings: List[StaticFinding]) -> Dict[str, int]:
        summary = {"errors": 0, "warnings": 0, "info": 0}
        for f in findings:
            if f.severity in summary:
                summary[f.severity] += 1
        return summary

if __name__ == "__main__":
    analyzer = StaticAnalyzer()
    test = """
def unsafe():
    eval("print('hello')")
    print("debug")
    var x = 5
    """
    findings = analyzer.analyze(test, "python")
    for f in findings:
        print(f"[{f.rule_id}] L{f.line} [{f.severity}] {f.message}")
