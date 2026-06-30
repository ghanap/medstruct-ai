# MedStruct AI - Specification

## Problem Statement

Medical prescriptions and reports are often handwritten or unstructured, making it difficult to store, search, and analyze patient information digitally, especially in areas with limited internet connectivity.

## Solution

MedStruct AI is an offline-first AI application that leverages a Two-Pass Pipeline to intelligently triage and extract structured medical information from documents and X-Rays using state-of-the-art local SLMs (Small Language Models) and Vision-Language Models. The extracted data is securely stored locally in SQLite for fast retrieval.

## Objectives

- Work completely offline (100% HIPAA-ready)
- Run inference purely on CPU without cloud dependencies
- Automatically triage input formats (X-Ray vs Document)
- Extract structured medical data and anomalies
- Store records locally
- Provide a simple user interface

## Input

- Prescription Image / Medical Document (.jpg, .png)
- Medical X-Ray Image (.jpg, .png)

## Output

Strictly formatted JSON containing patient details, medications, or X-Ray anomalies.

## Tech Stack

- Streamlit
- Python
- Microsoft TrOCR (`trocr-small-handwritten`)
- `llama3` via Ollama
- `llava` (Vision LLM)
- SQLite

## Constraints

- Zero cloud APIs
- Offline operation
- Resilient to poor handwriting (via TrOCR)