#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERLIN CORE — ENGINE (CLI Entry Point)
Resonance Loom v3 — The Sovereign Code Weaver
Zero external dependencies. Stdlib only.
"""
import argparse, sys, time, json
from .database import MerlinDatabase, CodeArtifact, AfterActionReport
from .resonance import ResonanceEngine
from .weaver import TheWeaver
from .analyzers.static import StaticAnalyzer
from .analyzers.semantic import SemanticAnalyzer

class MerlinEngine:
    def __init__(self, db_path: str = "merlin_vault.db"):
        self.db = MerlinDatabase(db_path)
        self.resonance = ResonanceEngine()
        self.weaver = TheWeaver()
        self.static = StaticAnalyzer()
        self.semantic = SemanticAnalyzer()

    def cmd_weave(self, spec: str, language: str, count: int = 3):
        print(f"\n[WEAVER] Spec: {spec} | Language: {language} | Strategies: {count}")
        candidates = self.weaver.synthesize(spec, language)
        print(f"[WEAVER] Generated {len(candidates)} candidates\n")
        for i, c in enumerate(candidates[:count], 1):
            print(f"=== Candidate #{i} [{c.strategy}] μ={c.profile.mu:.6f} ({'PASSED' if c.profile.passed else 'FAILED'}) ===")
            print(c.code)
            print(f"Seal: {c.seal}")
            print()
        return candidates

    def cmd_analyze(self, code: str, language: str):
        print(f"\n[ANALYZER] Static + Semantic analysis")
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
        print(f"Seal: {profile.seal}")
        domain_names = ["D1 Math", "D2 Physical", "D3 Biological", "D4 Cognitive", "D5 Social", "D6 Ethical"]
        domain_keys = ["D1_math", "D2_physical", "D3_biological", "D4_cognitive", "D5_social", "D6_ethical"]
        for name, key in zip(domain_names, domain_keys):
            val = getattr(profile, key)
            bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
            print(f"  {name}: [{bar}] {val:.4f}")
        
        return profile, static_findings, semantic_findings

    def cmd_serialize(self, profile, static_findings, semantic_findings, spec: str, language: str, strategy: str = "IMPERATIVE") -> CodeArtifact:
        code = ""
        for c in self.weaver.synthesize(spec, language)[:1]:
            code = c.code
            profile = c.profile
        
        import hashlib, uuid
        artifact_id = f"ART-{uuid.uuid4().hex[:12].upper()}"
        lines = len(code.strip().split("\n"))
        
        artifact = CodeArtifact(
            artifact_id=artifact_id,
            operation="weave",
            language=language,
            specification=spec,
            solution_code=code,
            mu_score=profile.mu,
            domain_scores=profile.to_dict(),
            strategy=strategy,
            lines=lines,
            seal=profile.seal
        )
        self.db.store_artifact(artifact)
        
        technical, resonant, seal = self.resonance.gen_after_action_report(
            "weave", artifact_id, profile,
            suggestions=["Static findings: " + str(len(static_findings)), "Semantic findings: " + str(len(semantic_findings))]
        )
        
        report = AfterActionReport(
            report_id=f"RPT-{uuid.uuid4().hex[:12].upper()}",
            operation="weave",
            artifact_id=artifact_id,
            start_time=time.time() - 1.0,
            end_time=time.time(),
            domain_scores=profile.to_dict(),
            mu_score=profile.mu,
            technical_summary=technical,
            resonant_narrative=resonant,
            suggestions=["Static findings: " + str(len(static_findings)), "Semantic findings: " + str(len(semantic_findings))],
            seal=seal
        )
        self.db.store_report(report)
        
        return artifact, report

def main():
    parser = argparse.ArgumentParser(description="Merlin Core — Resonance Loom v3")
    sub = parser.add_subparsers(dest="cmd")

    w = sub.add_parser("weave", help="Weave solutions")
    w.add_argument("--spec", required=True, help="Specification/prompt")
    w.add_argument("--language", default="python", help="Target language")
    w.add_argument("--count", type=int, default=3, help="Number of candidates")

    a = sub.add_parser("analyze", help="Analyze code")
    a.add_argument("--file", help="File to analyze")
    a.add_argument("--language", default="python", help="Language")

    o = sub.add_parser("optimize", help="Optimize code")
    o.add_argument("--file", help="File to optimize")
    o.add_argument("--domain", help="Target domain (D1-D6)")
    o.add_argument("--language", default="python", help="Language")

    s = sub.add_parser("simulate", help="Monte Carlo simulation")
    s.add_argument("--paths", type=int, default=500, help="Number of paths")
    s.add_argument("--steps", type=int, default=25, help="Steps per path")
    s.add_argument("--threshold", type=float, default=0.6, help="Survival threshold")

    v = sub.add_parser("vault", help="List artifacts")
    v.add_argument("--limit", type=int, default=20, help="Number to list")

    args = parser.parse_args()
    engine = MerlinEngine()

    if args.cmd == "weave":
        results = engine.cmd_weave(args.spec, args.language, args.count)
    elif args.cmd == "analyze":
        code = open(args.file).read() if args.file else sys.stdin.read()
        engine.cmd_analyze(code, args.language)
    elif args.cmd == "optimize":
        print("[OPTIMIZER] Domain optimization engine")
        print("  Target domains: D1 Math, D2 Physical, D3 Biological, D4 Cognitive, D5 Social, D6 Ethical")
        print("  (Full optimization requires code input + domain selection)")
    elif args.cmd == "simulate":
        print(f"\n[SIMULATOR] Monte Carlo — {args.paths} paths, {args.steps} steps, threshold {args.threshold}")
        print("  See frontend/Simulate tab for interactive visualization")
    elif args.cmd == "vault":
        artifacts = engine.db.list_artifacts(args.limit)
        print(f"\n[VAULT] {len(artifacts)} artifacts")
        for a in artifacts:
            print(f"  {a.artifact_id} | {a.operation} | {a.language} | μ={a.mu_score:.6f} | {a.strategy}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
