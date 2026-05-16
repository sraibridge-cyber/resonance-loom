#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERLIN CORE — DATABASE MODULE
SQLite-backed artifact ledger with SHA3-512 seals.
Zero external dependencies: sqlite3 (stdlib) + hashlib (stdlib).
"""
import sqlite3, hashlib, time, json
from dataclasses import dataclass, field, asdict
from typing import Optional, List

@dataclass
class CodeArtifact:
    artifact_id: str
    operation: str
    language: str
    specification: str
    solution_code: str
    mu_score: float
    domain_scores: dict
    strategy: str
    lines: int
    seal: Optional[str] = None
    created_at: float = field(default_factory=time.time)

@dataclass
class AfterActionReport:
    report_id: str
    operation: str
    artifact_id: str
    start_time: float
    end_time: float
    domain_scores: dict
    mu_score: float
    technical_summary: str
    resonant_narrative: str
    suggestions: List[str]
    seal: Optional[str] = None

class MerlinDatabase:
    def __init__(self, db_path: str = "merlin_vault.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS artifacts (
            artifact_id TEXT PRIMARY KEY,
            operation TEXT, language TEXT, specification TEXT,
            solution_code TEXT, mu_score REAL, domain_scores TEXT,
            strategy TEXT, lines INTEGER, seal TEXT, created_at REAL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS after_action_reports (
            report_id TEXT PRIMARY KEY,
            operation TEXT, artifact_id TEXT,
            start_time REAL, end_time REAL,
            domain_scores TEXT, mu_score REAL,
            technical_summary TEXT, resonant_narrative TEXT,
            suggestions TEXT, seal TEXT
        )""")
        c.execute("CREATE TABLE IF NOT EXISTS seal_ledger (entry_id TEXT, seal TEXT, timestamp REAL)")
        self.conn.commit()

    @staticmethod
    def _seal(data: str) -> str:
        return hashlib.sha3_512(data.encode()).hexdigest()

    def store_artifact(self, artifact: CodeArtifact) -> bool:
        try:
            c = self.conn.cursor()
            c.execute("""INSERT INTO artifacts VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (
                artifact.artifact_id, artifact.operation, artifact.language,
                artifact.specification, artifact.solution_code, artifact.mu_score,
                json.dumps(artifact.domain_scores), artifact.strategy,
                artifact.lines, artifact.seal, artifact.created_at
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[MERLIN] Artifact store error: {e}")
            return False

    def store_report(self, report: AfterActionReport) -> bool:
        try:
            c = self.conn.cursor()
            c.execute("""INSERT INTO after_action_reports VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (
                report.report_id, report.operation, report.artifact_id,
                report.start_time, report.end_time,
                json.dumps(report.domain_scores), report.mu_score,
                report.technical_summary, report.resonant_narrative,
                json.dumps(report.suggestions), report.seal
            ))
            c.execute("INSERT INTO seal_ledger VALUES (?,?,?)",
                (report.report_id, report.seal, time.time()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[MERLIN] Report store error: {e}")
            return False

    def get_artifact(self, artifact_id: str) -> Optional[CodeArtifact]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,))
        row = c.fetchone()
        if not row:
            return None
        return CodeArtifact(
            artifact_id=row["artifact_id"], operation=row["operation"],
            language=row["language"], specification=row["specification"],
            solution_code=row["solution_code"], mu_score=row["mu_score"],
            domain_scores=json.loads(row["domain_scores"]),
            strategy=row["strategy"], lines=row["lines"],
            seal=row["seal"], created_at=row["created_at"]
        )

    def get_reports_for_artifact(self, artifact_id: str) -> List[AfterActionReport]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM after_action_reports WHERE artifact_id = ? ORDER BY end_time DESC", (artifact_id,))
        reports = []
        for row in c.fetchall():
            reports.append(AfterActionReport(
                report_id=row["report_id"], operation=row["operation"],
                artifact_id=row["artifact_id"], start_time=row["start_time"],
                end_time=row["end_time"], domain_scores=json.loads(row["domain_scores"]),
                mu_score=row["mu_score"], technical_summary=row["technical_summary"],
                resonant_narrative=row["resonant_narrative"],
                suggestions=json.loads(row["suggestions"]), seal=row["seal"]
            ))
        return reports

    def list_artifacts(self, limit: int = 50) -> List[CodeArtifact]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM artifacts ORDER BY created_at DESC LIMIT ?", (limit,))
        artifacts = []
        for row in c.fetchall():
            artifacts.append(CodeArtifact(
                artifact_id=row["artifact_id"], operation=row["operation"],
                language=row["language"], specification=row["specification"],
                solution_code=row["solution_code"], mu_score=row["mu_score"],
                domain_scores=json.loads(row["domain_scores"]),
                strategy=row["strategy"], lines=row["lines"],
                seal=row["seal"], created_at=row["created_at"]
            ))
        return artifacts
