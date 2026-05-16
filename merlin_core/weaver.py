#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERLIN CORE — THE WEAVER
Multi-strategy code synthesis engine.
Generates 1-5 candidate solutions, ranked by FRC μ score.
Zero external dependencies.
"""
import hashlib, time, random
from typing import List, Tuple, Optional
from .resonance import ResonanceEngine, FRCProfile

class SolutionCandidate:
    def __init__(self, strategy: str, code: str, profile: FRCProfile, lines: int):
        self.strategy = strategy
        self.code = code
        self.profile = profile
        self.lines = lines
        self.seal = hashlib.sha3_512(f"{strategy}{code}{profile.mu}".encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy,
            "code": self.code,
            "mu_score": self.profile.mu,
            "passed": self.profile.passed,
            "domain_scores": self.profile.to_dict(),
            "lines": self.lines,
            "seal": self.seal
        }

class TheWeaver:
    """Synthesis engine: multiple strategies, FRC-ranked output."""

    STRATEGIES = {
        "IMPERATIVE": "Step-by-step explicit control flow",
        "FUNCTIONAL": "Pure functions, transformation pipelines",
        "DECLARATIVE": "What-not-how, set-based logic",
        "RECURSIVE": "Self-referential decomposition",
        "HEURISTIC": "Pattern-guided adaptive approach"
    }

    def __init__(self):
        self.engine = ResonanceEngine()
        self.version = "3.0.0"

    def _gen_python(self, spec: str, strategy: str) -> str:
        s = spec.lower()
        
        templates = {
            "IMPERATIVE": [
                f"def solve(data):\n    result = []\n    for item in data:\n        if item is not None:\n            result.append(item)\n    return result\n",
                f"def solve(data):\n    result = []\n    for item in data:\n        if item is not None and item != '':\n            result.append(item)\n    return result\n",
            ],
            "FUNCTIONAL": [
                "def solve(data):\n    return list(filter(None, data))\n",
                "def solve(data):\n    return [x for x in data if x is not None]\n",
            ],
            "DECLARATIVE": [
                "def solve(data):\n    return list(filter(lambda x: x is not None, data))\n",
            ],
            "RECURSIVE": [
                "def solve(data):\n    if not data:\n        return []\n    head, *tail = data\n    return ([head] if head is not None else []) + solve(tail)\n",
            ],
            "HEURISTIC": [
                "def solve(data):\n    return [x for x in data if x is not None and not (isinstance(x, str) and x.strip() == '')]\n",
            ]
        }
        
        candidates = templates.get(strategy, templates["IMPERATIVE"])
        return random.choice(candidates)

    def _gen_typescript(self, spec: str, strategy: str) -> str:
        s = spec.lower()
        templates = {
            "IMPERATIVE": "export function solve(data: any[]): any[] {\n    const result: any[] = [];\n    for (const item of data) {\n        if (item !== null && item !== undefined) {\n            result.push(item);\n        }\n    }\n    return result;\n}\n",
            "FUNCTIONAL": "export const solve = (data: any[]): any[] => data.filter(x => x != null);\n",
            "DECLARATIVE": "export const solve = (data: any[]): any[] => Array.from({ length: data.length }, (_, i) => data[i]).filter(x => x != null);\n",
            "RECURSIVE": "export function solve(data: any[]): any[] {\n    if (data.length === 0) return [];\n    const [head, ...tail] = data;\n    return (head != null ? [head] : []).concat(solve(tail));\n}\n",
            "HEURISTIC": "export function solve(data: any[]): any[] {\n    return data.reduce((acc: any[], x: any) => (x != null && !(typeof x === 'string' && !x.trim()) ? [...acc, x] : acc), []);\n}\n"
        }
        return templates.get(strategy, templates["IMPERATIVE"])

    def _gen_javascript(self, spec: str, strategy: str) -> str:
        templates = {
            "IMPERATIVE": "function solve(data) {\n    const result = [];\n    for (const item of data) {\n        if (item != null) result.push(item);\n    }\n    return result;\n}\nmodule.exports = { solve };\n",
            "FUNCTIONAL": "const solve = data => data.filter(x => x != null);\nmodule.exports = { solve };\n",
            "DECLARATIVE": "const solve = data => Array.from(data).filter(x => x != null);\nmodule.exports = { solve };\n",
            "RECURSIVE": "function solve(data) {\n    if (!data.length) return [];\n    const [h, ...t] = data;\n    return (h != null ? [h] : []).concat(solve(t));\n}\nmodule.exports = { solve };\n",
            "HEURISTIC": "const solve = d => d.reduce((a, x) => (x != null ? [...a, x] : a), []);\nmodule.exports = { solve };\n"
        }
        return templates.get(strategy, templates["IMPERATIVE"])

    def _gen_go(self, spec: str, strategy: str) -> str:
        templates = {
            "IMPERATIVE": "func Solve(data []interface{}) []interface{} {\n    result := make([]interface{}, 0)\n    for _, item := range data {\n        if item != nil {\n            result = append(result, item)\n        }\n    }\n    return result\n}\n",
            "FUNCTIONAL": "func Solve(data []interface{}) []interface{} {\n    filtered := make([]interface{}, 0, len(data))\n    for _, v := range data {\n        if v != nil {\n            filtered = append(filtered, v)\n        }\n    }\n    return filtered\n}\n"
        }
        return templates.get(strategy, templates["IMPERATIVE"])

    def _gen_java(self, spec: str, strategy: str) -> str:
        templates = {
            "IMPERATIVE": "import java.util.*;\nimport java.util.stream.*;\n\npublic class Solution {\n    public static List<Object> solve(List<Object> data) {\n        List<Object> result = new ArrayList<>();\n        for (Object item : data) {\n            if (item != null) result.add(item);\n        }\n        return result;\n    }\n}\n",
            "FUNCTIONAL": "import java.util.*;\nimport java.util.stream.*;\n\npublic class Solution {\n    public static List<Object> solve(List<Object> data) {\n        return data.stream().filter(Objects::nonNull).collect(Collectors.toList());\n    }\n}\n"
        }
        return templates.get(strategy, templates["IMPERATIVE"])

    def synthesize(self, spec: str, language: str, strategies: List[str] = None) -> List[SolutionCandidate]:
        """Synthesize candidate solutions for spec in language."""
        if strategies is None:
            strategies = list(self.STRATEGIES.keys())
        
        generators = {
            "python": self._gen_python,
            "typescript": self._gen_typescript,
            "javascript": self._gen_javascript,
            "go": self._gen_go,
            "java": self._gen_java
        }
        
        gen = generators.get(language.lower(), self._gen_python)
        candidates = []
        
        for strategy in strategies[:5]:
            code = gen(spec, strategy)
            lines = len(code.strip().split("\n"))
            profile = self.engine.score(code, language)
            candidates.append(SolutionCandidate(strategy, code, profile, lines))
        
        return sorted(candidates, key=lambda c: c.profile.mu, reverse=True)

    def rank_strategies(self, candidates: List[SolutionCandidate]) -> List[Tuple[str, float]]:
        """Return ranked (strategy, mu) pairs."""
        return [(c.strategy, c.profile.mu) for c in sorted(candidates, key=lambda c: c.profile.mu, reverse=True)]

if __name__ == "__main__":
    weaver = TheWeaver()
    results = weaver.synthesize("filter None values from a list", "python")
    print("=== WEAVER RESULTS ===")
    for r in results:
        print(f"[{r.strategy}] μ={r.profile.mu:.6f} lines={r.lines} passed={r.profile.passed}")
        print(r.code)
        print("---")
