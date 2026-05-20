# PersonalJournal

Quarto-based personal journal site with a `uv`-managed Python environment.

## Setup

1. Install `uv` and `direnv`.

```bash
uv python install 3.12
```

2. Allow the project environment once:

```bash
direnv allow
```

After that, entering this directory will automatically:

- create `.venv` with the Python version from `.python-version`
- run `uv sync` when dependencies change
- activate the virtual environment

## Main Python Packages

- `numpy`
- `pandas`
- `matplotlib`
- `plotly`
- `jupyter`
- `ipykernel`
