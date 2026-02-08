# MedGemma Copilot (v1.0) 🩺

MedGemma Copilot is a patient education and doctor-visit preparation tool powered by Google's **MedGemma 1.5-4b-it** (multimodal) and **MedASR**. It helps users understand medical reports, scans, and doctor's notes by providing structured, plain-language summaries and actionable questions for their next consultation.

## 🚀 Key Features

- **Multimodal Medical Q&A**: Analyze both medical text reports and images (X-rays, scans) using MedGemma.
- **Medical Speech-to-Text**: Built-in ASR for transcribing patient questions or recordings of doctor interactions.
- **Safety Guardrails**: Built-in filtering for unsafe requests (dosage advice, self-harm) and automatic detection of urgent symptoms.
- **Patient-Centric Output**: AI responses are strictly structured into:
  1. Plain-language summary
  2. Questions to ask a doctor
  3. Red flags (urgent care indicators)
  4. Groundedness references (based on provided text/images)
- **Local History**: SQLite-backed record keeping for users to track their previous queries.

## 🛠️ Project Structure

```text
medgemma-copilot/
├── app/
│   ├── core/
│   │   ├── orchestrator.py  # Central logic coordinator
│   │   ├── prompts.py       # MedGemma system instructions
│   │   ├── guardrails.py    # Safety & urgency filtering
│   │   └── metrics.py       # Quality and groundedness tracking
│   ├── db/
│   │   └── store.py         # SQLite database management
│   ├── models/
│   │   ├── medgemma.py      # MedGemma 1.5-4b-it interface
│   │   └── medasr.py        # Medical ASR interface
│   ├── ui/
│   │   └── streamlit_app.py # Modern split-screen UI
├── eval/                    # Evaluation scripts and datasets
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- MPS/GPU (Recommended for inference)
- Hugging Face Token (with access to `google/medgemma-1.5-4b-it` and `google/medasr`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/GaneshkrishnaL/medgemma_HAI-DEF_Project.git
cd medgemma_HAI-DEF_Project

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Authentication
Login to Hugging Face to access the gated models:
```bash
huggingface-cli login
```

### 4. Running the App
```bash
export PYTHONPATH=$PYTHONPATH:.
streamlit run app/ui/streamlit_app.py
```

## ⚠️ Disclaimer
This tool is for **educational and visit-preparation purposes only**. It does not provide medical diagnoses, medication dosing, or treatment plans. It is not a replacement for professional medical evaluation.
