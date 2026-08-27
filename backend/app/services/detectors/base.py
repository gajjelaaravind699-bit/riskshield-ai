"""
Base detector interface and candidate finding container for pattern analysis.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.analysis import AnalysisConfig


@dataclass
class CandidateFinding:
    """
    In-memory representation of an observed pattern candidate before persistence.
    """
    finding_type: str
    severity: str
    title: str
    explanation: str
    evidence_payload: Dict[str, Any]
    related_entities: List[Tuple[int, str]] = field(default_factory=list)  # (entity_id, role)
    related_transaction_ids: List[int] = field(default_factory=list)

    def compute_fingerprint(self) -> str:
        """
        Compute a deterministic SHA-256 fingerprint from the invariant components:
        finding_type, sorted entity (id, role) tuples, and sorted transaction IDs.
        """
        sorted_entities = sorted(self.related_entities, key=lambda x: (x[0], x[1]))
        sorted_tx_ids = sorted(self.related_transaction_ids)
        
        fingerprint_data = {
            "finding_type": self.finding_type,
            "entities": sorted_entities,
            "transactions": sorted_tx_ids,
        }
        encoded = json.dumps(fingerprint_data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class BaseDetector(ABC):
    """
    Abstract base detector for graph and temporal relationship analysis.
    """
    @abstractmethod
    async def detect(
        self,
        db: AsyncSession,
        config: AnalysisConfig,
    ) -> List[CandidateFinding]:
        """
        Execute detection logic against persisted relational data and return candidate findings.
        """
        pass
