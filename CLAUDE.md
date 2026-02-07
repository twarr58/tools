# CLAUDE.md

This file provides guidance for AI assistants working with this repository.

## Project Overview

A small Python utility module (`clean.py`) providing file system helpers: listing directory contents by glob pattern and reporting file sizes in human-readable units (KB/MB). Uses only the Python standard library (`glob`, `os`).

## Repository Structure

```
tools/
├── .github/
│   └── workflows/
│       └── pylint.yml    # CI: runs Pylint on Python 3.8, 3.9, 3.10
├── clean.py              # Main (and only) source module
└── CLAUDE.md             # This file
```

There is no `README.md`, `LICENSE`, `.gitignore`, or `requirements.txt`.

## Key Functions

- **`list_dir(path, ext='*.*', recursive=False)`** — Lists files matching a glob pattern in the given directory. Note: the `recursive` parameter is accepted but unused (explicitly deleted inside the function). Calls `os.chdir(path)`, which mutates global process state.
- **`get_file_size(file, out='kb')`** — Returns a formatted string with the file name and its size. Supports `'kb'` and `'mb'` output units. If `out` is neither `'kb'` nor `'mb'`, `out_div` and `ext` will be undefined and the function will raise `UnboundLocalError`.

## Development Workflow

### Prerequisites

- Python 3.8, 3.9, or 3.10

### Linting

The project uses **Pylint** as its sole code quality tool. There is no local `.pylintrc` configuration — Pylint runs with defaults.

```bash
pip install pylint
pylint clean.py
```

### Testing

There are no tests or test framework configured. No `pytest`, `unittest`, or similar setup exists.

### CI/CD

GitHub Actions runs on every push (`.github/workflows/pylint.yml`):
1. Checks out code
2. Sets up Python (matrix: 3.8, 3.9, 3.10)
3. Installs Pylint
4. Runs `pylint $(git ls-files '*.py')`

### No Build Step

This is a plain Python module with no build system, packaging config (`setup.py`, `pyproject.toml`), or external dependencies.

## Conventions

- Python 3 with standard library only — no third-party packages
- Google-style docstrings (with placeholder text currently unfilled)
- Type hints on function signatures (return type annotations)
- Pylint must pass in CI across Python 3.8–3.10

## Known Issues

- `list_dir()` uses `os.chdir()` which changes global working directory state
- `get_file_size()` will raise `UnboundLocalError` if `out` is not `'kb'` or `'mb'`
- Docstrings contain placeholder text (`_summary_`, `_type_`, `_description_`)
- `recursive` parameter in `list_dir()` is accepted but has no effect
