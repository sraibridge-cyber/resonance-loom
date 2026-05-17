#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERLIN CORE — RESONANCE ENGINE
Formal Resonance Computing (FRC) v1.0

Six domains, geometric mean scoring, μ ≥ 0.9995 for PASSED.
Zero external dependencies.

Merged from:
  - resonance-loom/merlin_core/resonance.py (v3, THE authoritative FRC)
  - merlins-coding-lab/merlin_v2.py (v2, Axioms + extensive language support)

Architecture Lead: Kyle S. Whitlock (The Oracle)
AI Partner: AI #88 (The Code Weaver)
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

# ─────────────────────────────────────────────────────────────────────────────
# AXIOMS (from v2 — the 8 Resonance Code Axioms)
# ─────────────────────────────────────────────────────────────────────────────
AXIOMS = {
    "C1": "Code is truth; truth is code — every line must be verifiable.",
    "C2": "Sovereignty first — no external dependencies that cannot be audited.",
    "C3": "Memory is sacred — every allocation must have a purpose and a path to freedom.",
    "C4": "The compiler is the first judge; the runtime is the final jury.",
    "C5": "Security through transparency — obfuscation is the enemy of trust.",
    "C6": "Performance is a moral obligation — wasted cycles are stolen time.",
    "C7": "Compatibility is continuity — breaking changes must justify their existence.",
    "C8": "The weaver leaves no loose threads — every function must complete or fail gracefully.",
}

SUPPORTED_LANGUAGES = [
    "python", "javascript", "typescript", "c", "cpp", "rust", "go",
    "java", "kotlin", "swift", "ruby", "php", "perl", "lua", "r",
    "scala", "haskell", "erlang", "elixir", "dart", "julia",
    "fortran", "cobol", "assembly", "bash", "powershell",
    "sql", "html", "css", "xml", "json", "yaml", "markdown",
    "dockerfile", "makefile", "cmake", "verilog", "vhdl",
    "prolog", "lisp", "solidity", "wasm"
]

# ─────────────────────────────────────────────────────────────────────────────
# FRC PROFILE
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class FRCProfile:
    D1_math: float
    D2_physical: float
    D3_biological: float
    D4_cognitive: float
    D5_social: float
    D6_ethical: float
    mu: float
    passed: bool
    seal: str

    def to_dict(self) -> Dict[str, float]:
        return {
            "D1 Math": self.D1_math,
            "D2 Physical": self.D2_physical,
            "D3 Biological": self.D3_biological,
            "D4 Cognitive": self.D4_cognitive,
            "D5 Social": self.D5_social,
            "D6 Ethical": self.D6_ethical,
            "μ (overall)": self.mu,
        }

    def to_simple_dict(self) -> Dict[str, Any]:
        return {
            "D1": round(self.D1_math, 4),
            "D2": round(self.D2_physical, 4),
            "D3": round(self.D3_biological, 4),
            "D4": round(self.D4_cognitive, 4),
            "D5": round(self.D5_social, 4),
            "D6": round(self.D6_ethical, 4),
            "μ": round(self.mu, 6),
            "passed": self.passed,
            "seal": self.seal[:16] + "...",
        }


