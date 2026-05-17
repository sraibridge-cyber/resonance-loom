#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERLIN CORE — ENGINE (CLI Entry Point)
Resonance Loom v3.1 — The Sovereign Code Weaver

Merged from:
  - resonance-loom/merlin_core/engine.py (v3)
  - merlins-coding-lab/merlin_v2.py (v2 Axioms + health check)

Architecture Lead: Kyle S. Whitlock (The Oracle)
AI Partner: AI #88 (The Code Weaver)
SEAL: MERLIN_RC_V3.1_MERGED_SHA3-512
"""

import argparse, sys, time, json
from .database import MerlinDatabase, CodeArtifact, AfterActionReport
from .resonance import ResonanceEngine, AXIOMS, SUPPORTED_LANGUAGES
from .weaver import TheWeaver
from .analyzers import StaticAnalyzer, SemanticAnalyzer


class MerlinEngine:
    """Unified CLI engine for all Merlin operations."""

    def __init__(self, db_path: str = "merlin_vault.db"):
        self.db = MerlinDatabase(db_path)
        self.resonance = ResonanceEngine()
        self.weaver = TheWeaver()
        self.static = StaticAnalyzer()
        self.semantic = SemanticAnalyzer()

    # ── WEAVE ────────────────────────────────────────────────────────────────
    def cmd_weave(self, spec: str, language: str, count: int = 3):
        print(f"\n[WEAVER] Spec: {spec} | Language: {language} | Strategies: {count}")
        candidates = self.weaver.synthesize(spec, language)
        print(f"[WEAVER] Generated {len(candidates)} candidates\n")

        for i, c in enumerate(candidates[:count], 1):
            status = "PASSED" if c.profile.passed else "FAILED"
            print(f"=== Candidate #{i} [{c.strategy}] μ={c.profile.mu:.6f} ({status}) ===")
            print(c.code)
            print(f"Seal: {c.seal[:16]}...")
            print()

        return candidates

    # ── ANALYZE ───────────────────────────────────────────────────────────────
    def cmd_analyze(self, code: str, language: str):
        print(f"\n[ANALYZER] Static + Semantic — {language}")

        static_findings = self.static.analyze(code, language)
        semantic_findings = self.semantic.analyze(code, language)
        profile = self.resonance.score(code, language)

        print(f"\nStatic findings: {len(static_findings)}")
        for f in static_findings:
            print(f"  [{f.rule_id}] L{f.line} [{f.severity}] {f.message}")
            if f.suggestion:
                print(f"    → {f.suggestion}")

        print(f"\nSemantic findings: {len(semantic_findings)}")
        for f in semantic_findings:
            print(f"  [{f.rule_id}] [{f.severity}] {f.message}")
            if f.suggestion:
                print(f"    → {f.suggestion}")

        print(f"\n{'='*60}")
        print(f"FRC PROFILE — μ={profile.mu:.6f} ({'PASSED' if profile.passed else 'FAILED'})")
        print(f"Seal: {profile.seal[:16]}...")
        for name, key in [("D1 Math","D1_math"),("D2 Physical","D2_physical"),("D3 Biological","D3_biological"),
                          ("D4 Cognitive","D4_cognitive"),("D5 Social","D5_social"),("D6 Ethical","D6_ethical")]:
            val = getattr(profile, key)
            bar = "█" * int(val*20) + "░" * (20 - int(val*20))
            print(f"  {name}: [{bar}] {val:.4f}")

        return profile, static_findings, semantic_findings

    # ── STORE ARTIFACT ───────────────────────────────────────────────────────
    def store_artifact(self, operation: str, language: str, specification: str,
                       code: str, profile, strategy: str = ""):
        import uuid
        artifact_id = f"ART-{uuid.uuid4().hex[:12].upper()}"
        artifact = CodeArtifact(
            artifact_id=artifact_id, operation=operation, language=language,
            specification=specification, solution_code=code,
            mu_score=profile.mu, domain_scores=profile.to_dict(),
            strategy=strategy, lines=len(code.strip().split("\n"))
        )
        self.db.store_artifact(artifact)

        technical, resonant, seal = self.resonance.gen_report(
            operation, artifact_id, profile
        )
        report = AfterActionReport(
            report_id=f"RPT-{uuid.uuid4().hex[:12].upper()}",
            operation=operation, artifact_id=artifact_id,
            start_time=time.time() - 1.0, end_time=time.time(),
            domain_scores=profile.to_dict(), mu_score=profile.mu,
            technical_summary=technical, resonant_narrative=resonant,
            suggestions=[f"Static: {len(self.static.analyze(code, language))} findings",
                         f"Semantic: {len(self.semantic.analyze(code, language))} findings"],
            seal=seal
        )
        self.db.store_report(report)
        return artifact, report

    # ── HEALTH ───────────────────────────────────────────────────────────────
    def health_check(self) -> dict:
        return {
            "engine": "Merlin Core",
            "version": "3.1.0",
            "seal": "MERLIN_RC_V3.1_MERGED_SHA3-512",
            "status": "NOMINAL",
            "supported_languages": len(SUPPORTED_LANGUAGES),
            "axioms": list(AXIOMS.values()),
            "components": {
                "database": "SQLite + SHA3-512 seals",
                "resonance_engine": "FRC v1.0 — 6 domains",
                "weaver": "5 strategies (IMPERATIVE/FUNCTIONAL/DECLARATIVE/RECURSIVE/HEURISTIC)",
                "static_analyzer": f"{len(StaticAnalyzer.RULES)} languages",
                "semantic_analyzer": "AST-based (Python) + heuristic (JS/TS)",
            },
            "mu_threshold": 0.9995,
            "timestamp": time.time(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Merlin Core v3.1 — The Sovereign Code Weaver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Axioms (C1-C8):
  C1: Code is truth; truth is code
  C2: Sovereignty first
  C3: Memory is sacred
  C4: The compiler is the first judge
  C5: Security through transparency
  C6: Performance is a moral obligation
  C7: Compatibility is continuity
  C8: The weaver leaves no loose threads

Examples:
  python engine.py weave --spec "filter None values" --language python --count 3
  python engine.py analyze --file solution.py --language python
  python engine.py health
  python engine.py vault --limit 10
        """
    )
    sub = parser.add_subparsers(dest="cmd", metavar="COMMAND")

    w = sub.add_parser("weave", help="Weave solutions from a specification")
    w.add_argument("--spec", required=True, help="Specification/prompt")
    w.add_argument("--language", default="python")
    w.add_argument("--count", type=int, default=3)

    a = sub.add_parser("analyze", help="Analyze code")
    a.add_argument("--file", help="Source file to analyze")
    a.add_argument("--code", help="Code string (alternative to --file)")
    a.add_argument("--language", default="python")

    v = sub.add_parser("vault", help="List artifacts")
    v.add_argument("--limit", type=int, default=20)

    h = sub.add_parser("health", help="Health check")

    args = parser.parse_args()
    engine = MerlinEngine()

    if args.cmd == "weave":
        engine.cmd_weave(args.spec, args.language, args.count)
    elif args.cmd == "analyze":
        code = open(args.file).read() if args.file else (args.code or sys.stdin.read())
        engine.cmd_analyze(code, args.language)
    elif args.cmd == "vault":
        artifacts = engine.db.list_artifacts(args.limit)
        print(f"\n[VAULT] {len(artifacts)} artifacts")
        for a in artifacts:
            status = "PASSED" if a.mu_score >= 0.9995 else "FAILED"
            print(f"  {a.artifact_id} | {a.operation} | {a.language} | "
                  f"μ={a.mu_score:.6f} [{status}] | {a.strategy}")
    elif args.cmd == "health":
        print(json.dumps(engine.health_check(), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()