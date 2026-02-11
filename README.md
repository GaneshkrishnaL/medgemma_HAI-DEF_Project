# MedGemma Copilot Pro 🩺

MedGemma Copilot Pro is an advanced medical AI assistant for patient education, doctor-visit preparation, and personal health tracking. It leverages Google's **MedGemma 1.5-4b-it** (multimodal) and **MedASR** to provide a comprehensive health companion experience.

## 🚀 Key Features

- **Personalized Accounts**: Secure user login and registration to keep your medical data private.
- **Multimodal Chat & Analysis**: 
  - Analyze medical text reports and images (X-rays, scans).
  - Voice-to-Text support via a live microphone (no FFmpeg required).
  - Structured, plain-language AI responses.
- **Visit History**: Session-based chat storage. Revisit previous consultations and scan analyses at any time.
- **Health Vitals Monitoring**:
  - Track Blood Pressure (Systolic/Diastolic) and Blood Sugar levels.
  - Interactive trend visualizations powered by Plotly.
  - **AI Insights**: Automated trend analysis with actionable medical suggestions.
- **Safety First**: Built-in guardrails for unsafe requests and automatic urgency detection for severe symptoms.

## 🛠️ Project Structure

```text
medgemma-copilot/
├── app/
│   ├── core/
│   │   ├── orchestrator.py    # Logic coordinator
│   │   ├── guardrails.py      # Safety filtering
│   │   ├── vitals_analyzer.py # BP/Sugar trend analysis
│   │   └── prompts.py         # MedGemma instructions
│   ├── db/
│   │   └── store.py           # SQLite Pro (Users, Sessions, Vitals)
│   ├── models/
│   │   ├── medgemma.py        # 4B Multimodal Model interface
│   │   └── medasr.py          # Medical ASR (FFmpeg-free)
│   ├── ui/
│   │   └── streamlit_app.py   # Modern Pro Dashboard
├── requirements.txt           # Modernized dependencies
└── README.md                  # Comprehensive guide
```

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- GPU/MPS (Highly Recommended)
- Hugging Face Token (Access to google/medgemma models)

### 2. Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Running the App
```bash
export PYTHONPATH=$PYTHONPATH:.
streamlit run app/ui/streamlit_app.py
```

## ⚠️ Disclaimer
This tool is for **educational and visit-preparation purposes only**. It does not provide medical diagnoses or treatment plans. In case of emergency, contact local emergency services immediately.
