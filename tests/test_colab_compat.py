"""Test that exercise notebooks install and import correctly in a Colab-like environment.

Creates a Python 3.12 venv, pre-installs Colab's conflict-prone packages at their
exact pinned versions (fetched from googlecolab/backend-info), then runs the
notebook's pip install line and tests imports.

Run with: uv run pytest tests/test_colab_compat.py -v
Skip with: SKIP_SLOW=1 uv run pytest tests/ -v
"""
import os
import re
import shlex
import subprocess
from pathlib import Path

import nbformat
import pytest
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
EXERCISES = ROOT / "exercises"

COLAB_FREEZE_URL = (
    "https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.gpu.txt"
)

# Packages pre-installed in Colab that conflict with transformer_lens installs.
COLAB_RELEVANT = {"numpy", "numba", "transformers", "torch", "einops", "plotly", "matplotlib", "ipython"}


def _fetch_colab_pins():
    """Fetch exact versions of relevant packages from Colab's published freeze."""
    resp = urllib.request.urlopen(COLAB_FREEZE_URL, timeout=10)
    pins = {}
    for line in resp.read().decode().splitlines():
        m = re.match(r"^([a-zA-Z0-9_-]+)==(.+)$", line.strip())
        if not m:
            continue
        pkg = m.group(1).lower().replace("-", "_")
        if pkg in COLAB_RELEVANT:
            # Strip CUDA build tags (+cu128) — unavailable on PyPI for macOS
            pins[m.group(1)] = re.sub(r"\+.*$", "", m.group(2))
    return pins


def _extract_pip_and_imports(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    pip_line = None
    import_src = None
    for cell in nb["cells"]:
        if cell.cell_type != "code":
            continue
        src = cell.source
        if "%pip install" in src:
            m = re.search(r"%pip install (.+)", src)
            if m:
                pip_line = m.group(1)
        elif pip_line and import_src is None and ("import torch" in src or "from transformer_lens" in src):
            import_src = src
    return pip_line, import_src


def _find_python_312():
    for cmd in ["python3.12"]:
        try:
            r = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and "3.12" in r.stdout:
                return cmd
        except FileNotFoundError:
            pass
    try:
        r = subprocess.run(["uv", "python", "find", "3.12"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return r.stdout.strip()
    except FileNotFoundError:
        pass
    pytest.skip("Python 3.12 not available")


def discover():
    results = []
    for nb_path in sorted(EXERCISES.glob("*/notebook_*.ipynb")):
        pip_line, import_src = _extract_pip_and_imports(nb_path)
        if pip_line and import_src:
            variant = nb_path.stem.replace("notebook_", "")
            label = f"{nb_path.parent.name}/{variant}"
            results.append((nb_path, pip_line, import_src, label))
    return results


_notebooks = discover()


@pytest.fixture(scope="session")
def colab_pins():
    return _fetch_colab_pins()


@pytest.mark.parametrize(
    "nb_path,pip_line,import_src",
    [(p, pip, imp) for p, pip, imp, _ in _notebooks],
    ids=[label for _, _, _, label in _notebooks],
)
def test_colab_install_and_import(nb_path, pip_line, import_src, colab_pins, tmp_path):
    if os.environ.get("SKIP_SLOW"):
        pytest.skip("SKIP_SLOW is set")

    python = _find_python_312()
    venv = tmp_path / "venv"
    subprocess.run([python, "-m", "venv", str(venv)], check=True, timeout=30)
    pip_bin = str(venv / "bin" / "pip")
    py_bin = str(venv / "bin" / "python")

    # Step 1: install Colab's pinned packages
    pins = [f"{pkg}=={ver}" for pkg, ver in colab_pins.items()]
    r = subprocess.run([pip_bin, "install", "-q"] + pins, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"Colab baseline install failed:\n{r.stderr}"

    # Step 2: run the notebook's pip install
    args = shlex.split(pip_line.replace("-q", "").strip())
    r = subprocess.run([pip_bin, "install"] + args, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"Notebook pip install failed:\n{r.stderr}"

    # Step 3: verify numpy wasn't downgraded (the root cause of all Colab issues)
    r = subprocess.run([py_bin, "-c", "import numpy; print(numpy.__version__)"], capture_output=True, text=True, timeout=10)
    numpy_ver = r.stdout.strip()
    assert numpy_ver == colab_pins.get("numpy", ""), f"numpy was changed to {numpy_ver} (Colab has {colab_pins.get('numpy')})"

    # Step 4: test imports
    r = subprocess.run([py_bin, "-c", import_src], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"
