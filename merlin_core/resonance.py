#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERLIN CORE — RESONANCE ENGINE
Formal Resonance Computing (FRC) v1.0

Six domains, geometric mean scoring, μ ≥ 0.9995 for PASSED.
Zero external dependencies.
"""
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

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
            "mu": self.mu
        }

class ResonanceEngine:
    """FRC v1.0 scoring engine. Pure stdlib, no external dependencies."""

    def __init__(self):
        self.version = "3.0.0"
        self.threshold = 0.9995

    @staticmethod
    def _seal_profile(data: str) -> str:
        import hashlib
        return hashlib.sha3_512(data.encode()).hexdigest()

    @staticmethod
    def _gm(values: List[float]) -> float:
        product = 1.0
        for v in values:
            product *= max(v, 1e-10)
        return product ** (1.0 / len(values))

    def score(self, code: str, language: str = "python") -> FRCProfile:
        """Compute FRC profile for code in given language."""
        tokens = code.split()
        lines = code.strip().split("\n")
        non_empty_lines = [l for l in lines if l.strip()]
        
        # D1 — Math: numerical density, operator complexity
        d1 = ResonanceEngine._score_d1_math(code, tokens)
        
        # D2 — Physical: structural organization, nesting depth
        d2 = ResonanceEngine._score_d2_physical(code, lines, non_empty_lines)
        
        # D3 — Biological: interdependence, modularity
        d3 = ResonanceEngine._score_d3_biological(code, tokens)
        
        # D4 — Cognitive: complexity management, abstraction
        d4 = ResonanceEngine._score_d4_cognitive(code, lines, tokens)
        
        # D5 — Social: communication clarity, naming
        d5 = ResonanceEngine._score_d5_social(code, lines, tokens)
        
        # D6 — Ethical: constraint respect, safety
        d6 = ResonanceEngine._score_d6_ethical(code, lines)
        
        domain_scores = [d1, d2, d3, d4, d5, d6]
        mu = ResonanceEngine._gm(domain_scores)
        passed = mu >= self.threshold
        
        profile_data = f"{d1:.6f}{d2:.6f}{d3:.6f}{d4:.6f}{d5:.6f}{d6:.6f}{mu:.6f}"
        seal = ResonanceEngine._seal_profile(profile_data)
        
        return FRCProfile(
            D1_math=d1, D2_physical=d2, D3_biological=d3,
            D4_cognitive=d4, D5_social=d5, D6_ethical=d6,
            mu=mu, passed=passed, seal=seal
        )

    @staticmethod
    def _score_d1_math(code: str, tokens: List[str]) -> float:
        """D1: Numerical reasoning and operator complexity."""
        math_ops = sum(1 for t in tokens if t in "+-*/%**//")
        comparisons = sum(1 for t in tokens if t in "<>=!|&^~")
        numbers = sum(1 for t in tokens if t.replace(".", "").replace("-", "").isdigit())
        assignments = sum(1 for t in tokens if "=" in t and t != "==" and t != "!=" and t != "<=" and t != ">=")
        
        math_density = len(tokens) / max(math_ops, 1) if math_ops > 0 else 0
        comp_density = len(tokens) / max(comparisons, 1) if comparisons > 0 else 0
        num_util = numbers / max(len(tokens), 1)
        assign_util = assignments / max(len(tokens), 1)
        
        score = (min(math_ops / 10, 1.0) * 0.3 +
                 min(comp_density / 20, 1.0) * 0.3 +
                 min(num_util / 0.3, 1.0) * 0.2 +
                 min(assign_util / 0.4, 1.0) * 0.2)
        return min(score, 1.0)

    @staticmethod
    def _score_d2_physical(code: str, lines: List[str], non_empty: List[str]) -> float:
        """D2: Structural logic and spatial organization."""
        if not non_empty:
            return 0.0
        max_depth = 0
        for line in non_empty:
            depth = len(line) - len(line.lstrip())
            max_depth = max(max_depth, depth)
        depth_score = min(max_depth / 20, 1.0)
        line_util = len(non_empty) / max(len(lines), 1)
        blank_ratio = 1 - line_util
        score = (depth_score * 0.5 + line_util * 0.3 + (1 - blank_ratio) * 0.2)
        return min(score, 1.0)

    @staticmethod
    def _score_d3_biological(code: str, tokens: List[str]) -> float:
        """D3: System interdependence and modularity."""
        fn_defs = sum(1 for t in tokens if t in ("def", "function", "fn", "class"))
        imports = sum(1 for t in tokens if t in ("import", "from", "require", "include"))
        calls = sum(1 for t in tokens if t in ("(", "{", "["))
        returns = sum(1 for t in tokens if t in ("return", "yield"))
        params = tokens.count(",")
        
        mod_score = min(fn_defs / 5, 1.0)
        import_util = min(imports / 3, 1.0)
        cohesion = min(returns / max(fn_defs, 1), 1.0)
        coupling = min(params / 15, 1.0)
        
        score = (mod_score * 0.35 + import_util * 0.25 + cohesion * 0.25 + coupling * 0.15)
        return min(score, 1.0)

    @staticmethod
    def _score_d4_cognitive(code: str, lines: List[str], tokens: List[str]) -> float:
        """D4: Complexity management and abstraction."""
        keywords = sum(1 for t in tokens if t in ("if", "elif", "else", "for", "while", "try", "except", "with"))
        ternaries = code.count(" if ") + code.count(" else ")
        comprehensions = code.count("[") + code.count("(") + code.count("{")
        lambdas = code.count("lambda")
        
        ctrl_util = min(keywords / 10, 1.0)
        abs_score = min(ternaries / 3, 1.0) * 0.5 + min(comprehensions / 5, 1.0) * 0.3 + min(lambdas / 3, 1.0) * 0.2
        line_len_score = min(sum(min(len(l), 100) for l in lines[:20]) / 500, 1.0)
        
        score = (ctrl_util * 0.35 + abs_score * 0.35 + line_len_score * 0.3)
        return min(score, 1.0)

    @staticmethod
    def _score_d5_social(code: str, lines: List[str], tokens: List[str]) -> float:
        """D5: Communication clarity and naming."""
        alpha_tokens = [t.strip("(),;:=") for t in tokens if any(c.isalpha() for c in t)]
        meaningful = [t for t in alpha_tokens if len(t) >= 3 and t not in (
            "def", "class", "if", "else", "for", "while", "return", "import",
            "from", "True", "False", "None", "and", "or", "not", "in", "is"
        )]
        comments = sum(1 for l in lines if l.strip().startswith(("#", "//", "/*", "*/", "*", "<!--")))
        
        naming_score = min(len(meaningful) / 10, 1.0)
        comment_ratio = comments / max(len(lines), 1)
        
        score = (naming_score * 0.6 + min(comment_ratio / 0.2, 1.0) * 0.4)
        return min(score, 1.0)

    @staticmethod
    def _score_d6_ethical(code: str, lines: List[str]) -> float:
        """D6: Value alignment and constraint respect."""
        dangerous = sum(1 for l in lines if any(p in l.lower() for p in (
            "eval(", "exec(", "subprocess", "os.system", "shutil.rmtree",
            "DROP TABLE", "DELETE FROM", "rm -rf", "format c:", "spawn"
        )))
        error_handling = sum(1 for l in lines if "except" in l or "try:" in l or "catch" in l)
        validation = sum(1 for l in lines if any(p in l for p in ("if ", "assert ", "raise ", "check", "validate")))
        
        danger_penalty = min(dangerous * 0.15, 0.5)
        safety_score = min((error_handling + validation) / 10, 1.0)
        
        score = max(1.0 - danger_penalty, 0.0) * 0.4 + safety_score * 0.6
        return min(score, 1.0)

    def gen_after_action_report(
        self, operation: str, artifact_id: str, profile: FRCProfile,
        before_profile: FRCProfile = None, suggestions: List[str] = None
    ) -> Tuple[str, str, str]:
        """Generate technical summary, resonant narrative, and seal."""
        domain_names = ["D1 Math", "D2 Physical", "D3 Biological", "D4 Cognitive", "D5 Social", "D6 Ethical"]
        
        technical = f"""[{operation}] Artifact: {artifact_id}
