# Development Guide

**Project:** Compose Release Assurance
**Status:** Initial quality-foundation workflow

## 1. Supported Runtime

The initial supported runtime is Python 3.14.

Do not claim support for another Python version until automated validation and
documentation explicitly add it.

## 2. Windows Setup

From the repository root:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-virtualenv -r requirements-dev.txt
.\.venv\Scripts\pre-commit.exe install
```

## 3. Linux and WSL Setup

From the repository root:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install --require-virtualenv -r requirements-dev.txt
.venv/bin/pre-commit install
```

## 4. Required Local Quality Checks

Windows PowerShell:

```powershell
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe
.\.venv\Scripts\pytest.exe
.\.venv\Scripts\pre-commit.exe run --all-files
```

All commands must exit with code `0` before a work item is considered complete.

## 5. Scope of This Foundation

This stage establishes the local developer quality workflow only.

It does not introduce application endpoints, database models, Docker Compose
services, business logic, enterprise integrations, or deployment automation.

Mypy checks the `tests/` directory during this foundation stage. Its scope will
expand to product source directories when the first Python implementation
module is added.
