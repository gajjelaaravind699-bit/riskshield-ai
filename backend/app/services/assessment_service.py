"""
Service for deterministic, explainable risk scoring and decision-support assessment.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment import Assessment, RiskLevel, Recommendation
from app.models.finding import Finding, FindingType
from app.models.finding_entity import FindingEntity
from app.models.finding_transaction import FindingTransaction
from app.models.transaction import Transaction
from app.models.transaction_entity import TransactionEntity
from app.schemas.assessment import (
    RulesetConfig,
    DecisionPolicyConfig,
    AssessmentBatchResponse,
    AssessmentRead,
)


class AssessmentService:
    @classmethod
    async def evaluate_transaction(
        cls,
        db: AsyncSession,
        transaction_lookup: int | str,
        ruleset: Optional[RulesetConfig] = None,
        policy: Optional[DecisionPolicyConfig] = None,
    ) -> Assessment:
        """
        Evaluate a single transaction against persisted findings using a versioned ruleset and decision policy.
        Produces deterministic, bounded risk scores and explainable advisory recommendations (ALLOW / REVIEW / BLOCK).
        NEVER modifies underlying transaction status or executes automated financial actions.
        """
        active_ruleset = ruleset or RulesetConfig()
        active_policy = policy or DecisionPolicyConfig()

        # 1. Fetch transaction with entity relationships
        stmt = select(Transaction).options(
            selectinload(Transaction.entities).selectinload(TransactionEntity.entity)
        )
        if isinstance(transaction_lookup, int):
            stmt = stmt.where(Transaction.id == transaction_lookup)
        else:
            stmt = stmt.where(Transaction.transaction_id == str(transaction_lookup))

        tx = (await db.execute(stmt)).scalars().first()
        if not tx:
            raise ValueError(f"Transaction '{transaction_lookup}' not found.")

        # 2. Collect all findings associated with this transaction directly or through its linked entities
        entity_ids = [te.entity_id for te in tx.entities]

        # Findings linked directly to transaction
        direct_stmt = (
            select(Finding)
            .join(FindingTransaction, FindingTransaction.finding_id == Finding.id)
            .where(FindingTransaction.transaction_id == tx.id)
        )
        direct_findings = list((await db.execute(direct_stmt)).scalars().all())

        # Findings linked through participating entities
        entity_findings: List[Finding] = []
        if entity_ids:
            entity_stmt = (
                select(Finding)
                .join(FindingEntity, FindingEntity.finding_id == Finding.id)
                .where(FindingEntity.entity_id.in_(entity_ids))
            )
            entity_findings = list((await db.execute(entity_stmt)).scalars().all())

        # Deduplicate all related findings by ID
        finding_map: Dict[int, Finding] = {}
        for f in direct_findings + entity_findings:
            finding_map[f.id] = f
        related_findings = list(finding_map.values())

        # Group findings by type
        findings_by_type: Dict[str, List[Finding]] = {}
        for f in related_findings:
            findings_by_type.setdefault(f.finding_type, []).append(f)

        # 3. Deterministically evaluate active rules
        rule_contributions: List[Dict[str, Any]] = []
        total_points = active_ruleset.base_score

        # Rule Definitions
        rule_specs = [
            {
                "rule_name": "Shared Payment Instrument Anomaly",
                "finding_type": FindingType.SHARED_PAYMENT_INSTRUMENT,
                "weight": active_ruleset.shared_instrument_weight,
                "description": "Payment instrument token / VPA / card hash shared across distinct customer accounts.",
            },
            {
                "rule_name": "Shared Device Fingerprint Anomaly",
                "finding_type": FindingType.SHARED_DEVICE,
                "weight": active_ruleset.shared_device_weight,
                "description": "Hardware device fingerprint shared across distinct customer accounts.",
            },
            {
                "rule_name": "Shared IP Subnet/Cluster Anomaly",
                "finding_type": FindingType.SHARED_IP_CLUSTER,
                "weight": active_ruleset.shared_ip_weight,
                "description": "IP address cluster originating transactions across multiple accounts.",
            },
            {
                "rule_name": "Entity Velocity Burst Anomaly",
                "finding_type": FindingType.VELOCITY_BURST,
                "weight": active_ruleset.velocity_burst_weight,
                "description": "High transaction frequency burst on associated entity within sliding window.",
            },
            {
                "rule_name": "Rapid Failure Sequence Anomaly",
                "finding_type": FindingType.RAPID_FAILURE_BURST,
                "weight": active_ruleset.failure_burst_weight,
                "description": "Repeated authorization failure sequence on associated entity within sliding window.",
            },
        ]

        triggered_rule_summaries: List[str] = []

        for spec in rule_specs:
            ftype = spec["finding_type"]
            matched_findings = findings_by_type.get(ftype, [])
            is_triggered = len(matched_findings) > 0
            points = spec["weight"] if is_triggered else 0
            total_points += points

            finding_ids = [f.finding_id for f in matched_findings]
            rule_contributions.append({
                "rule_name": spec["rule_name"],
                "finding_type": ftype,
                "weight": spec["weight"],
                "triggered": is_triggered,
                "points_contributed": points,
                "description": spec["description"],
                "finding_ids": finding_ids,
            })

            if is_triggered:
                triggered_rule_summaries.append(f"{spec['rule_name']} (+{points} pts)")

        # 4. Compute bounded score [0, max_score]
        bounded_score = min(max(total_points, 0), active_ruleset.max_score)

        # 5. Map to Risk Level
        if bounded_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif bounded_score >= 60:
            risk_level = RiskLevel.HIGH
        elif bounded_score >= active_policy.review_threshold:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # 6. Map to Decision-Support Recommendation
        if bounded_score >= active_policy.block_threshold:
            recommendation = Recommendation.BLOCK
        elif bounded_score >= active_policy.review_threshold:
            recommendation = Recommendation.REVIEW
        else:
            recommendation = Recommendation.ALLOW

        # 7. Formulate Human-Readable Explanation
        if recommendation == Recommendation.BLOCK:
            explanation = (
                f"Risk Score: {bounded_score}/{active_ruleset.max_score} ({risk_level}). "
                f"Advisory Recommendation: BLOCK. Triggered {len(triggered_rule_summaries)} abuse patterns: "
                f"{', '.join(triggered_rule_summaries)}. "
                "Coordinated abuse ring indicators exceed high-risk threshold. "
                "Decision-support advisory recommendation only — no automated financial block was executed."
            )
        elif recommendation == Recommendation.REVIEW:
            explanation = (
                f"Risk Score: {bounded_score}/{active_ruleset.max_score} ({risk_level}). "
                f"Advisory Recommendation: REVIEW. Triggered {len(triggered_rule_summaries)} patterns: "
                f"{', '.join(triggered_rule_summaries)}. "
                "Borderline anomaly signals detected warranting manual compliance review."
            )
        else:
            explanation = (
                f"Risk Score: {bounded_score}/{active_ruleset.max_score} ({risk_level}). "
                "Advisory Recommendation: ALLOW. No suspicious entity sharing, velocity bursts, or failure clusters detected. "
                "Transaction signals operate within normal baseline parameters."
            )

        evidence_summary = {
            "total_related_findings": len(related_findings),
            "triggered_rules_count": len(triggered_rule_summaries),
            "finding_ids": [f.finding_id for f in related_findings],
            "customer_id": tx.customer_id,
            "amount": str(tx.amount),
            "currency": tx.currency,
            "payment_method": tx.payment_method,
            "transacted_at": tx.transacted_at.isoformat(),
        }

        action_disclaimer = (
            "Decision-support recommendation only. RiskShield AI is an advisory sentinel "
            "and does not execute autonomous transaction blocks or financial interventions."
        )

        # 8. Check for existing assessment to update or create new
        asmt_stmt = select(Assessment).where(
            Assessment.transaction_id == tx.id,
            Assessment.ruleset_version == active_ruleset.ruleset_version,
            Assessment.decision_policy_version == active_policy.decision_policy_version,
        )
        existing_asmt = (await db.execute(asmt_stmt)).scalars().first()

        if existing_asmt:
            existing_asmt.score = bounded_score
            existing_asmt.risk_level = risk_level
            existing_asmt.recommendation = recommendation
            existing_asmt.explanation = explanation
            existing_asmt.rule_contributions = rule_contributions
            existing_asmt.evidence_summary = evidence_summary
            existing_asmt.action_executed = False
            existing_asmt.action_disclaimer = action_disclaimer
            existing_asmt.created_at = datetime.now(timezone.utc)
            assessment = existing_asmt
        else:
            assessment_id = f"asmt_{uuid4().hex[:10]}"
            assessment = Assessment(
                assessment_id=assessment_id,
                transaction_id=tx.id,
                score=bounded_score,
                risk_level=risk_level,
                recommendation=recommendation,
                explanation=explanation,
                ruleset_version=active_ruleset.ruleset_version,
                decision_policy_version=active_policy.decision_policy_version,
                rule_contributions=rule_contributions,
                evidence_summary=evidence_summary,
                action_executed=False,
                action_disclaimer=action_disclaimer,
            )
            db.add(assessment)

        await db.flush()
        return assessment

    @classmethod
    async def evaluate_all_transactions(
        cls,
        db: AsyncSession,
        ruleset: Optional[RulesetConfig] = None,
        policy: Optional[DecisionPolicyConfig] = None,
    ) -> AssessmentBatchResponse:
        """
        Evaluate all persisted transactions against the current ruleset and decision policy.
        """
        active_ruleset = ruleset or RulesetConfig()
        active_policy = policy or DecisionPolicyConfig()

        txs_stmt = select(Transaction.id).order_by(Transaction.transacted_at.desc())
        tx_ids = list((await db.execute(txs_stmt)).scalars().all())

        assessments: List[Assessment] = []
        allow_count = 0
        review_count = 0
        block_count = 0

        for tx_id in tx_ids:
            asmt = await cls.evaluate_transaction(
                db=db,
                transaction_lookup=tx_id,
                ruleset=active_ruleset,
                policy=active_policy,
            )
            assessments.append(asmt)
            if asmt.recommendation == Recommendation.ALLOW:
                allow_count += 1
            elif asmt.recommendation == Recommendation.REVIEW:
                review_count += 1
            elif asmt.recommendation == Recommendation.BLOCK:
                block_count += 1

        # Reload assessments with transaction relationships for response
        reloaded_assessments: List[AssessmentRead] = []
        for asmt in assessments:
            reloaded = await cls.get_assessment_by_id(db=db, assessment_id=asmt.assessment_id)
            if reloaded:
                reloaded_assessments.append(AssessmentRead.model_validate(reloaded))

        return AssessmentBatchResponse(
            total_evaluated=len(assessments),
            allow_count=allow_count,
            review_count=review_count,
            block_count=block_count,
            ruleset_version=active_ruleset.ruleset_version,
            decision_policy_version=active_policy.decision_policy_version,
            action_disclaimer=(
                "Decision-support recommendation only. RiskShield AI is an advisory sentinel "
                "and does not execute autonomous transaction blocks or financial interventions."
            ),
            items=reloaded_assessments,
        )

    @classmethod
    async def get_assessments(
        cls,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        recommendation: Optional[str] = None,
        risk_level: Optional[str] = None,
        customer_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
    ) -> Tuple[List[Assessment], int]:
        """
        Retrieve paginated list of assessments with optional filters.
        """
        filters = []
        if recommendation:
            filters.append(Assessment.recommendation == recommendation)
        if risk_level:
            filters.append(Assessment.risk_level == risk_level)
        if customer_id:
            tx_subq = select(Transaction.id).where(Transaction.customer_id == customer_id)
            filters.append(Assessment.transaction_id.in_(tx_subq))
        if transaction_id:
            tx_subq = select(Transaction.id).where(Transaction.transaction_id == transaction_id)
            filters.append(Assessment.transaction_id.in_(tx_subq))

        count_stmt = select(func.count()).select_from(Assessment)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Assessment)
            .options(selectinload(Assessment.transaction))
            .order_by(Assessment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if filters:
            stmt = stmt.where(*filters)

        items = list((await db.execute(stmt)).scalars().all())
        return items, total

    @classmethod
    async def get_assessment_by_id(
        cls,
        db: AsyncSession,
        assessment_id: str,
    ) -> Optional[Assessment]:
        """
        Retrieve a single assessment by assessment_id.
        """
        stmt = (
            select(Assessment)
            .options(selectinload(Assessment.transaction))
            .where(Assessment.assessment_id == assessment_id)
        )
        return (await db.execute(stmt)).scalars().first()

    @classmethod
    async def get_assessment_by_transaction_id(
        cls,
        db: AsyncSession,
        transaction_id: str,
    ) -> Optional[Assessment]:
        """
        Retrieve assessment for a specific transaction by transaction_id.
        """
        stmt = (
            select(Assessment)
            .options(selectinload(Assessment.transaction))
            .join(Transaction, Transaction.id == Assessment.transaction_id)
            .where(Transaction.transaction_id == transaction_id)
            .order_by(Assessment.created_at.desc())
        )
        return (await db.execute(stmt)).scalars().first()