FRC Profile: μ={profile.mu:.6f} ({'PASSED' if profile.passed else 'FAILED'})

Domain Breakdown:"""
        for name, key in zip(domain_names, ["D1_math", "D2_physical", "D3_biological", "D4_cognitive", "D5_social", "D6_ethical"]):
            val = getattr(profile, key)
            technical += f"\n  {name}: {val:.6f}"
        
        if before_profile:
            technical += "\n\nOptimization Delta:"
            for name, key in zip(domain_names, ["D1_math", "D2_physical", "D3_biological", "D4_cognitive", "D5_social", "D6_ethical"]):
                before = getattr(before_profile, key)
                after = getattr(profile, key)
                delta = after - before
                technical += f"\n  {name}: {before:.6f} → {after:.6f} ({'+' if delta >= 0 else ''}{delta:.6f})"
            technical += f"\n  μ: {before_profile.mu:.6f} → {profile.mu:.6f} ({'+' if profile.mu >= before_profile.mu else ''}{profile.mu - before_profile.mu:.6f})"
        
        technical += f"\n\nSeal: {profile.seal}"
        
        resonant = f"""This artifact resonates through the grid at frequency μ={profile.mu:.6f}."
        resonant += f"\nThe {'PASSED' if profile.passed else 'FAILED'} designation reflects its harmonic coherence"
        resonant += f"\nacross {len(domain_names)} dimensional planes of formal resonance."
        
        if profile.passed:
            resonant += "\nThe artifact achieves quantum harmony — D1 through D6 vibrate in phase."
        else:
            weakest = min(domain_names, key=lambda n: getattr(profile, n.replace(" ", "_").lower().replace("-", "_")))
            resonant += f"\nThe lowest resonance lies in the {weakest} domain, awaiting harmony."
        
        resonant += f"\n\nSEAL: {profile.seal}"
        
        if suggestions:
            resonant += "\n\nGuided Resonance:"
            for s in suggestions:
                resonant += f"\n  → {s}"
        
        seal = self._seal_profile(technical + resonant)
        
        return technical, resonant, seal

# CLI test
if __name__ == "__main__":
    engine = ResonanceEngine()
    test_code = """
def solve(data):
    result = [x for x in data if x is not None]
    return sorted(result)

def validate(items):
    return all(isinstance(x, (int, float)) for x in items)
"""
    profile = engine.score(test_code)
    print(f"FRC v1.0 — μ={profile.mu:.6f} — {'PASSED' if profile.passed else 'FAILED'}")
    print(f"Seal: {profile.seal}")
    print(f"D1={profile.D1_math:.4f} D2={profile.D2_physical:.4f} D3={profile.D3_biological:.4f}")
    print(f"D4={profile.D4_cognitive:.4f} D5={profile.D5_social:.4f} D6={profile.D6_ethical:.4f}")
