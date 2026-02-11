import torch
from transformers import pipeline

DEFAULT_ASR_ID = "google/medasr"

class MedASRClient:
    def __init__(self, model_id: str = DEFAULT_ASR_ID):
        # Auto-detect device for faster transcription
        device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
        self.asr = pipeline("automatic-speech-recognition", model=model_id, device=device)

    def transcribe(self, audio_path: str) -> str:
        result = self.asr(audio_path)
        return (result.get("text") or "").strip()
