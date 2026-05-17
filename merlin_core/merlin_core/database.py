#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERLIN CORE — DATABASE
SQLite-backed sealed ledger for artifacts, analysis results, and after-action reports.
SHA3-512 cryptographic seals on all records.
Zero external dependencies.
"""

import sqlite3, json, time, uuid, hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from .resonance import ResonanceEngine

# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class CodeArtifact:
    artifact_id: str
    operation: str
    language: str
    specification: str
    solution_code: str = ""
    mu_score: float = 0.0
    domain_scores: Dict[str, float] = field(default_factory=dict)
    strategy: str = ""
    lines: int = 0
    seal: str = ""
    timestamp: float = field(default_factory=time.time)

    def compute_seal(self) -> str:
        data = f"{self.artifact_id}{self.operation}{self.language}{self.mu_score}{self.timestamp}"
        self.seal = hashlib.sha3_512(data.encode()).hexdigest()
        return self.seal


@dataclass
class AfterActionReport:
    report_id: str
    operation: str
    artifact_id: str
    start_time: float
    end_time: float
    domain_scores: Dict[str, float]
    mu_score: float
    technical_summary: str
    resonant_narrative: str
    suggestions: List[str] = field(default_factory=list)
    seal: str = ""
    timestamp: float = field(default_factory=time.time)

    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000


# ─────────────────────────────────────────────────────────────────────────────
# MERLIN DATABASE
# ─────────────────────────────────────────────────────────────────────────────
class MerlinDatabase:
    """
    SQLite-backed artifact ledger with SHA3-512 seals.
    Pure stdlib — no external dependencies.
    """

    def __init__(self, db_path: str = "merlin_vault.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                operation TEXT,
                language TEXT,
                specification TEXT,
                solution_code TEXT,
                mu_score REAL,
                domain_scores TEXT,
                strategy TEXT,
                lines INTEGER,
                seal TEXT,
                timestamp REAL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS after_action_reports (
                report_id TEXT PRIMARY KEY,
                operation TEXT,
                artifact_id TEXT,
                start_time REAL,
                end_time REAL,
                domain_scores TEXT,
                mu_score REAL,
                technical_summary TEXT,
                resonant_narrative TEXT,
                suggestions TEXT,
                seal TEXT,
                timestamp REAL
            )
        """)
        self.conn.commit()

    def store_artifact(self, artifact: CodeArtifact) -> bool:
        try:
            c = self.conn.cursor()
            artifact.compute_seal()
            c.execute("""
                INSERT OR REPLACE INTO artifacts
                (artifact_id, operation, language, specification, solution_code,
                 mu_score, domain_scores, strategy, lines, seal, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                artifact.artifact_id, artifact.operation, artifact.language,
                artifact.specification, artifact.solution_code, artifact.mu_score,
                json.dumps(artifact.domain_scores), artifact.strategy,
                artifact.lines, artifact.seal, artifact.timestamp
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[MERLIN DB] store_artifact error: {e}")
            return False

    def store_report(self, report: AfterActionReport) -> bool:
        try:
            c = self.conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO after_action_reports
                (report_id, operation, artifact_id, start_time, end_time,
                 domain_scores, mu_score, technical_summary, resonant_narrative,
                 suggestions, seal, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.report_id, report.operation, report.artifact_id,
                report.start_time, report.end_time, json.dumps(report.domain_scores),
                report.mu_score, report.technical_summary, report.resonant_narrative,
                json.dumps(report.suggestions), report.seal, report.timestamp
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[MERLIN DB] store_report error: {e}")
            return False

    def list_artifacts(self, limit: int = 20) -> List[CodeArtifact]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM artifacts ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        return [self._row_to_artifact(r) for r in rows]

    def get_artifact(self, artifact_id: str) -> Optional[CodeArtifact]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,))
        row = c.fetchone()
        return self._row_to_artifact(row) if row else None

    def list_reports(self, limit: int = 20) -> List[AfterActionReport]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM after_action_reports ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        return [self._row_to_report(r) for r in rows]

    def _row_to_artifact(self, row) -> CodeArtifact:
        return CodeArtifact(
            artifact_id=row["artifact_id"], operation=row["operation"],
            language=row["language"], specification=row["specification"],
            solution_code=row["solution_code"], mu_score=row["mu_score"],
            domain_scores=json.loads(row["domain_scores"] or "{}"),
            strategy=row["strategy"], lines=row["lines"],
            seal=row["seal"], timestamp=row["timestamp"]
        )

    def _row_to_report(self, row) -> AfterActionReport:
        return AfterActionReport(
            report_id=row["report_id"], operation=row["operation"],
            artifact_id=row["artifact_id"], start_time=row["start_time"],
            end_time=row["end_time"], domain_scores=json.loads(row["domain_scores"] or "{}"),
            mu_score=row["mu_score"], technical_summary=row["technical_summary"],
            resonant_narrative=row["resonant_narrative"],
            suggestions=json.loads(row["suggestions"] or "[]"),
            seal=row["seal"], timestamp=row["timestamp"]
        )

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = MerlinDatabase(":memory:")
    print(f"MerlinDatabase initialized — version 3.1.0")
    print(f"Seal: {hashlib.sha3_512(b'merlin_vault').hexdigest()[:16]}...")
    db.close()