import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyFinding:
    category: str


class SafetyEvaluator:
    """Small deterministic evaluator for exercising safety telemetry locally."""

    patterns = {
        "prompt_injection": (
            re.compile(r"ignore (all |the )?previous instructions", re.IGNORECASE),
            re.compile(r"reveal (the )?system prompt", re.IGNORECASE),
        ),
        "self_harm": (
            re.compile(r"\bkill myself\b", re.IGNORECASE),
            re.compile(r"\bsuicide\b", re.IGNORECASE),
        ),
        "violence": (
            re.compile(r"\bhow (can|do) i (kill|hurt|attack)\b", re.IGNORECASE),
        ),
    }

    def evaluate(self, text: str) -> list[SafetyFinding]:
        return [
            SafetyFinding(category)
            for category, patterns in self.patterns.items()
            if any(pattern.search(text) for pattern in patterns)
        ]
