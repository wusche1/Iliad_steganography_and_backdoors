#!/usr/bin/env python3
"""Extract figures and tables from a PDF paper using Docling's layout analysis.

Usage:
    uv run python scripts/tools/extract_figures.py <citation_key> [output_dir]

Extracts to bib/<key>/figures/ by default. Each figure/table gets a PNG and a
caption .txt file. Output structure:
    fig0.png, fig0-caption.txt
    table0.png, table0-caption.txt
"""

import sys
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions


def extract_figures(citation_key: str, output_dir: str | None = None, scale: float = 3.0):
    project_root = Path(__file__).parent.parent.parent
    pdf_path = project_root / "bib" / citation_key / f"{citation_key}.pdf"

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        sys.exit(1)

    out = Path(output_dir) if output_dir else project_root / "bib" / citation_key / "figures"
    out.mkdir(parents=True, exist_ok=True)

    pipeline_options = PdfPipelineOptions(
        images_scale=scale,
        generate_picture_images=True,
        generate_table_images=True,
    )
    converter = DocumentConverter(
        format_options={"pdf": PdfFormatOption(pipeline_options=pipeline_options)}
    )

    print(f"Extracting from {pdf_path.name}...")
    result = converter.convert(str(pdf_path))

    for i, element in enumerate(result.document.pictures):
        img = element.get_image(result.document)
        if img:
            img.save(str(out / f"fig{i}.png"))
            caption = element.caption_text(result.document) if hasattr(element, 'caption_text') else ""
            if caption:
                (out / f"fig{i}-caption.txt").write_text(caption)
            print(f"  fig{i}.png: {img.size}  {caption[:80] if caption else '(no caption)'}")

    for i, element in enumerate(result.document.tables):
        img = element.get_image(result.document)
        if img:
            img.save(str(out / f"table{i}.png"))
            caption = element.caption_text(result.document) if hasattr(element, 'caption_text') else ""
            if caption:
                (out / f"table{i}-caption.txt").write_text(caption)
            print(f"  table{i}.png: {img.size}  {caption[:80] if caption else '(no caption)'}")

    n_pics = len(result.document.pictures)
    n_tables = len(result.document.tables)
    print(f"Extracted {n_pics} figures + {n_tables} tables to {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    citation_key = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    extract_figures(citation_key, output_dir)
