# PersonalJournal

Quarto-based personal journal site with a `uv`-managed Python environment.

## Development

Install `uv`, `direnv`, and Quarto on each machine. This project keeps the `uv`
virtual environment outside the iCloud-synced checkout via `.envrc`.

### First setup

```bash
uv python install
direnv allow
uv sync
python -m ipykernel install --user --name quarto-notes --display-name "Python (quarto-notes)"
```

The virtual environment is stored at:

```bash
$HOME/.local/uv-venvs/quarto-notes
```

Do not commit `.venv`, `_site`, `_freeze`, `.quarto`, Jupyter checkpoints, or
rendered HTML/PDF/DOCX outputs. If a PDF/DOCX/HTML file is an intentional source
asset, add it deliberately with an exception or `git add -f`.

### Local preview

```bash
uv run quarto preview
```

VS Code's Quarto extension uses the project wrapper at `scripts/quarto`, so the
toolbar Preview button also runs through `uv`.
The wrapper also sets `QUARTO_PYTHON` to the uv-managed Python interpreter.
Run "Developer: Reload Window" in VS Code after pulling this setting.

### Local render

```bash
uv run quarto render
```

The published site is rendered by GitHub Actions and deployed to GitHub Pages
from the `_site` artifact. Generated site files should not be committed.

If GitHub Pages is currently configured to publish from `docs/` or a `gh-pages`
branch, switch the repository Pages source to GitHub Actions after this workflow
is merged.

## Main Python Packages

- `numpy`
- `pandas`
- `matplotlib`
- `plotly`
- `jupyter`
- `ipykernel`
