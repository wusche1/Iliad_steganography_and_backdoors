#!/usr/bin/env python3
"""Extract figures and tables from PDF papers using Docling.

Runs as part of the sync pipeline. Only processes papers that have a PDF
but no figures/ directory yet.
"""

import re
import base64
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions


def _extract_html_figures(html_path, figures_dir):
    """Extract base64-encoded images from an HTML file."""
    html = html_path.read_text(errors='ignore')
    # Match both data:image/PNG and data:binary/octet-stream (used by some sites)
    matches = re.findall(
        r'data:(?:image/(?:PNG|png|jpeg|jpg)|binary/octet-stream);base64,([A-Za-z0-9+/=\s]+)',
        html
    )
    for i, data in enumerate(matches):
        data = data.replace('\n', '').replace(' ', '')
        img_bytes = base64.b64decode(data)
        # Detect format from magic bytes
        ext = 'png' if img_bytes[:4] == b'\x89PNG' else 'jpg'
        (figures_dir / f"fig{i}.{ext}").write_bytes(img_bytes)
    print(f"    {len(matches)} figures extracted from HTML")


_converter = None


def _get_converter():
    global _converter
    if _converter is None:
        pipeline_options = PdfPipelineOptions(
            images_scale=3.0,
            generate_picture_images=True,
            generate_table_images=True,
        )
        _converter = DocumentConverter(
            format_options={"pdf": PdfFormatOption(pipeline_options=pipeline_options)}
        )
    return _converter


def extract_figures(config):
    bib_dir = Path(config.get('output_dir', 'bib'))
    if not bib_dir.is_absolute():
        bib_dir = Path(__file__).parent.parent.parent / bib_dir

    for paper_dir in sorted(bib_dir.iterdir()):
        if not paper_dir.is_dir():
            continue

        figures_dir = paper_dir / "figures"
        if figures_dir.exists():
            continue

        pdf = paper_dir / f"{paper_dir.name}.pdf"
        html = paper_dir / f"{paper_dir.name}.html"

        if not pdf.exists() and not html.exists():
            continue

        print(f"  Extracting figures from {paper_dir.name}...")
        figures_dir.mkdir()

        # HTML-only papers: extract base64 images directly
        if not pdf.exists() and html.exists():
            try:
                _extract_html_figures(html, figures_dir)
            except Exception as e:
                print(f"    Error extracting HTML figures: {e}")
            continue

        try:
            converter = _get_converter()
            result = converter.convert(str(pdf))

            for i, element in enumerate(result.document.pictures):
                img = element.get_image(result.document)
                if img:
                    img.save(str(figures_dir / f"fig{i}.png"))
                    caption = element.caption_text(result.document) if hasattr(element, 'caption_text') else ""
                    if caption:
                        (figures_dir / f"fig{i}-caption.txt").write_text(caption)

            for i, element in enumerate(result.document.tables):
                img = element.get_image(result.document)
                if img:
                    img.save(str(figures_dir / f"table{i}.png"))
                    caption = element.caption_text(result.document) if hasattr(element, 'caption_text') else ""
                    if caption:
                        (figures_dir / f"table{i}-caption.txt").write_text(caption)

            n = len(result.document.pictures) + len(result.document.tables)
            print(f"    {n} figures/tables extracted")
        except Exception as e:
            print(f"    Error: {e}")
