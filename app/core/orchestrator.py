from PIL import Image
from app.core.prompts import build_user_prompt
from app.core.guardrails import run_guardrails
from app.core.metrics import log_event, has_required_sections, groundedness_proxy

class Orchestrator:
    def __init__(self, medgemma_client, medasr_client=None):
        self.medgemma = medgemma_client
        self.medasr = medasr_client

    def transcribe_if_audio(self, audio_path: str | None) -> str | None:
        if not audio_path:
            return None
        if not self.medasr:
            return None
        return self.medasr.transcribe(audio_path)

    def chat(self, user_id: str, user_question: str, pasted_text: str | None, image: Image.Image | None):
        gr = run_guardrails(user_question + "\n" + (pasted_text or ""))
        if not gr.allowed:
            log_event({"type": "refusal", "reason": gr.reason})
            return gr.override_response

        prompt = build_user_prompt(user_question, pasted_text)

        answer = self.medgemma.generate(prompt=prompt, image=image, max_new_tokens=650, temperature=0.2)

        # Light post-check + logging
        sec_ok = has_required_sections(answer)
        ground = groundedness_proxy(answer, pasted_text)

        log_event({
            "type": "chat",
            "urgent": (gr.urgency == "urgent"),
            "sections_ok": sec_ok,
            "groundedness_proxy": ground
        })

        # If urgent symptoms, prepend a cautious note
        if gr.urgency == "urgent":
            answer = (
                "⚠️ **Urgent note:** Some symptoms you mentioned can be serious. "
                "If you feel unsafe or symptoms are severe/worsening, seek urgent care or local emergency services.\n\n"
                + answer
            )

        return answer
