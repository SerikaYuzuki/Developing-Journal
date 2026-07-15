# PersonalJournal

Quarto-based personal journal site with a `uv`-managed Python environment.

## Development

Install `uv`, `direnv`, and Quarto on each machine. This project keeps the `uv`
virtual environment in the project-local `.venv/` directory, which is ignored by
Git.

### First setup

```bash
uv python install
direnv allow
uv sync
python -m ipykernel install --user --name quarto-notes --display-name "Python (quarto-notes)"
./scripts/patch-quarto-visual-editor-mathjax.sh
```

Install the Quarto VS Code extension before running the final command. It enables
the `physics` and `mhchem` MathJax extensions in the Visual Editor. Run it again
after a Quarto extension update if the Visual Editor math preview stops working.
If VS Code is already open when applying the patch, run "Developer: Reload
Window" once.

The virtual environment is stored at:

```bash
.venv/
```

Do not commit `.venv`, `_freeze`, `.quarto`, Jupyter checkpoints, or local
runtime/cache files. This repository does commit `_site`, so local renders update
the static site output that should be committed together with source changes.

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

Because this repository does not use GitHub Pages deployment, commit the updated
`_site` files when you want to publish or preserve rendered output.

## Main Python Packages

- `numpy`
- `pandas`
- `matplotlib`
- `plotly`
- `jupyter`
- `ipykernel`
