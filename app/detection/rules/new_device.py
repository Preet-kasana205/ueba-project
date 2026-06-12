from app.detection.rules.base import BaseDetectionRule, DetectionResult
from app.models.event import NormalizedEvent


class NewDeviceRule(BaseDetectionRule):

    def evaluate(
        self,
        event: NormalizedEvent,
        baselines: dict,
    ) -> DetectionResult:

        if not event.device_id:
            return DetectionResult(
                fired=False,
                anomaly_type="new_device",
                severity="low",
                confidence=0.0,
                explanation={}
            )

        baseline = baselines.get("known_devices")
        if not baseline:
            return DetectionResult(
                fired=False,
                anomaly_type="new_device",
                severity="low",
                confidence=0.0,
                explanation={"reason": "no baseline available"}
            )

        known_devices = baseline.parameters.get("known_devices", [])
        is_new = event.device_id not in known_devices

        return DetectionResult(
            fired=is_new,
            anomaly_type="new_device",
            severity="high" if is_new else "low",
            confidence=0.95 if is_new else 0.0,
            explanation={
                "device_id": event.device_id,
                "known_devices": known_devices,
                "interpretation": f"Device {event.device_id} has never been seen for this user"
                if is_new else "Known device"
            }
        )