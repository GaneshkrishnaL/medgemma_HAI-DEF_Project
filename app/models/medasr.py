from transformers import pipeline

DEFAULT_ASR_ID = "google/medasr"

class MedASRClient:
    def __init__(self, model_id: str = DEFAULT_ASR_ID):
        # Transformers ASR pipeline
        self.asr = pipeline("automatic-speech-recognition", model=model_id)

    def transcribe(self, audio_path: str) -> str:
        result = self.asr(audio_path)
        return (result.get("text") or "").strip()
