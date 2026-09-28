---
name: literature
description: Search the project's literature collection using RAG. Use when the user asks about their papers, wants to find sources, or needs to verify claims.
allowed-tools: Bash
---

# Literature Search

Search across all papers in the bibliography using RAG (Retrieval Augmented Generation) with semantic embeddings.

## When to Use

- User asks "Is there anything about X in my papers?"
- User asks "What do my sources say about Y?"
- User asks to find or verify a citation
- User asks "Find information about Z in the literature"
- You need to check what papers say before writing or editing a chapter

## RAG Search (default)

Returns chapter previews, abstracts, and relevance scores.

```bash
uv run python scripts/tools/rag.py "search query"
uv run python scripts/tools/rag.py "search query" 10  # custom number of results
```

## Quick Search

Returns just paper names, chapter names, and file paths (faster, less output).

```bash
uv run python scripts/tools/search_bib.py "search query"
uv run python scripts/tools/search_bib.py "search query" 10
```

## Workflow

1. Run a RAG search with appropriate terms
2. Review the returned chapters and abstracts
3. If the preview is insufficient, read the full chapter: `bib/[paper]/chapters/[chapter].md`
4. Explore related sections of the same paper if relevant
5. Always cite the exact paper and chapter when reporting findings

## Reading Full Papers

After finding relevant results, you can read the complete source material:

- Full paper text: `bib/[citation_key]/[citation_key]_fulltext.md`
- Individual chapters: `bib/[citation_key]/chapters/[chapter_name].md`
- Paper metadata/abstract: `bib/[citation_key]/.metadata.txt`
