# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a course/lecture template using Claude Code + Beamer + Zotero with RAG-based literature search.
Each lecture is a standalone Beamer presentation with an accompanying Jupyter notebook.

## Build Commands

```bash
make slides                              # Compile every lecture into lectures/<lecture>/output/main.pdf
make steganography                       # Compile a single lecture (steganography or backdoors)
make clean                               # Clean build artifacts
uv run pytest tests/ -v                  # Test all exercise notebooks with solutions
uv run python scripts/syncing/main.py    # Run Zotero sync daemon
uv run python scripts/tools/rag.py "query"  # Search literature with RAG
```

## Architecture

### Lecture Structure
- `lectures/<lecture>/` - One folder per lecture (`steganography`, `backdoors`), each with its own `main.tex` and `output/`
- `lectures/<lecture>/main.tex` - Top-level LaTeX file that `\input`s all chapter slides into one PDF
- `lectures/<lecture>/output/main.pdf` - Compiled output (single PDF with all chapters + speaker notes)
- `lectures/<lecture>/XX_name/notes.md` - User's draft notes (source of truth, `--` = new slide, `s:` = speaker notes)
- `lectures/<lecture>/XX_name/slides.tex` - Chapter slides (no `\documentclass`, included by main.tex)
- `lectures/<lecture>/XX_name/figures/` - Extracted figures for this chapter
- `exercises/name/{notebook.ipynb, utils.py}` - Exercises (top-level folder, not inside the lecture folders)
- `lectures/<lecture>/XX_name/claude_notes.md` - AI's research notes (only when explicitly instructed)

### Figure Capture
Figures are captured by the user via a macOS hotkey (Cmd+Shift+6) while reading papers in Zotero.
Figures are saved as `bib/{key}/figures/{name}.png` with user-chosen names.
The daemon's label sync picks these up and adds `{key}/{name}` entries to `labels.bib`.

In notes, the user references figures as `@key/figure_name` (e.g., `@fillingham2025/staircase_sae`).
When adding a figure to slides, copy it from `bib/{key}/figures/` to `lectures/<lecture>/XX_name/figures/{key}/` and reference as `\paperfig{figures/{key}/{name}.png}{}`.

Do NOT auto-extract figures. Only use figures the user has explicitly captured.

### Presenter Mode
Use `pdfpc` to present with speaker notes on Mac:
```bash
pdfpc --notes=right lectures/steganography/output/main.pdf
```
This shows slides on the projector and notes + next slide on the presenter screen.

### Shared LaTeX Config
- `lib/preamble.tex` - Shared preamble included by all lectures
- `lib/packages.tex` - Beamer package imports
- `lib/settings.tex` - Beamer theme and formatting
- `lib/metadata.tex` - Course metadata (`\coursetitle`, `\instructor`, `\institution`)

### Bibliography System
- `bib/refs.bib` - BibTeX file auto-synced from Zotero
- `bib/labels.bib` - Extracted LaTeX labels for autocomplete
- `bib/[citation_key]/` - Per-paper folders containing fulltext, chapters, metadata

### Sync Pipeline (`scripts/syncing/main.py`)
Runs continuously (30s interval) via nohup in the background. Check if it's running with `pgrep -f syncing/main.py`. If not running, start it with:
```bash
nohup uv run python scripts/syncing/main.py > /dev/null 2>&1 &
```

### Experiments
- `experiments/` - Cloned experiment repositories (git-ignored)

### Configuration
`scripts/config.yaml` controls Zotero sync, text extraction, chapter splitting, and embeddings settings.

## Exercise System

### File structure

Each exercise lives in `exercises/name/` with two files:
- `notebook.ipynb` — the notebook students open (single source of truth)
- `utils.py` — test/check functions (print PASS/FAIL)

### Notebook cell pattern

Per exercise within a notebook, cells appear in this order:
1. **Markdown** — explanation + instructions
2. **Code cell** — skeleton with `# TODO`. Cell metadata must include `"exercise_id": "some_id"`
3. **Test cell** — calls check function from `utils.py` (e.g. `test_tangent(tangent)`)
4. **Hint/Solution markdown** — collapsible `<details>` blocks with the full standalone solution in a ` ```python ``` ` block. Cell metadata must include `"solution_id": "some_id"` matching the exercise

The solution code block must be a complete, standalone replacement for the exercise cell (full function/class definition, not just the body).

The notebook also needs at the top:
1. **Colab badge** as first markdown cell (REQUIRED)
2. **Setup cell** — fetches `utils.py` from GitHub raw URL on Colab, uses importlib reload

### Testing

`tests/test_notebooks.py` auto-discovers every `notebook.ipynb` under `exercises/*/`. For each one it:
1. Finds all cells with `exercise_id` metadata and all cells with `solution_id` metadata
2. Extracts the python code from each solution cell's ` ```python ``` ` block
3. Asserts every exercise has a matching solution
4. Swaps the solution code into the exercise cell
5. Executes the entire notebook
6. Fails if any cell errors or any output contains "FAIL"

No separate solutions file needed. The notebook is the single source of truth.

Run with: `uv run pytest tests/ -v`

### Adding a new exercise

1. Create `exercises/name/`
2. Author `notebook.ipynb` directly in Jupyter/Colab following the cell pattern above
3. Write `utils.py` with test functions that print PASS/FAIL
4. Tag exercise code cells with `exercise_id` and solution markdown cells with `solution_id` in cell metadata
5. Run `make update-links` to fix Colab badge and raw GitHub URLs
6. Verify: `uv run pytest tests/ -v` should pick it up automatically

## Key Rules

1. **Never modify `_fulltext.md` files** - Read-only source material
2. **Only write `slides.tex` when explicitly asked** - User writes notes, AI transforms to Beamer frames
3. **Put each sentence on a new line** in LaTeX files (improves diffs, invisible in PDF)
4. **Read existing slides before editing** to maintain context and consistency
5. **Verify citations** by reading the corresponding `bib/[key]/[key]_fulltext.md`
6. **Search literature** when answering questions about papers or verifying claims
7. **Notes are the source of truth** - slides should never contain information not in notes
8. **Never manually edit `bib/refs.bib`** - Auto-synced from Zotero. Use the Zotero skill to add papers.
9. **Avoid em-dashes (---)** - Use commas, parentheses, or separate sentences instead
10. **Use `[fragile]`** on frames with verbatim or code content
11. **Use `[allowframebreaks]`** on bibliography frames
12. **Keep frames concise** - Bullet points, not paragraphs
13. **New lectures**: Copy an existing lecture folder, update the title and Colab badge URL
14. **Notebooks must have the Colab badge** as the first markdown cell
15. **Shared metadata** lives in `lib/metadata.tex` - update there, not per-lecture
16. **Exercises are the main value prop** - Participants can read slides on their own
