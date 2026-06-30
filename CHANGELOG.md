# Changelog

All notable changes to MedStruct AI are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- PDF first-page extraction support
- Dashboard page with aggregate stats
- `get_stats()` database utility

### Changed
- Improved OCR preprocessing (autocontrast + sharpen pipeline)

---

## [0.2.0] — 2025-07-05

### Added
- Ollama backend support via `LLM_BACKEND=ollama`
- Lab results extraction in JSON schema
- Search across medications (not just patient/doctor)
- JSON download button on history records
- CI/CD: offline network-call audit job

### Fixed
- Empty OCR text no longer crashes the pipeline
- SQLite concurrent write lock on rapid uploads

### Changed
- `EXTRACTION_PROMPT` updated for better structured output
- Medications stored in child table for queryability

---

## [0.1.0] — 2025-07-04  *(Hackathon day 1)*

### Added
- Initial project structure
- Tesseract OCR integration (`utils/ocr.py`)
- llama.cpp GGUF inference (`utils/llm.py`)
- SQLite schema and storage (`utils/database.py`)
- End-to-end pipeline (`utils/pipeline.py`)
- Streamlit UI: Upload, History, Search pages
- `setup.sh` one-command bootstrap
- `db/schema.sql`, `schemas/prescription.json`
- `.gitlab-ci.yml` with lint, test, build, audit stages
- README, CONTRIBUTING, CHANGELOG, LICENSE
