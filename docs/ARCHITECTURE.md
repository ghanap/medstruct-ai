# Architecture

## Workflow

```
Prescription Image
        │
        ▼
Tesseract OCR
        │
        ▼
Extracted Text
        │
        ▼
TinyLlama (Local)
        │
        ▼
Structured JSON
        │
        ▼
SQLite Database
        │
        ▼
Streamlit Dashboard
```

## Components

### Frontend

- Streamlit

### AI Layer

- OCR
- Local LLM

### Storage

- SQLite

### Output

- JSON
- Medical Record