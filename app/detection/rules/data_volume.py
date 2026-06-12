from app.detection.rules.base import BaseDetectionRule, DetectionResult
from app.models.event import NormalizedEvent


class DataVolumeSpikeRule(BaseDetectionRule):

    def evaluate(
        self,
        event: NormalizedEvent,
        baselines: dict,
    ) -> DetectionResult:

        if event.event_type != "file_download":
            return DetectionResult(
                fired=False,
                anomaly_type="data_volume_spike",
                severity="low",
                confidence=0.0,
                explanation={}
            )

        if not event.bytes_transferred:
            return DetectionResult(
                fired=False,
                anomaly_type="data_volume_spike",
                severity="low",
                confidence=0.0,
                explanation={}
            )

        baseline = baselines.get("data_volume")
        if not baseline:
            return DetectionResult(
                fired=False,
                anomaly_type="data_volume_spike",
                severity="low",
                confidence=0.0,
                explanation={"reason": "no baseline available"}
            )

        params = baseline.parameters
        mean = params.get("mean_daily_bytes", 0)
        std_dev = params.get("std_dev", 1)

        if std_dev == 0:
            std_dev = mean * 0.1 or 1

        z_score = (event.bytes_transferred - mean) / std_dev

        fired = z_score > 2.0

        if z_score > 4.0:
            severity = "critical"
            confidence = 0.95
        elif z_score > 3.0:
            severity = "high"
            confidence = 0.85
        elif z_score > 2.0:
            severity = "medium"
            confidence = 0.7
        else:
            severity = "low"
            confidence = 0.0

        mb_transferred = round(event.bytes_transferred / 1024 / 1024, 2)
        mean_mb = round(mean / 1024 / 1024, 2)

        return DetectionResult(
            fired=fired,
            anomaly_type="data_volume_spike",
            severity=severity,
            confidence=confidence,
            explanation={
                "bytes_transferred": event.bytes_transferred,
                "mb_transferred": mb_transferred,
                "user_mean_daily_mb": mean_mb,
                "z_score": round(z_score, 2),
                "interpretation": f"Downloaded {mb_transferred}MB, user's normal is {mean_mb}MB/day (z-score: {round(z_score, 1)})"
            }
        )