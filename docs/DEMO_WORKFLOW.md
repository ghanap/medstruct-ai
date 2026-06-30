# Demo Workflow

## Step 1
Upload a medical image (Prescription or X-Ray).

↓

## Step 2 (Triage Phase)
`llama3` automatically classifies the image type.

↓

## Step 3 (Routing Phase)
- **If Document:** Microsoft `trocr-small-handwritten` extracts the raw text.
- **If X-Ray:** Process is routed to `llava` Vision LLM (skips OCR).

↓

## Step 4 (Extraction Phase)
- **Document Text:** `llama3` strictly formats the text into JSON.
- **X-Ray Analysis:** `llava` analyzes the image and outputs JSON anomalies.

↓

## Step 5
Data is securely stored in local SQLite database.

↓

## Step 6
User views extracted medical information via Streamlit Dashboard and can search historical records.