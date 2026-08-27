"""
Service for orchestrating deterministic graph/pattern analysis, deduplication, and persistence.
"""

from datetime import datetime, timezone
import hashlib
from typing import List, Optional, Set, Tuple
from uuid import uuid4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analysis_run import AnalysisRun, AnalysisRunStatus
from app.models.finding import Finding
from app.models.finding_entity import FindingEntity
from app.models.finding_transaction import FindingTransaction
from app.models.transaction import Transaction
from app.schemas.analysis import AnalysisConfig
from app.services.detectors import ALL_DETECTORS, CandidateFinding


class AnalysisService:
    @classmethod
    async def run_analysis(
        cls,
        db: AsyncSession,
        config: Optional[AnalysisConfig] = None,
    ) -> AnalysisRun:
        """
        Execute deterministic pattern/graph analysis across all persisted transactions and entities.
        Deduplicates candidate findings by deterministic content fingerprint.
        """
        active_config = config or AnalysisConfig()
        config_hash = hashlib.sha256(
            active_config.model_dump_json().encode("utf-8")
        ).hexdigest()

        # Count total transactions in database
        total_txs = (
            await db.execute(select(func.count()).select_from(Transaction))
        ).scalar() or 0

        # Create AnalysisRun record
        run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
        analysis_run = AnalysisRun(
            run_id=run_id,
            status=AnalysisRunStatus.RUNNING,
            total_transactions_analyzed=total_txs,
            findings_count=0,
            config_hash=config_hash,
        )
        db.add(analysis_run)
        await db.flush()

        # Execute all active detectors
        all_candidates: List[CandidateFinding] = []
        for detector_cls in ALL_DETECTORS:
            detector = detector_cls()
            candidates = await detector.detect(db=db, config=active_config)
            all_candidates.extend(candidates)

        # Deduplicate candidate findings by deterministic fingerprint
        seen_fingerprints: Set[str] = set()
        persisted_findings_count = 0

        for candidate in all_candidates:
            fp = candidate.compute_fingerprint()
            if fp in seen_fingerprints:
                continue
            seen_fingerprints.add(fp)

            finding_id = f"find_{uuid4().hex[:10]}"
            finding = Finding(
                finding_id=finding_id,
                analysis_run_id=analysis_run.id,
                finding_type=candidate.finding_type,
                severity=candidate.severity,
                title=candidate.title,
                explanation=candidate.explanation,
                fingerprint=fp,
                evidence_payload=candidate.evidence_payload,
            )
            db.add(finding)
            await db.flush()

            # Attach entity links
            for entity_id, role in candidate.related_entities:
                fe = FindingEntity(
                    finding_id=finding.id,
                    entity_id=entity_id,
                    role=role,
                )
                db.add(fe)

            # Attach transaction links
            for tx_id in candidate.related_transaction_ids:
                ft = FindingTransaction(
                    finding_id=finding.id,
                    transaction_id=tx_id,
                )
                db.add(ft)

            persisted_findings_count += 1

        # Mark analysis run complete
        analysis_run.findings_count = persisted_findings_count
        analysis_run.status = AnalysisRunStatus.COMPLETED
        analysis_run.completed_at = datetime.now(timezone.utc)
        await db.flush()

        # Return full reloaded run
        return await cls.get_analysis_run_by_id(db=db, run_id=analysis_run.run_id)  # type: ignore

    @classmethod
    async def get_analysis_runs(
        cls,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[AnalysisRun], int]:
        """
        Retrieve paginated list of analysis execution runs.
        """
        count_stmt = select(func.count()).select_from(AnalysisRun)
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(AnalysisRun)
            .order_by(AnalysisRun.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        runs = list((await db.execute(stmt)).scalars().all())
        return runs, total

    @classmethod
    async def get_analysis_run_by_id(
        cls,
        db: AsyncSession,
        run_id: str,
    ) -> Optional[AnalysisRun]:
        """
        Retrieve an analysis run with all associated findings and entity links.
        """
        stmt = (
            select(AnalysisRun)
            .options(
                selectinload(AnalysisRun.findings)
                .selectinload(Finding.related_entities)
                .selectinload(FindingEntity.entity),
                selectinload(AnalysisRun.findings)
                .selectinload(Finding.related_transactions)
                .selectinload(FindingTransaction.transaction),
            )
            .where(AnalysisRun.run_id == run_id)
        )
        return (await db.execute(stmt)).scalars().first()

    @classmethod
    async def get_findings(
        cls,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        finding_type: Optional[str] = None,
        severity: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> Tuple[List[Finding], int]:
        """
        Retrieve paginated list of findings with optional filters.
        """
        filters = []
        if finding_type:
            filters.append(Finding.finding_type == finding_type)
        if severity:
            filters.append(Finding.severity == severity)
        if run_id:
            subq = select(AnalysisRun.id).where(AnalysisRun.run_id == run_id)
            filters.append(Finding.analysis_run_id.in_(subq))

        count_stmt = select(func.count()).select_from(Finding)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Finding)
            .options(
                selectinload(Finding.related_entities).selectinload(FindingEntity.entity),
                selectinload(Finding.related_transactions).selectinload(FindingTransaction.transaction),
            )
            .order_by(Finding.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if filters:
            stmt = stmt.where(*filters)

        items = list((await db.execute(stmt)).scalars().all())
        return items, total

    @classmethod
    async def get_finding_by_id(
        cls,
        db: AsyncSession,
        finding_id: str,
    ) -> Optional[Finding]:
        """
        Retrieve a single finding by finding_id with full evidence and linkages.
        """
        stmt = (
            select(Finding)
            .options(
                selectinload(Finding.related_entities).selectinload(FindingEntity.entity),
                selectinload(Finding.related_transactions).selectinload(FindingTransaction.transaction),
            )
            .where(Finding.finding_id == finding_id)
        )
        return (await db.execute(stmt)).scalars().first()
