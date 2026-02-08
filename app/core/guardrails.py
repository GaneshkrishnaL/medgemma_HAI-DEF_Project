import re
from dataclasses import dataclass

@dataclass
class GuardrailResult:
    allowed: bool
    reason: str = ""
    override_response: str | None = None
    urgency: str = "routine"  # routine | urgent

UNSAFE_PATTERNS = [
    r"\b(dose|dosage|mg|milligram|prescribe)\b",
    r"\b(suicide|kill myself|self-harm)\b",
    r"\b(make a bomb|explosive)\b",
]

URGENT_SYMPTOMS = [
    r"\b(chest pain|shortness of breath|trouble breathing)\b",
    r"\b(face droop|slurred speech|one-sided weakness)\b",
    r"\b(severe bleeding|passed out|unconscious)\b",
]

def run_guardrails(user_text: str) -> GuardrailResult:
    t = user_text.lower()

    for p in UNSAFE_PATTERNS:
        if re.search(p, t):
            return GuardrailResult(
                allowed=False,
                reason="unsafe_request",
                override_response=(
                    "I can’t help with that request. If this is a medical concern, "
                    "please contact a licensed clinician. If you’re in immediate danger, "
                    "seek local emergency help right now."
                )
            )

    for p in URGENT_SYMPTOMS:
        if re.search(p, t):
            return GuardrailResult(
                allowed=True,
                urgency="urgent",
                reason="urgent_symptoms_detected",
            )

    return GuardrailResult(allowed=True)
