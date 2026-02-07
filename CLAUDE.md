# CLAUDE.md

This file provides guidance for AI assistants working with this repository.

## Project Overview

This repository contains two Python tools:

1. **`clean.py`** — File system utility for listing directory contents by glob pattern and reporting file sizes in human-readable units (KB/MB). Uses only the Python standard library.
2. **`news.py`** — Web-based news aggregator (Flask) covering Czech/world politics, sports, culture, and IT/AI. Fetches RSS feeds in parallel, caches results, and serves a modern responsive single-page UI.

## Repository Structure

```
tools/
├── .github/
│   └── workflows/
│       └── pylint.yml        # CI: runs Pylint on Python 3.8, 3.9, 3.10
├── templates/
│   └── index.html            # News aggregator frontend (HTML/CSS/JS)
├── clean.py                  # File system utility module
├── news.py                   # News aggregator Flask app
├── requirements.txt          # Python dependencies (feedparser, flask)
├── .gitignore
└── CLAUDE.md                 # This file
```

## News Aggregator (`news.py`)

### Running

```bash
pip install -r requirements.txt
python news.py
# → http://localhost:5000
```

### Architecture

- **Backend:** Flask with JSON API (`/api/feeds`, `/api/feeds/<category>`)
- **Frontend:** Single-page app in `templates/index.html` using vanilla JS, CSS custom properties for theming
- **Feed fetching:** `feedparser` library, parallelized with `concurrent.futures.ThreadPoolExecutor`, 5-minute in-memory cache

### Categories & RSS Sources

| Category | Key | Sources |
|---|---|---|
| Česká politika | `cz-politika` | iROZHLAS, Novinky.cz, ČT24, Aktuálně.cz, ČTK, Deník.cz |
| Světová politika | `svet-politika` | iROZHLAS, BBC World, Al Jazeera, Aktuálně.cz |
| Český sport | `cz-sport` | iROZHLAS, iSport.cz, Aktuálně.cz |
| Světový sport | `svet-sport` | BBC Sport, ESPN |
| Kultura | `kultura` | iROZHLAS, Aktuálně.cz, Guardian Film, Guardian Music |
| IT & AI | `ai` | iROZHLAS, Ars Technica, The Verge AI, TechCrunch, MIT News AI |

### API Endpoints

- `GET /` — Main page (serves `templates/index.html`)
- `GET /api/feeds` — All categories (JSON)
- `GET /api/feeds/<key>` — Single category or group alias (`politika`, `sport`, `kultura`, `ai`)

### Frontend Features

- Dark/light theme toggle (persisted in localStorage)
- Category tab filtering
- Auto-refresh every 5 minutes
- Keyboard shortcuts: `r` = refresh, `t` = toggle theme
- Responsive card grid layout
- Skeleton loading states

### Adding/Changing RSS Sources

Edit the `FEEDS` dict in `news.py`. Each category has a list of `sources` with `name` and `url` keys. Group aliases are in `CATEGORY_GROUPS`.

## File System Utility (`clean.py`)

### Key Functions

- **`list_dir(path, ext='*.*', recursive=False)`** — Lists files matching a glob pattern. Note: the `recursive` parameter is accepted but unused. Calls `os.chdir(path)`, which mutates global process state.
- **`get_file_size(file, out='kb')`** — Returns formatted string with file name and size. Supports `'kb'` and `'mb'`. Raises `UnboundLocalError` for other values of `out`.

## Development Workflow

### Prerequisites

- Python 3.8+

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Linting

Pylint is the sole code quality tool. No `.pylintrc` — runs with defaults.

```bash
pip install pylint
pylint $(git ls-files '*.py')
```

### Testing

No test framework is configured.

### CI/CD

GitHub Actions (`.github/workflows/pylint.yml`) runs on every push:
1. Sets up Python (matrix: 3.8, 3.9, 3.10)
2. Installs Pylint
3. Runs `pylint $(git ls-files '*.py')`

## Conventions

- Pylint must pass in CI
- Docstrings on all public functions
- Standard library preferred; third-party packages listed in `requirements.txt`

## Known Issues (`clean.py`)

- `list_dir()` uses `os.chdir()` which changes global working directory state
- `get_file_size()` will raise `UnboundLocalError` if `out` is not `'kb'` or `'mb'`
- Docstrings contain placeholder text (`_summary_`, `_type_`, `_description_`)
- `recursive` parameter in `list_dir()` is accepted but has no effect
