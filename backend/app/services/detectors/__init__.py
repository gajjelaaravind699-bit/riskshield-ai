"""
Detectors package initialization.
"""

from app.services.detectors.base import BaseDetector, CandidateFinding
from app.services.detectors.shared_entity_detectors import (
    SharedPaymentInstrumentDetector,
    SharedDeviceDetector,
    SharedIPClusterDetector,
)
from app.services.detectors.velocity_detectors import (
    VelocityBurstDetector,
    RapidFailureBurstDetector,
)

ALL_DETECTORS = [
    SharedPaymentInstrumentDetector,
    SharedDeviceDetector,
    SharedIPClusterDetector,
    VelocityBurstDetector,
    RapidFailureBurstDetector,
]

__all__ = [
    "BaseDetector",
    "CandidateFinding",
    "SharedPaymentInstrumentDetector",
    "SharedDeviceDetector",
    "SharedIPClusterDetector",
    "VelocityBurstDetector",
    "RapidFailureBurstDetector",
    "ALL_DETECTORS",
]