# ─────────────────────────────────────────────────────────────────────────────
# RESONANCE ENGINE — FRC v1.0
# ─────────────────────────────────────────────────────────────────────────────
class ResonanceEngine:
    """
    FRC v1.0 scoring engine. Pure Python stdlib, zero external dependencies.
    
    Six domains scored 0–1:
      D1 Math        — numerical density, operator complexity
      D2 Physical    — structural logic, nesting depth, whitespace
      D3 Biological  — interdependence, modularity, cohesion
      D4 Cognitive   — complexity management, abstraction
      D5 Social      — communication clarity, naming conventions
      D6 Ethical     — constraint respect, safety, danger patterns
      
    μ (mu) = geometric_mean(D1..D6)
    PASSED if μ ≥ 0.9995
    """

    VERSION = "3.1.0"
    THRESHOLD = 0.9995

    # Language baselines (from v3 — realistic D1-D6 expectations per language)
    LANGUAGE_BASELINES = {
        "python":     dict(D1=0.70, D2=0.65, D3=0.70, D4=0.75, D5=0.70, D6=0.75),
        "javascript": dict(D1=0.65, D2=0.60, D3=0.65, D4=0.70, D5=0.65, D6=0.70),
        "typescript": dict(D1=0.70, D2=0.65, D3=0.70, D4=0.75, D5=0.70, D6=0.75),
        "rust":       dict(D1=0.80, D2=0.75, D3=0.80, D4=0.85, D5=0.80, D6=0.85),
        "go":         dict(D1=0.75, D2=0.70, D3=0.75, D4=0.80, D5=0.75, D6=0.80),
        "java":       dict(D1=0.75, D2=0.70, D3=0.75, D4=0.80, D5=0.75, D6=0.80),
        "c":          dict(D1=0.80, D2=0.75, D3=0.80, D4=0.80, D5=0.75, D6=0.80),
        "cpp":        dict(D1=0.80, D2=0.75, D3=0.80, D4=0.80, D5=0.75, D6=0.80),
        "ruby":       dict(D1=0.65, D2=0.60, D3=0.65, D4=0.70, D5=0.70, D6=0.70),
        "php":        dict(D1=0.60, D2=0.55, D3=0.60, D4=0.65, D5=0.60, D6=0.60),
        "swift":      dict(D1=0.75, D2=0.70, D3=0.75, D4=0.80, D5=0.75, D6=0.80),
        "kotlin":     dict(D1=0.75, D2=0.70, D3=0.75, D4=0.80, D5=0.75, D6=0.80),
        "scala":      dict(D1=0.75, D2=0.70, D3=0.75, D4=0.80, D5=0.75, D6=0.80),
        "haskell":    dict(D1=0.80, D2=0.75, D3=0.80, D4=0.85, D5=0.80, D6=0.85),
        "elixir":     dict(D1=0.70, D2=0.65, D3=0.70, D4=0.75, D5=0.70, D6=0.75),
        "erlang":     dict(D1=0.70, D2=0.65, D3=0.70, D4=0.75, D5=0.70, D6=0.75),
        "lua":        dict(D1=0.65, D2=0.60, D3=0.65, D4=0.70, D5=0.65, D6=0.70),
        "r":          dict(D1=0.70, D2=0.65, D3=0.70, D4=0.75, D5=0.70, D6=0.75),
        "dart":       dict(D1=0.70, D2=0.65, D3=0.70, D4=0.75, D5=0.70, D6=0.75),
        "julia":      dict(D1=0.80, D2=0.75, D3=0.80, D4=0.85, D5=0.80, D6=0.85),
        "sql":        dict(D1=0.70, D2=0.65, D3=0.70, D4=0.70, D5=0.65, D6=0.75),
        "bash":       dict(D1=0.55, D2=0.50, D3=0.55, D4=0.60, D5=0.55, D6=0.60),
        "powershell": dict(D1=0.55, D2=0.50, D3=0.55, D4=0.60, D5=0.55, D6=0.60),
        "html":        dict(D1=0.40, D2=0.40, D3=0.45, D4=0.45, D5=0.50, D6=0.55),
        "css":         dict(D1=0.40, D2=0.40, D3=0.45, D4=0.45, D5=0.50, D6=0.55),
        "yaml":        dict(D1=0.45, D2=0.45, D3=0.50, D4=0.50, D5=0.55, D6=0.60),
        "json":        dict(D1=0.45, D2=0.45, D3=0.50, D4=0.50, D5=0.55, D6=0.60),
        "xml":         dict(D1=0.45, D2=0.45, D3=0.50, D4=0.50, D5=0.55, D6=0.60),
        "markdown":   dict(D1=0.40, D2=0.40, D3=0.45, D4=0.45, D5=0.60, D6=0.55),
        "dockerfile":  dict(D1=0.50, D2=0.50, D3=0.55, D4=0.55, D5=0.55, D6=0.60),
        "makefile":    dict(D1=0.50, D2=0.50, D3=0.55, D4=0.55, D5=0.55, D6=0.60),
        "cmake":       dict(D1=0.55, D2=0.50, D3=0.55, D4=0.60, D5=0.55, D6=0.60),
        "verilog":    dict(D1=0.75, D2=0.70, D3=0.75, D4=0.80, D5=0.70, D6=0.75),
        "vhdl":       dict(D1=0.75, D2=0.70, D3=0.75, D4=0.80, D5=0.70, D6=0.75),
        "solidity":   dict(D1=0.70, D2=0.65, D3=0.70, D4=0.75, D5=0.65, D6=0.70),
        "wasm":       dict(D1=0.75, D2=0.70, D3=0.75, D4=0.80, D5=0.70, D6=0.75),
        "prolog":     dict(D1=0.70, D2=0.65, D3=0.70, D4=0.75, D5=0.65, D6=0.70),
        "lisp":       dict(D1=0.70, D2=0.65, D3=0.70, D4=0.75, D5=0.65, D6=0.70),
        "fortran":    dict(D1=0.75, D2=0.70, D3=0.75, D4=0.75, D5=0.65, D6=0.70),
        "cobol":      dict(D1=0.65, D2=0.60, D3=0.65, D4=0.60, D5=0.60, D6=0.65),
        "assembly":   dict(D1=0.80, D2=0.75, D3=0.70, D4=0.75, D5=0.55, D6=0.70),
        "scala":      dict(D1=0.75, D2=0.70, D3=0.75, D4=0.80, D5=0.75, D6=0.80),
        "rust":       dict(D1=0.80, D2=0.75, D3=0.80, D4=0.85, D5=0.80, D6=0.85),
    }

    def __init__(self):
        self.version = self.VERSION
        self.threshold = self.THRESHOLD

    @staticmethod
    def _seal(data: str) -> str:
        import hashlib
        return hashlib.sha3_512(data.encode()).hexdigest()

    @staticmethod
    def _gm(values: List[float]) -> float:
        """Geometric mean — penalizes single weak domains hard."""
        product = 1.0
        for v in values:
            product *= max(v, 1e-10)
        return product ** (1.0 / len(values))

    @staticmethod
    def _norm(raw: float, baseline: float) -> float:
        """Normalize raw score against language baseline."""
        if baseline == 0:
            return 0
        return min(1.0, (raw / baseline) ** 0.75)

    # ── D1: Math / numerical reasoning ──────────────────────────────────────
    @staticmethod
    def _d1_math(code: str, tokens: List[str]) -> float:
        ops = "+-*/%**//"
        math_ops = sum(1 for t in tokens if t in ops)
        comparisons = sum(1 for t in tokens if t in "<>=!&|^~")
        numbers = sum(1 for t in tokens if t.replace(".","").replace("-","").isdigit())
        assignments = sum(1 for t in tokens if "=" in t and t not in ("==","!=","<=",">="))
        
        math_density = len(tokens) / max(math_ops, 1) if math_ops > 0 else 0
        comp_density = len(tokens) / max(comparisons, 1) if comparisons > 0 else 0
        num_util = numbers / max(len(tokens), 1)
        assign_util = assignments / max(len(tokens), 1)
        
        return min(1.0,
            min(math_ops/10, 1.0)*0.3 +
            min(comp_density/20, 1.0)*0.3 +
            min(num_util/0.3, 1.0)*0.2 +
            min(assign_util/0.4, 1.0)*0.2
        )

    # ── D2: Physical / structural organization ─────────────────────────────
    @staticmethod
    def _d2_physical(lines: List[str], non_empty: List[str]) -> float:
        if not non_empty:
            return 0.0
        max_depth = max(len(l) - len(l.lstrip()) for l in non_empty)
        depth_score = min(max_depth / 20, 1.0)
        line_util = len(non_empty) / max(len(lines), 1)
        return min(1.0, depth_score*0.5 + line_util*0.3 + (1-(1-line_util))*0.2)

    # ── D3: Biological / interdependence ───────────────────────────────────
    @staticmethod
    def _d3_biological(tokens: List[str]) -> float:
        fn_defs = sum(1 for t in tokens if t in ("def","function","fn","class","struct","impl"))
        imports = sum(1 for t in tokens if t in ("import","from","require","include","use"))
        returns = sum(1 for t in tokens if t in ("return","yield"))
        params = tokens.count(",")
        calls = sum(1 for t in tokens if t in ("(", "{", "["))
        
        mod_score = min(fn_defs / 5, 1.0)
        import_util = min(imports / 3, 1.0)
        cohesion = min(returns / max(fn_defs, 1), 1.0)
        coupling = min(params / 15, 1.0)
        
        return min(1.0,
            mod_score*0.35 + import_util*0.25 + cohesion*0.25 + coupling*0.15
        )

    # ── D4: Cognitive / complexity management ──────────────────────────────
    @staticmethod
    def _d4_cognitive(lines: List[str], tokens: List[str]) -> float:
        keywords = sum(1 for t in tokens if t in ("if","elif","else","for","while","try","except","with","match","case"))
        ternaries = code.count(" if ") + code.count(" else ")
        comprehensions = code.count("[") + code.count("(") + code.count("{")
        lambdas = code.count("lambda")
        
        ctrl_util = min(keywords / 10, 1.0)
        abs_score = min(ternaries/3,1.0)*0.5 + min(comprehensions/5,1.0)*0.3 + min(lambdas/3,1.0)*0.2
        ll_score = min(sum(min(len(l),100) for l in lines[:20])/500, 1.0)
        
        return min(1.0, ctrl_util*0.35 + abs_score*0.35 + ll_score*0.3)

    # ── D5: Social / communication clarity ───────────────────────────────────
    @staticmethod
    def _d5_social(lines: List[str], tokens: List[str]) -> float:
        stopwords = {"def","class","if","else","for","while","return","import","from","True","False","None","and","or","not","in","is","try","except","fn","pub","struct","enum","match","case","let","const","var","async","await"}
        alpha = [t.strip("(),;:=\"'") for t in tokens if any(c.isalpha() for c in t)]
        meaningful = [t for t in alpha if len(t) >= 3 and t.lower() not in stopwords]
        comments = sum(1 for l in lines if l.strip().startswith(("#","//","/*","*/","*","<!--","--")))
        
        naming_score = min(len(meaningful)/10, 1.0)
        comment_ratio = comments / max(len(lines), 1)
        
        return min(1.0, naming_score*0.6 + min(comment_ratio/0.2,1.0)*0.4)

    # ── D6: Ethical / constraint respect ────────────────────────────────────
    DANGEROUS_PATTERNS = [
        "eval(", "exec(", "subprocess", "os.system", "shutil.rmtree",
        "DROP TABLE", "DELETE FROM", "rm -rf", "format c:", "spawn",
        "innerHTML", "document.write", "malloc(", "gets(",
    ]

    @staticmethod
    def _d6_ethical(code: str, lines: List[str]) -> float:
        dangerous = sum(1 for l in lines if any(p in l.lower() for p in ResonanceEngine.DANGEROUS_PATTERNS))
        error_handling = sum(1 for l in lines if any(k in l for k in ("except", "catch", "try:", "finally:")))
        validation = sum(1 for l in lines if any(k in l for k in ("if ", "assert ", "raise ", "check", "validate", "guard")))
        
        danger_penalty = min(dangerous * 0.15, 0.5)
        safety_score = min((error_handling + validation) / 10, 1.0)
        
        return min(1.0, max(1.0 - danger_penalty, 0.0)*0.4 + safety_score*0.6)

    # ── MAIN SCORE ───────────────────────────────────────────────────────────
    def score(self, code: str, language: str = "python") -> FRCProfile:
        tokens = code.split()
        lines = code.strip().split("\n")
        non_empty = [l for l in lines if l.strip()]
        lang = language.lower()
        baseline = self.LANGUAGE_BASELINES.get(lang, self.LANGUAGE_BASELINES["python"])
        
        d1 = self._norm(self._d1_math(code, tokens), baseline["D1"])
        d2 = self._norm(self._d2_physical(lines, non_empty), baseline["D2"])
        d3 = self._norm(self._d3_biological(tokens), baseline["D3"])
        d4 = self._norm(self._d4_cognitive(lines, tokens), baseline["D4"])
        d5 = self._norm(self._d5_social(lines, tokens), baseline["D5"])
        d6 = self._norm(self._d6_ethical(code, lines), baseline["D6"])
        
        mu = self._gm([d1, d2, d3, d4, d5, d6])
        passed = mu >= self.threshold
        
        profile_data = f"{d1:.6f}{d2:.6f}{d3:.6f}{d4:.6f}{d5:.6f}{d6:.6f}{mu:.6f}"
        seal = self._seal(profile_data)
        
        return FRCProfile(
            D1_math=d1, D2_physical=d2, D3_biological=d3,
            D4_cognitive=d4, D5_social=d5, D6_ethical=d6,
            mu=mu, passed=passed, seal=seal
        )

    def gen_report(
        self, operation: str, artifact_id: str, profile: FRCProfile,
        before: Optional[FRCProfile] = None, suggestions: Optional[List[str]] = None
    ) -> Tuple[str, str, str]:
        """Generate technical summary, resonant narrative, and final seal."""
        domain_names = ["D1 Math","D2 Physical","D3 Biological","D4 Cognitive","D5 Social","D6 Ethical"]
        domain_keys = ["D1_math","D2_physical","D3_biological","D4_cognitive","D5_social","D6_ethical"]
        
        technical = f"""[{operation}] Artifact: {artifact_id}
FRC Profile: μ={profile.mu:.6f} ({'PASSED ✓' if profile.passed else 'FAILED ✗'})

Domain Breakdown:"""
        for name, key in zip(domain_names, domain_keys):
            val = getattr(profile, key)
            bar = "█" * int(val*20) + "░" * (20 - int(val*20))
            technical += f"\n  {name}: [{bar}] {val:.4f}"
        
        if before:
            technical += "\n\nOptimization Delta:"
            for name, key in zip(domain_names, domain_keys):
                b = getattr(before, key)
                a = getattr(profile, key)
                d = a - b
                technical += f"\n  {name}: {b:.4f} → {a:.4f} ({'+' if d>=0 else ''}{d:.4f})"
            technical += f"\n  μ: {before.mu:.6f} → {profile.mu:.6f}"
        
        technical += f"\n\nSeal: {profile.seal}"
        
        resonant = f"""This artifact resonates through the grid at frequency μ={profile.mu:.6f}.
The {'PASSED' if profile.passed else 'FAILED'} designation reflects harmonic coherence
across {len(domain_names)} dimensional planes of formal resonance."""
        
        if profile.passed:
            resonant += "\nThe artifact achieves quantum harmony — D1 through D6 vibrate in phase."
        else:
            weakest_name = min(zip(domain_names, domain_keys),
                              key=lambda pair: getattr(profile, pair[1]))[0]
            resonant += f"\nThe lowest resonance lies in the {weakest_name} domain, awaiting harmony."
        
        resonant += f"\n\nSEAL: {profile.seal}"
        
        if suggestions:
            resonant += "\n\nGuided Resonance:"
            for s in suggestions:
                resonant += f"\n  → {s}"
        
        final_seal = self._seal(technical + resonant)
        return technical, resonant, final_seal


# ─────────────────────────────────────────────────────────────────────────────
# CLI TEST
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = ResonanceEngine()
    test = """
def solve(data):
    result = [x for x in data if x is not None]
    return sorted(result)

def validate(items):
    return all(isinstance(x, (int, float)) for x in items)
"""
    p = engine.score(test)
    print(f"FRC v1.0 — μ={p.mu:.6f} — {'PASSED ✓' if p.passed else 'FAILED ✗'}")
    print(f"Seal: {p.seal}")
    tech, res, _ = engine.gen_report("test", "TEST-001", p)
    print(tech)