"""Execute every exercise notebook with solutions injected, verify all tests pass.

For each notebook, finds cells tagged with exercise_id and solution_id metadata.
Extracts the code from the solution markdown cell's ```python block, swaps it into
the exercise code cell, then executes the entire notebook.

Notebooks importing transformer_lens are marked slow (they need model downloads + GPU).
Skip them with: SKIP_SLOW=1 uv run pytest tests/ -v
"""
import os
import re
from pathlib import Path

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parent.parent
LECTURES = ROOT / "lectures"
EXERCISES = ROOT / "exercises"

SLOW_TIMEOUT = 600
FAST_TIMEOUT = 120

SLOW_IMPORTS = {"transformer_lens", "circuitsvis"}


def discover_exercises():
    """Find all exercise notebooks across both directory structures."""
    results = []
    # lectures/*/exercises/*/notebook.ipynb (e.g. tangent)
    for nb_path in sorted(LECTURES.glob("*/exercises/*/notebook.ipynb")):
        d = nb_path.parent
        label = f"{d.parent.parent.name}/{d.name}"
        results.append((nb_path, label))
    # exercises/*/notebook*.ipynb (e.g. watermarking, logit_lens normal/hard)
    for nb_path in sorted(EXERCISES.glob("*/notebook*.ipynb")):
        d = nb_path.parent
        variant = nb_path.stem.replace("notebook_", "")
        label = f"{d.name}/{variant}"
        results.append((nb_path, label))
    return results


def extract_solutions(nb):
    """Extract solution code from markdown cells tagged with solution_id."""
    solutions = {}
    for cell in nb.cells:
        sid = cell.metadata.get("solution_id")
        if not sid:
            continue
        m = re.search(r"```python\n(.+?)```", cell.source, re.DOTALL)
        if m:
            solutions[sid] = m.group(1).strip()
    return solutions


def _is_slow(nb):
    """Check if any code cell imports a slow dependency."""
    for cell in nb.cells:
        if cell.cell_type == "code":
            for keyword in SLOW_IMPORTS:
                if keyword in cell.source:
                    return True
    return False


@pytest.mark.parametrize(
    "nb_path",
    [p for p, _ in discover_exercises()],
    ids=[n for _, n in discover_exercises()],
)
def test_notebook(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    solutions = extract_solutions(nb)

    exercise_ids = [
        cell.metadata["exercise_id"]
        for cell in nb.cells
        if cell.metadata.get("exercise_id")
    ]
    for eid in exercise_ids:
        assert eid in solutions, f"Exercise '{eid}' has no matching solution cell"

    for cell in nb.cells:
        eid = cell.metadata.get("exercise_id")
        if eid and eid in solutions:
            cell.source = solutions[eid]

    slow = _is_slow(nb)
    if slow and os.environ.get("SKIP_SLOW"):
        pytest.skip("Skipping slow notebook (SKIP_SLOW is set)")

    timeout = SLOW_TIMEOUT if slow else FAST_TIMEOUT
    ep = ExecutePreprocessor(timeout=timeout, kernel_name="python3")
    ep.preprocess(nb, resources={"metadata": {"path": str(nb_path.parent)}})

    for i, cell in enumerate(nb.cells):
        for output in cell.get("outputs", []):
            text = output.get("text", "")
            if isinstance(text, list):
                text = "".join(text)
            if "FAIL" in text:
                pytest.fail(f"Cell {i} output contains FAIL:\n{text}")
