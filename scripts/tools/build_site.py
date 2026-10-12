import gzip
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LECTURES = ROOT / "lectures"
OUT = ROOT / "site" / "data"

CITE_RE = re.compile(r"\\(?:source|cite|textcite|parencite|fullcite|fullfig\{[^}]*\})\{([^}]*)\}")
FIG_RE = re.compile(r"figures/([^/}]+)/[^}]+\.(?:png|jpg|jpeg|pdf)")


def parse_frames(path):
    lines = path.read_text().splitlines()
    frames, start = [], None
    for i, line in enumerate(lines, 1):
        if r"\begin{frame}" in line and start is None:
            start = i
        elif r"\end{frame}" in line and start is not None:
            src = "\n".join(lines[start - 1:i])
            m = re.search(r"\\begin\{frame\}(?:\[[^\]]*\])?\{([^}]*)\}", src) or re.search(r"\\frametitle\{([^}]*)\}", src)
            frames.append({"start": start, "end": i, "title": m.group(1) if m else "", "source": src})
            start = None
    return frames


def page_lines(lecture):
    """Map each PDF page to a Counter of (input file, line) records from synctex."""
    inputs, pages, page = {}, {}, None
    with gzip.open(lecture / "output" / "main.synctex.gz", "rt") as f:
        for line in f:
            if line.startswith("Input:"):
                _, tag, path = line.rstrip().split(":", 2)
                inputs[tag] = Path(path).resolve()
            elif line.startswith("{"):
                page = int(line[1:])
                pages[page] = Counter()
            elif page and (m := re.match(r"[\[\(hvxkg$r](\d+),(\d+):", line)):
                pages[page][(inputs[m.group(1)], int(m.group(2)))] += 1
    return pages


def page_text(pdf, n):
    return subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), str(pdf), "-"],
                          capture_output=True, text=True).stdout.strip()


def build_slides(lecture, papers):
    chapters = {p.resolve(): (p.parent.name, parse_frames(p)) for p in sorted(LECTURES.glob("*/*/slides.tex"))}
    slides = []
    for n, counts in sorted(page_lines(lecture).items()):
        votes = Counter()
        for (path, line), c in counts.items():
            if path in chapters:
                for fi, fr in enumerate(chapters[path][1]):
                    if fr["start"] <= line <= fr["end"]:
                        votes[(path, fi)] += c
        slide = {"page": n, "text": page_text(lecture / "output" / "main.pdf", n)}
        if votes:
            path, fi = votes.most_common(1)[0][0]
            fr = chapters[path][1][fi]
            refs = set(CITE_RE.findall(fr["source"])) | set(FIG_RE.findall(fr["source"]))
            refs = {k.strip() for r in refs for k in r.split(",")}
            slide |= {"chapter": chapters[path][0], "title": fr["title"], "file": str(path.relative_to(ROOT)),
                      "lines": [fr["start"], fr["end"]], "source": fr["source"], "refs": sorted(refs & papers.keys())}
        else:
            slide["title"] = slide["text"].splitlines()[0].strip() if slide["text"] else ""
        slides.append(slide)
    return slides


def build_papers():
    papers = {}
    for meta in sorted((ROOT / "bib").glob("*/.metadata.txt")):
        d = meta.parent
        fields = dict(re.findall(r"^(\w[\w ]*): (.*)$", meta.read_text(), re.M))
        fulltext = d / f"{d.name}_fulltext.md"
        papers[d.name] = {
            "key": d.name, "title": fields.get("Title", ""), "author": fields.get("Author", ""),
            "year": fields.get("Year", ""), "url": fields.get("URL", ""), "abstract": fields.get("Abstract", ""),
            "fulltext": fulltext.exists(), "chars": fulltext.stat().st_size if fulltext.exists() else 0,
            "figures": sorted(p.stem for p in (d / "figures").glob("*.png")),
        }
    return papers


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    papers = build_papers()
    lectures = [LECTURES / name for name in sys.argv[1:]]
    (OUT / "papers.json").write_text(json.dumps(list(papers.values()), indent=1))
    (OUT / "lectures.json").write_text(json.dumps([d.name for d in lectures]))
    for d in lectures:
        slides = build_slides(d, papers)
        (OUT / f"{d.name}.json").write_text(json.dumps(slides, indent=1))
        print(f"{d.name}: {len(slides)} slides, {len(papers)} papers -> {OUT}")
