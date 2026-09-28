#!/usr/bin/env python3
import re
from pathlib import Path
from datetime import datetime
import yaml


def _extract_refs_bib_keys(refs_content):
    """Extract all citation keys already present in refs.bib"""
    return set(re.findall(r'^@\w+\{(.+),$', refs_content, re.MULTILINE))


def _generate_metadata_entries(bib_dir, existing_keys):
    """Generate BibTeX entries from .metadata.txt for papers not yet in refs.bib.

    This bridges the gap between the daemon detecting a new Zotero paper
    and Better BibTeX exporting it to refs.bib.
    """
    entries = []
    for metadata_file in bib_dir.glob('*/.metadata.txt'):
        citation_key = metadata_file.parent.name
        if citation_key in existing_keys:
            continue
        meta = {}
        for line in metadata_file.read_text().splitlines():
            if ': ' in line:
                k, v = line.split(': ', 1)
                meta[k.strip()] = v.strip()
        title = meta.get('Title', citation_key)
        author = meta.get('Author', 'Unknown')
        year = meta.get('Year', '')
        entry = f"@misc{{{citation_key},\n"
        entry += f"  title = {{{title}}},\n"
        entry += f"  author = {{{author}}},\n"
        entry += f"  year = {{{year}}}\n"
        entry += "}\n"
        entries.append(entry)
    return entries


def _find_named_figures(bib_dir):
    """Find user-named figures (not auto-extracted fig0, table0, etc.)."""
    auto_pattern = re.compile(r'^(fig|table)\d+')
    figures = []
    for fig_file in bib_dir.glob('*/figures/*.png'):
        name = fig_file.stem
        if not auto_pattern.match(name) and not name.endswith('_caption'):
            citation_key = fig_file.parent.parent.name
            figures.append((citation_key, name))
    for fig_file in bib_dir.glob('*/figures/*.jpg'):
        name = fig_file.stem
        if not auto_pattern.match(name) and not name.endswith('_caption'):
            citation_key = fig_file.parent.parent.name
            figures.append((citation_key, name))
    return sorted(figures)


def sync_labels(config):
    """Extract all LaTeX labels and combine with refs.bib into a single file"""
    # Get project root (go up two levels from scripts/syncing/)
    project_root = Path(__file__).parent.parent.parent

    # Get bib directory from config
    bib_dir = Path(config.get('output_dir', 'bib'))
    if not bib_dir.is_absolute():
        bib_dir = project_root / bib_dir

    # First, read the existing refs.bib content
    refs_bib_path = bib_dir / "refs.bib"
    refs_content = ""
    if refs_bib_path.exists():
        refs_content = refs_bib_path.read_text()

    # Generate entries for papers the daemon found but BBT hasn't exported yet
    existing_keys = _extract_refs_bib_keys(refs_content)
    metadata_entries = _generate_metadata_entries(bib_dir, existing_keys)

    # Find all .tex files in the project
    tex_files = list(project_root.rglob('*.tex'))

    # Extract all \label{...} commands
    all_labels = []
    for tex_file in tex_files:
        try:
            content = tex_file.read_text()
            labels = re.findall(r'\\label\{([^}]+)\}', content)
            all_labels.extend(labels)
        except:
            pass

    # Remove duplicates and sort
    all_labels = sorted(set(all_labels))

    # Get output file from config
    output_path = config.get('label_extraction', {}).get('output_file', 'bib/labels.bib')
    if output_path.endswith('.json'):
        output_path = output_path.replace('.json', '.bib')

    # Handle both absolute and relative paths
    output_file = Path(output_path)
    if not output_file.is_absolute():
        output_file = project_root / output_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Start with the refs.bib content
    bib_content = refs_content

    # Add entries from metadata (papers not yet in refs.bib)
    if metadata_entries:
        bib_content += f"\n\n% ===== PENDING BBT EXPORT (from Zotero metadata) =====\n"
        bib_content += f"% These entries will be replaced once Better BibTeX exports them\n\n"
        bib_content += "\n".join(metadata_entries)

    # Add separator and label entries
    bib_content += f"\n\n% ===== AUTO-GENERATED LATEX LABELS =====\n"
    bib_content += f"% Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    bib_content += f"% Total labels: {len(all_labels)}\n\n"

    for label in all_labels:
        bib_content += f"@misc{{{label},\n"
        bib_content += f"  title = {{LaTeX Label: {label}}},\n"
        bib_content += f"  note = {{Internal cross-reference}},\n"
        bib_content += f"  keywords = {{label}},\n"
        bib_content += f"  year = {{9999}}\n"
        bib_content += f"}}\n\n"

    # Add named figure entries
    named_figures = _find_named_figures(bib_dir)
    if named_figures:
        bib_content += f"\n% ===== NAMED FIGURES =====\n"
        bib_content += f"% Captured via figure-capture hotkey\n\n"
        for citation_key, fig_name in named_figures:
            ref = f"{citation_key}/{fig_name}"
            bib_content += f"@misc{{{ref},\n"
            bib_content += f"  title = {{Figure: {fig_name} ({citation_key})}},\n"
            bib_content += f"  keywords = {{figure}},\n"
            bib_content += f"  year = {{9999}}\n"
            bib_content += f"}}\n\n"

    # Save to .bib file
    with open(output_file, 'w') as f:
        f.write(bib_content)

    n_pending = len(metadata_entries)
    n_figures = len(named_figures)
    pending_msg = f" + {n_pending} pending" if n_pending else ""
    figures_msg = f" + {n_figures} figures" if n_figures else ""
    print(f"Combined {refs_bib_path.name}{pending_msg} + {len(all_labels)} labels{figures_msg} -> {output_path}")


def main():
    """Main entry point for standalone testing"""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f'=== Label Sync (Standalone) ===')
    sync_labels(config)


if __name__ == '__main__':
    main() 