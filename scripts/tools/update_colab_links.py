"""Update Colab badge and raw GitHub URLs in all lecture notebooks based on git remote and branch."""

import json
import re
import subprocess
from pathlib import Path

RAW_GH = "https://raw.githubusercontent.com"
COLAB = "https://colab.research.google.com"


def get_repo_info():
    remote = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode().strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()
    match = re.search(r"[:/]([^/]+)/([^/.]+?)(?:\.git)?$", remote)
    return match.group(1), match.group(2), branch


def update_notebook(path, user, repo, branch):
    raw = path.read_text()
    lecture_dir = str(path.parent)

    # Update Colab badge URLs
    colab_url = f"{COLAB}/github/{user}/{repo}/blob/{branch}/{path}"
    badge = f"[![Open In Colab]({COLAB}/assets/colab-badge.svg)]({colab_url})"
    new = re.sub(r"\[!\[Open In Colab\]\(.*?\)\]\(.*?\)", badge, raw)

    # Update raw.githubusercontent.com URLs (for utils.py downloads etc.)
    new = re.sub(
        rf"{RAW_GH}/[^/]+/[^/]+/[^/]+/{re.escape(lecture_dir)}/",
        f"{RAW_GH}/{user}/{repo}/{branch}/{lecture_dir}/",
        new,
    )

    if new == raw:
        print(f"Already up to date: {path}")
    else:
        path.write_text(new)
        print(f"Updated: {path}")


if __name__ == "__main__":
    user, repo, branch = get_repo_info()
    print(f"Repo: {user}/{repo} Branch: {branch}")
    for nb_path in sorted(Path("exercises").rglob("notebook*.ipynb")):
        update_notebook(nb_path, user, repo, branch)
