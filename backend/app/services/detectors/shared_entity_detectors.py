"""
Deterministic detectors for shared entities (Payment Instruments, Devices, and IPs).
"""

from typing import List, Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entity import Entity, EntityType
from app.models.transaction_entity import TransactionEntity
from app.models.transaction import Transaction
from app.models.finding import FindingType, FindingSeverity
from app.schemas.analysis import AnalysisConfig
from app.services.detectors.base import BaseDetector, CandidateFinding


class SharedPaymentInstrumentDetector(BaseDetector):
    """
    Detects payment instruments linked to multiple distinct customer accounts.
    """
    async def detect(
        self,
        db: AsyncSession,
        config: AnalysisConfig,
    ) -> List[CandidateFinding]:
        threshold = config.shared_instrument_threshold
        findings: List[CandidateFinding] = []

        stmt = (
            select(Entity)
            .where(Entity.entity_type == EntityType.PAYMENT_INSTRUMENT)
            .options(
                selectinload(Entity.transaction_links)
                .selectinload(TransactionEntity.transaction)
            )
        )
        entities = (await db.execute(stmt)).scalars().all()

        for entity in entities:
            # Gather all transactions linked to this instrument
            transactions = [
                link.transaction
                for link in entity.transaction_links
                if link.transaction is not None
            ]
            if not transactions:
                continue

            customer_ids: Set[str] = {tx.customer_id for tx in transactions}
            if len(customer_ids) >= threshold:
                # Find user entity IDs for the customer_ids
                user_stmt = select(Entity).where(
                    Entity.entity_type == EntityType.USER,
                    Entity.entity_value.in_(customer_ids),
                )
                user_entities = (await db.execute(user_stmt)).scalars().all()

                sorted_custs = sorted(list(customer_ids))
                sorted_txs = sorted(transactions, key=lambda x: x.transacted_at)
                first_seen = sorted_txs[0].transacted_at.isoformat()
                last_seen = sorted_txs[-1].transacted_at.isoformat()

                severity = (
                    FindingSeverity.HIGH
                    if len(customer_ids) >= 3
                    else FindingSeverity.MEDIUM
                )
                title = f"Shared Payment Instrument across {len(customer_ids)} Accounts"
                explanation = (
                    f"Payment instrument '{entity.entity_value}' was used in transactions across "
                    f"{len(customer_ids)} distinct customer accounts ({', '.join(sorted_custs)})."
                )
                evidence = {
                    "instrument_reference": entity.entity_value,
                    "customer_count": len(customer_ids),
                    "customer_ids": sorted_custs,
                    "transaction_count": len(sorted_txs),
                    "transaction_ids": [tx.transaction_id for tx in sorted_txs],
                    "first_seen": first_seen,
                    "last_seen": last_seen,
                }

                related_entities = [(entity.id, "PRIMARY_SHARED_ENTITY")]
                for ue in user_entities:
                    related_entities.append((ue.id, "ASSOCIATED_ACCOUNT"))

                candidate = CandidateFinding(
                    finding_type=FindingType.SHARED_PAYMENT_INSTRUMENT,
                    severity=severity,
                    title=title,
                    explanation=explanation,
                    evidence_payload=evidence,
                    related_entities=related_entities,
                    related_transaction_ids=[tx.id for tx in sorted_txs],
                )
                findings.append(candidate)

        return findings


