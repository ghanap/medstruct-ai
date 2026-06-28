# MedStruct AI - Specification

## Problem Statement

Medical prescriptions and reports are often handwritten or unstructured, making it difficult to store, search, and analyze patient information digitally, especially in areas with limited internet connectivity.

## Solution

MedStruct AI is an offline-first AI application that extracts structured medical information from prescription images using OCR and a local Small Language Model (SLM). The extracted data is stored locally in SQLite for quick retrieval.

## Objectives

- Work completely offline
- Run inference on CPU
- Extract structured medical data
- Store records locally
- Provide a simple user interface

## Input

- Prescription Image (.jpg, .png)
- Prescription PDF

## Output

Structured JSON

Example:

```json
{
  "patient_name": "",
  "doctor": "",
  "diagnosis": [],
  "medicines": [],
  "follow_up": ""
}
```

## Tech Stack

- Streamlit
- Python
- Tesseract OCR
- llama.cpp
- TinyLlama GGUF
- SQLite

## Constraints

- CPU only
- No cloud APIs
- Offline operation