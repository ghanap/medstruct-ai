# Contributing to MedStruct AI

Thanks for helping improve MedStruct AI. This document covers the workflow
for contributors working on this project during and after the hackathon.

## Development setup

```bash
git clone https://gitlab.example.com/your-team/medstruct-ai.git
cd medstruct-ai
./setup.sh
source venv/bin/activate
```

Install dev tools:

```bash
pip install ruff black pytest pytest-cov
```

## Branch strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, always deployable |
| `dev` | Integration branch |
| `feat/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation only |

Create a branch:

```bash
git checkout -b feat/your-feature-name
```

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add PDF multi-page support
fix: handle empty OCR output gracefully
docs: update README quick-start
chore: bump llama-cpp-python to 0.2.80
```

## Running tests

```bash
pytest tests/ -v
```

Ensure tests pass and the offline check passes before opening an MR:

```bash
grep -rn "requests.get\|urllib.request" utils/ app.py && echo FAIL || echo PASS
```

## Merge request checklist

- [ ] Tests added / updated
- [ ] `ruff check .` passes
- [ ] No outbound network calls introduced
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] MR description explains what changed and why

## Code style

- Python 3.10+
- Black formatting (`black .`)
- Ruff linting (`ruff check .`)
- Docstrings on all public functions
- Type hints encouraged

## Reporting issues

Open a GitLab issue with:
1. What you expected to happen
2. What actually happened
3. Steps to reproduce
4. OS, Python version, model being used
