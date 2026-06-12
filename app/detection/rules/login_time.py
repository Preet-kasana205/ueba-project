from app.detection.rules.base import BaseDetectionRule, DetectionResult
from app.models.event import NormalizedEvent


class UnusualLoginTimeRule(BaseDetectionRule):

    def evaluate(
        self,
        event: NormalizedEvent,
        baselines: dict,
    ) -> DetectionResult:

        if event.event_type not in ("login_success", "login_failed"):
            return DetectionResult(
                fired=False,
                anomaly_type="unusual_login_time",
                severity="low",
                confidence=0.0,
                explanation={}
            )

        baseline = baselines.get("login_hours")
        if not baseline:
            return DetectionResult(
                fired=False,
                anomaly_type="unusual_login_time",
                severity="low",
                confidence=0.0,
                explanation={"reason": "no baseline available"}
            )

        params = baseline.parameters
        mean_hour = params.get("mean_hour", 12)
        std_dev = params.get("std_dev", 2)
        event_hour = event.event_time.hour

        if std_dev == 0:
            std_dev = 1

        z_score = abs(event_hour - mean_hour) / std_dev

        fired = z_score > 2.0

        if z_score > 3.5:
            severity = "high"
            confidence = 0.9
        elif z_score > 2.5:
            severity = "medium"
            confidence = 0.7
        else:
            severity = "low"
            confidence = 0.5

        return DetectionResult(
            fired=fired,
            anomaly_type="unusual_login_time",
            severity=severity,
            confidence=confidence,
            explanation={
                "event_hour": event_hour,
                "user_mean_hour": mean_hour,
                "user_std_dev": std_dev,
                "z_score": round(z_score, 2),
                "interpretation": f"Login at {event_hour}:00 is {round(z_score, 1)} standard deviations from this user's normal login time of {int(mean_hour)}:00"
            }
        )