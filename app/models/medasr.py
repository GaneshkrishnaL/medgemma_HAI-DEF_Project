import torch
from transformers import pipeline
import librosa

DEFAULT_ASR_ID = "google/medasr"

class MedASRClient:
    def __init__(self, model_id: str = DEFAULT_ASR_ID):
        # Auto-detect device for faster transcription
        self.device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
        self.asr = pipeline("automatic-speech-recognition", model=model_id, device=self.device)

    def transcribe(self, audio_path: str) -> str:
        # Load audio using librosa to avoid ffmpeg dependency in transformers
        # transformers pipeline handles numpy arrays (float32, 16kHz)
        audio, sr = librosa.load(audio_path, sr=16000)
        result = self.asr(audio)
        return (result.get("text") or "").strip()
