from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.models.event import NormalizedEvent
from app.models.baseline import Baseline


@dataclass
class DetectionResult:
    fired: bool
    anomaly_type: str
    severity: str
    confidence: float
    explanation: dict


class BaseDetectionRule(ABC):

    @abstractmethod
    def evaluate(
        self,
        event: NormalizedEvent,
        baselines: dict,
    ) -> DetectionResult:
        pass