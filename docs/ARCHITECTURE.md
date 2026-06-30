# Architecture

## Workflow

```mermaid
graph TD
    A[Medical Image Upload] --> B[Triage Phase: llama3]
    B -->|Classified as X-Ray| C[Vision Model: llava]
    B -->|Classified as Document| D[OCR: trocr-small-handwritten]
    D --> E[Text Extraction: llama3]
    C --> F[Structured JSON]
    E --> F
    F --> G[SQLite Database]
    G --> H[Streamlit Dashboard]
```

## Components

### Frontend
- Streamlit

### AI Layer
- **Triage**: `llama3` (Local)
- **OCR**: `microsoft/trocr-small-handwritten` (Local)
- **Document Text LLM**: `llama3` (Local)
- **X-Ray Vision LLM**: `llava` (Local)

### Storage
- SQLite

### Output
- Strict JSON Formats
- Searchable Medical Database