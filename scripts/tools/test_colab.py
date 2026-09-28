"""Test exercise notebooks on actual Google Colab using Playwright.

Opens each notebook in Colab, runs all cells, and checks for errors.
Requires one-time manual Google login (cookies are saved for future runs).

Usage:
    uv run python scripts/tools/test_colab.py                    # test all notebooks
    uv run python scripts/tools/test_colab.py 01_logit_lens hard # test one specific notebook
"""
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
EXERCISES = ROOT / "exercises"
PROFILE_DIR = ROOT / ".cache" / "playwright-colab-profile"

REPO = "wusche1/Iliad_steganography_and_backdoors"
BRANCH = "main"
MAX_WAIT = 240  # seconds to wait for cell execution


def colab_url(exercise_dir, variant):
    return (
        f"https://colab.research.google.com/github/{REPO}/blob/{BRANCH}"
        f"/exercises/{exercise_dir}/notebook_{variant}.ipynb"
    )


def discover_notebooks():
    results = []
    for nb_path in sorted(EXERCISES.glob("*/notebook_*.ipynb")):
        exercise_dir = nb_path.parent.name
        variant = nb_path.stem.replace("notebook_", "")
        results.append((exercise_dir, variant))
    return results


def dismiss_dialogs(page):
    for text in ["Dismiss", "OK", "Got it", "Close", "Run anyway", "Cancel", "Verstanden"]:
        try:
            page.click(f'button:has-text("{text}")', timeout=500)
        except Exception:
            pass


def test_notebook(context, exercise_dir, variant):
    url = colab_url(exercise_dir, variant)
    label = f"{exercise_dir}/{variant}"
    print(f"\n{'='*60}")
    print(f"Testing: {label}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    page = context.new_page()
    page.goto(url, timeout=60000, wait_until="networkidle")
    page.wait_for_timeout(5000)
    dismiss_dialogs(page)

    # Check for sign-in requirement
    if "sign-in" in page.content().lower():
        print("Google sign-in required. Please log in in the browser window.")
        print("Waiting up to 120s for login...")
        for _ in range(24):
            page.wait_for_timeout(5000)
            if "sign-in" not in page.content().lower():
                print("Logged in!")
                break
        else:
            print("FAIL: Could not log in within 120s")
            page.close()
            return False

    dismiss_dialogs(page)

    # Trigger "Run all"
    print("Running all cells...")
    try:
        page.click('#runtime-menu-button', timeout=5000)
        page.wait_for_timeout(500)
        page.click('text=Run all', timeout=5000)
    except Exception:
        page.keyboard.press("Control+F9")

    page.wait_for_timeout(2000)
    dismiss_dialogs(page)

    # Wait for execution
    error_found = False
    success = False
    for i in range(MAX_WAIT // 10):
        page.wait_for_timeout(10000)
        dismiss_dialogs(page)
        elapsed = (i + 1) * 10

        content = page.content()

        # Check for Python errors
        for err_type in ["ValueError", "ModuleNotFoundError", "ImportError", "AttributeError"]:
            if err_type in content:
                print(f"  [{elapsed}s] ERROR: {err_type} detected!")
                page.screenshot(path=f"/tmp/colab_error_{exercise_dir}_{variant}.png", full_page=True)
                error_found = True
                break

        if error_found:
            break

        if "PASS" in content and "FAIL" not in content:
            print(f"  [{elapsed}s] All tests PASS!")
            success = True
            break

        if "FAIL" in content:
            print(f"  [{elapsed}s] Test FAIL detected!")
            error_found = True
            break

        # Progress indicators
        if "Installing collected packages" in content or "Downloading" in content:
            print(f"  [{elapsed}s] Installing packages...")
        elif "Loaded pretrained model" in content:
            print(f"  [{elapsed}s] Model loaded...")
        else:
            print(f"  [{elapsed}s] Waiting...")

    page.screenshot(path=f"/tmp/colab_final_{exercise_dir}_{variant}.png", full_page=True)

    if error_found:
        print(f"RESULT: {label} FAILED")
    elif success:
        print(f"RESULT: {label} PASSED")
    else:
        print(f"RESULT: {label} TIMEOUT (check /tmp/colab_final_{exercise_dir}_{variant}.png)")

    page.close()
    return success and not error_found


def main():
    notebooks = discover_notebooks()

    # Filter if args provided
    if len(sys.argv) > 1:
        exercise_filter = sys.argv[1]
        variant_filter = sys.argv[2] if len(sys.argv) > 2 else None
        notebooks = [
            (d, v) for d, v in notebooks
            if exercise_filter in d and (variant_filter is None or v == variant_filter)
        ]

    if not notebooks:
        print("No notebooks found matching filter")
        sys.exit(1)

    print(f"Will test {len(notebooks)} notebook(s):")
    for d, v in notebooks:
        print(f"  {d}/{v}")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 900},
        )

        results = {}
        for exercise_dir, variant in notebooks:
            results[f"{exercise_dir}/{variant}"] = test_notebook(context, exercise_dir, variant)

        context.close()

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    all_pass = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_pass = False

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