class SharedDeviceDetector(BaseDetector):
    """
    Detects device fingerprints shared across multiple distinct customer accounts.
    """
    async def detect(
        self,
        db: AsyncSession,
        config: AnalysisConfig,
    ) -> List[CandidateFinding]:
        threshold = config.shared_device_threshold
        findings: List[CandidateFinding] = []

        stmt = (
            select(Entity)
            .where(Entity.entity_type == EntityType.DEVICE)
            .options(
                selectinload(Entity.transaction_links)
                .selectinload(TransactionEntity.transaction)
            )
        )
        entities = (await db.execute(stmt)).scalars().all()

        for entity in entities:
            transactions = [
                link.transaction
                for link in entity.transaction_links
                if link.transaction is not None
            ]
            if not transactions:
                continue

            customer_ids: Set[str] = {tx.customer_id for tx in transactions}
            if len(customer_ids) >= threshold:
                user_stmt = select(Entity).where(
                    Entity.entity_type == EntityType.USER,
                    Entity.entity_value.in_(customer_ids),
                )
                user_entities = (await db.execute(user_stmt)).scalars().all()

                sorted_custs = sorted(list(customer_ids))
                sorted_txs = sorted(transactions, key=lambda x: x.transacted_at)
                first_seen = sorted_txs[0].transacted_at.isoformat()
                last_seen = sorted_txs[-1].transacted_at.isoformat()

                severity = (
                    FindingSeverity.HIGH
                    if len(customer_ids) >= 3
                    else FindingSeverity.MEDIUM
                )
                title = f"Shared Device Fingerprint across {len(customer_ids)} Accounts"
                explanation = (
                    f"Device fingerprint '{entity.entity_value}' was used across "
                    f"{len(customer_ids)} distinct customer accounts ({', '.join(sorted_custs)})."
                )
                evidence = {
                    "device_id": entity.entity_value,
                    "customer_count": len(customer_ids),
                    "customer_ids": sorted_custs,
                    "transaction_count": len(sorted_txs),
                    "transaction_ids": [tx.transaction_id for tx in sorted_txs],
                    "first_seen": first_seen,
                    "last_seen": last_seen,
                }

                related_entities = [(entity.id, "PRIMARY_SHARED_ENTITY")]
                for ue in user_entities:
                    related_entities.append((ue.id, "ASSOCIATED_ACCOUNT"))

                candidate = CandidateFinding(
                    finding_type=FindingType.SHARED_DEVICE,
                    severity=severity,
                    title=title,
                    explanation=explanation,
                    evidence_payload=evidence,
                    related_entities=related_entities,
                    related_transaction_ids=[tx.id for tx in sorted_txs],
                )
                findings.append(candidate)

        return findings


class SharedIPClusterDetector(BaseDetector):
    """
    Detects IP addresses originating transactions from multiple distinct customer accounts.
    """
    async def detect(
        self,
        db: AsyncSession,
        config: AnalysisConfig,
    ) -> List[CandidateFinding]:
        threshold = config.shared_ip_threshold
        findings: List[CandidateFinding] = []

        stmt = (
            select(Entity)
            .where(Entity.entity_type == EntityType.IP)
            .options(
                selectinload(Entity.transaction_links)
                .selectinload(TransactionEntity.transaction)
            )
        )
        entities = (await db.execute(stmt)).scalars().all()

        for entity in entities:
            transactions = [
                link.transaction
                for link in entity.transaction_links
                if link.transaction is not None
            ]
            if not transactions:
                continue

            customer_ids: Set[str] = {tx.customer_id for tx in transactions}
            if len(customer_ids) >= threshold:
                user_stmt = select(Entity).where(
                    Entity.entity_type == EntityType.USER,
                    Entity.entity_value.in_(customer_ids),
                )
                user_entities = (await db.execute(user_stmt)).scalars().all()

                sorted_custs = sorted(list(customer_ids))
                sorted_txs = sorted(transactions, key=lambda x: x.transacted_at)
                first_seen = sorted_txs[0].transacted_at.isoformat()
                last_seen = sorted_txs[-1].transacted_at.isoformat()

                severity = (
                    FindingSeverity.HIGH
                    if len(customer_ids) >= 5
                    else FindingSeverity.MEDIUM
                )
                title = f"Shared IP Cluster across {len(customer_ids)} Accounts"
                explanation = (
                    f"IP address '{entity.entity_value}' originated transactions across "
                    f"{len(customer_ids)} distinct customer accounts ({', '.join(sorted_custs)})."
                )
                evidence = {
                    "ip_address": entity.entity_value,
                    "customer_count": len(customer_ids),
                    "customer_ids": sorted_custs,
                    "transaction_count": len(sorted_txs),
                    "transaction_ids": [tx.transaction_id for tx in sorted_txs],
                    "first_seen": first_seen,
                    "last_seen": last_seen,
                }

                related_entities = [(entity.id, "PRIMARY_SHARED_ENTITY")]
                for ue in user_entities:
                    related_entities.append((ue.id, "ASSOCIATED_ACCOUNT"))

                candidate = CandidateFinding(
                    finding_type=FindingType.SHARED_IP_CLUSTER,
                    severity=severity,
                    title=title,
                    explanation=explanation,
                    evidence_payload=evidence,
                    related_entities=related_entities,
                    related_transaction_ids=[tx.id for tx in sorted_txs],
                )
                findings.append(candidate)

        return findings
