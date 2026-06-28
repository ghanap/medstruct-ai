# 🏥 MedStruct AI

> Offline-first medical document structuring — prescriptions, lab reports, and discharge summaries converted to structured JSON, stored locally, searchable without internet.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.35%2B-red)
![License](https://img.shields.io/badge/license-MIT-green)
![Offline](https://img.shields.io/badge/mode-100%25%20offline-brightgreen)

## Features

| Feature | Detail |
|---|---|
| 📄 Upload | JPG, PNG, BMP, TIFF, PDF |
| 🔍 OCR | Tesseract 5 (local, CPU) |
| 🤖 LLM | GGUF via llama.cpp or Ollama |
| 💾 Storage | SQLite (local file) |
| 🔒 Privacy | Zero external calls |
| ⚡ CPU-first | Runs on edge / low-resource devices |

## Quick start

```bash
# 1. Clone
git clone https://gitlab.example.com/your-team/medstruct-ai.git
cd medstruct-ai

# 2. Setup (creates venv, installs deps, inits DB)
chmod +x setup.sh && ./setup.sh

# 3. Download a GGUF model (example: Mistral 7B Q4)
mkdir -p models
wget -P models/ https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# 4. Configure
cp .env.example .env   # set MODEL_PATH if needed

# 5. Run
source venv/bin/activate
streamlit run app.py
```

Open http://localhost:8501

## Tesseract install

```bash
# Ubuntu / Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract

# Windows — download installer from
# https://github.com/UB-Mannheim/tesseract/wiki
```

## Project structure

```
medstruct-ai/
├── app.py                  # Streamlit UI
├── requirements.txt
├── setup.sh
├── .env.example
├── .gitlab-ci.yml          # CI/CD pipeline
├── db/schema.sql
├── models/                 # Place GGUF here
├── utils/
│   ├── ocr.py
│   ├── llm.py
│   ├── database.py
│   └── pipeline.py
└── schemas/prescription.json
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `LLM_BACKEND` | `llama` | `llama` or `ollama` |
| `MODEL_PATH` | `models/mistral…gguf` | Path to GGUF model |
| `LLM_CTX` | `4096` | Context window tokens |
| `LLM_THREADS` | `4` | CPU threads for inference |
| `OLLAMA_MODEL` | `mistral` | Model name for Ollama backend |

## License

MIT — see [LICENSE](LICENSE)
