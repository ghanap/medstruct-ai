# MedStruct AI

MedStruct AI is a locally-hosted AI pipeline designed to intelligently triage, process, and structure medical documents and X-Rays with zero cloud dependencies.

## Key Features
- **Intelligent Triage Phase**: Uses local `llama3` to automatically classify uploaded files as either Documents or X-Rays.
- **Two-Pass Routing**: 
  - **Documents**: Processed via Microsoft `trocr-small-handwritten` for highly accurate local OCR, followed by `llama3` for strict JSON extraction.
  - **X-Rays**: Processed directly via `llava` (Vision LLM) to analyze medical imaging without OCR.
- **Full Privacy**: 100% offline and HIPAA-ready. No outbound network calls.
- **Lightning Fast CI/CD**: Uses a custom GitLab Runner setup with aggressive local caching.

## Getting Started
Run the interactive dashboard:
```bash
pip install -r requirements.txt
streamlit run app.py
```
