"""
Deterministic detectors for temporal velocity bursts and rapid failure sequences.
"""

from datetime import timedelta
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entity import Entity, EntityType
from app.models.transaction_entity import TransactionEntity
from app.models.transaction import Transaction
from app.models.finding import FindingType, FindingSeverity
from app.schemas.analysis import AnalysisConfig
from app.services.detectors.base import BaseDetector, CandidateFinding


class VelocityBurstDetector(BaseDetector):
    """
    Detects high transaction velocity bursts within a sliding time window for an entity.
    """
    async def detect(
        self,
        db: AsyncSession,
        config: AnalysisConfig,
    ) -> List[CandidateFinding]:
        burst_count = config.velocity_burst_count
        window_duration = timedelta(minutes=config.velocity_window_minutes)
        findings: List[CandidateFinding] = []

        stmt = (
            select(Entity)
            .where(Entity.entity_type.in_([EntityType.USER, EntityType.DEVICE, EntityType.IP]))
            .options(
                selectinload(Entity.transaction_links)
                .selectinload(TransactionEntity.transaction)
            )
        )
        entities = (await db.execute(stmt)).scalars().all()

        for entity in entities:
            transactions: List[Transaction] = [
                link.transaction
                for link in entity.transaction_links
                if link.transaction is not None
            ]
            if len(transactions) < burst_count:
                continue

            sorted_txs = sorted(transactions, key=lambda x: x.transacted_at)
            
            # Sliding window search
            i = 0
            while i < len(sorted_txs):
                window_txs = [sorted_txs[i]]
                j = i + 1
                while j < len(sorted_txs):
                    if sorted_txs[j].transacted_at - sorted_txs[i].transacted_at <= window_duration:
                        window_txs.append(sorted_txs[j])
                        j += 1
                    else:
                        break

                if len(window_txs) >= burst_count:
                    first_time = window_txs[0].transacted_at
                    last_time = window_txs[-1].transacted_at
                    span_seconds = int((last_time - first_time).total_seconds())

                    severity = (
                        FindingSeverity.HIGH
                        if len(window_txs) >= 5
                        else FindingSeverity.MEDIUM
                    )
                    title = (
                        f"Velocity Burst on {entity.entity_type}: "
                        f"{len(window_txs)} Transactions in {config.velocity_window_minutes}m"
                    )
                    explanation = (
                        f"{entity.entity_type} '{entity.entity_value}' executed "
                        f"{len(window_txs)} transactions within a span of {span_seconds} seconds "
                        f"(threshold: {burst_count} within {config.velocity_window_minutes}m)."
                    )
                    evidence = {
                        "entity_type": entity.entity_type,
                        "entity_value": entity.entity_value,
                        "transaction_count": len(window_txs),
                        "window_minutes": config.velocity_window_minutes,
                        "actual_span_seconds": span_seconds,
                        "first_transaction_time": first_time.isoformat(),
                        "last_transaction_time": last_time.isoformat(),
                        "transaction_ids": [tx.transaction_id for tx in window_txs],
                    }

                    candidate = CandidateFinding(
                        finding_type=FindingType.VELOCITY_BURST,
                        severity=severity,
                        title=title,
                        explanation=explanation,
                        evidence_payload=evidence,
                        related_entities=[(entity.id, "PRIMARY_BURST_ENTITY")],
                        related_transaction_ids=[tx.id for tx in window_txs],
                    )
                    findings.append(candidate)
                    # Advance i to j to avoid duplicate overlapping sub-windows
                    i = j
                else:
                    i += 1

        return findings


class RapidFailureBurstDetector(BaseDetector):
    """
    Detects repeated rapid payment failures within a sliding time window for an entity.
    """
    async def detect(
        self,
        db: AsyncSession,
        config: AnalysisConfig,
    ) -> List[CandidateFinding]:
        burst_count = config.failure_burst_count
        window_duration = timedelta(minutes=config.failure_window_minutes)
        findings: List[CandidateFinding] = []

        stmt = (
            select(Entity)
            .where(Entity.entity_type.in_([EntityType.USER, EntityType.DEVICE, EntityType.PAYMENT_INSTRUMENT]))
            .options(
                selectinload(Entity.transaction_links)
                .selectinload(TransactionEntity.transaction)
            )
        )
        entities = (await db.execute(stmt)).scalars().all()

        for entity in entities:
            failed_transactions: List[Transaction] = [
                link.transaction
                for link in entity.transaction_links
                if link.transaction is not None and link.transaction.status.upper() == "FAILED"
            ]
            if len(failed_transactions) < burst_count:
                continue

            sorted_txs = sorted(failed_transactions, key=lambda x: x.transacted_at)
            
            # Sliding window search
            i = 0
            while i < len(sorted_txs):
                window_txs = [sorted_txs[i]]
                j = i + 1
                while j < len(sorted_txs):
                    if sorted_txs[j].transacted_at - sorted_txs[i].transacted_at <= window_duration:
                        window_txs.append(sorted_txs[j])
                        j += 1
                    else:
                        break

                if len(window_txs) >= burst_count:
                    first_time = window_txs[0].transacted_at
                    last_time = window_txs[-1].transacted_at
                    span_seconds = int((last_time - first_time).total_seconds())

                    severity = (
                        FindingSeverity.HIGH
                        if len(window_txs) >= 4
                        else FindingSeverity.MEDIUM
                    )
                    title = (
                        f"Rapid Failure Burst on {entity.entity_type}: "
                        f"{len(window_txs)} Failures in {config.failure_window_minutes}m"
                    )
                    explanation = (
                        f"{entity.entity_type} '{entity.entity_value}' incurred "
                        f"{len(window_txs)} failed transactions within {span_seconds} seconds "
                        f"(threshold: {burst_count} in {config.failure_window_minutes}m)."
                    )
                    evidence = {
                        "entity_type": entity.entity_type,
                        "entity_value": entity.entity_value,
                        "failed_transaction_count": len(window_txs),
                        "window_minutes": config.failure_window_minutes,
                        "actual_span_seconds": span_seconds,
                        "first_failure_time": first_time.isoformat(),
                        "last_failure_time": last_time.isoformat(),
                        "failed_transaction_ids": [tx.transaction_id for tx in window_txs],
                    }

                    candidate = CandidateFinding(
                        finding_type=FindingType.RAPID_FAILURE_BURST,
                        severity=severity,
                        title=title,
                        explanation=explanation,
                        evidence_payload=evidence,
                        related_entities=[(entity.id, "PRIMARY_BURST_ENTITY")],
                        related_transaction_ids=[tx.id for tx in window_txs],
                    )
                    findings.append(candidate)
                    i = j
                else:
                    i += 1

        return findings
