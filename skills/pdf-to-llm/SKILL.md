---
name: pdf-to-llm
description: Convert a PDF into clean, LLM-digestible Markdown with as little context loss as possible. Extracts text, tables, layout and images locally with opendataloader-pdf, then uses Claude vision to describe every figure, diagram, chart, plot, and in-image table inline. Use whenever the user wants to convert, parse, ingest, or "make LLM-readable" a PDF into Markdown — especially PDFs containing images, diagrams, plots, slides, or scanned content — for use as LLM context, RAG, or notes.
---

# PDF → LLM-digestible Markdown

Convert a PDF into a single self-contained Markdown file that an LLM can fully
understand **without needing the original images**. The hard part of most PDFs is
that the real content lives inside figures (block diagrams, plots, spectrograms,
tables rendered as images). Raw text extractors drop all of that. This skill
solves it in two stages:

1. **Deterministic extraction** (local, fast) — `opendataloader-pdf` pulls out the
   text, tables, layout, reading order, and saves every embedded image as a file.
2. **Vision enrichment** (you, Claude) — read every extracted image and write a
   detailed inline description / transcription, so no visual context is lost.

## Prerequisites

- **Python 3.9+** on PATH (used to create an isolated venv on first run).
- **Java 11+** on PATH — `opendataloader-pdf` is Java-backed. If `java` is missing,
  the helper script stops with a clear message; install Temurin/Adoptium or
  Microsoft OpenJDK and retry.
- First run installs `opendataloader-pdf` into a private venv at
  `~/.pdf-to-llm/venv`. It does **not** touch the user's global Python packages.

## Workflow

### Step 1 — Extract (run the helper script)

Run the bundled script with the system Python. It manages the venv and runs the
local conversion:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/convert_pdf.py" "<absolute/path/to/input.pdf>" ["<output_dir>"]
```

- On Windows use `python`; on macOS/Linux use `python3` if needed.
- `${CLAUDE_PLUGIN_ROOT}` is set by Claude Code to this plugin's install directory.
- If `<output_dir>` is omitted it defaults to `<pdf_dir>/<pdf_stem>_odl`.
- The script prints a JSON summary: the raw `markdown` path, the `output_dir`, and
  the list of extracted `images`.

### Step 2 — Read the raw extraction

Read the raw `.md` produced by Step 1. It gives you the document's text, headings,
reading order, and `![...](images/...)` references — your scaffold for the final file.

### Step 3 — Vision enrichment (the important part)

Read **every** extracted image with the Read tool (it renders images visually).
Batch the reads in parallel for speed. For each image, write a description sized to
its information content — aim for **zero context loss**:

- **Block / flow / architecture diagrams** → describe every box, label, and the
  arrows/connections between them, in order. Reproduce the logical flow as text
  (and as a Markdown list or table when that captures it faithfully).
- **Plots / charts / graphs** → state the chart type, axis labels and ranges, each
  series (with legend colors), the trend/shape, and any printed numeric values,
  peaks, or annotations. Transcribe callout numbers exactly.
- **Tables rendered as images** → transcribe fully into a real Markdown table.
- **Spectrograms / heatmaps / waterfalls** → describe axes, color scale, and where
  the notable features (bright stripes, bursts, gaps) sit.
- **Photographs** → one to three sentences on what they show and why they're there.
- **Decorative-only images** (logos, background banners, bullets) → a short note or
  skip; don't waste effort.

Preserve any text the extractor already captured (captions, equations, references) —
don't discard it; weave it together with your image descriptions.

### Step 4 — Assemble the final file

Write `<pdf_stem>_llm.md` next to the original PDF (or in the user's requested
location). Rules:

- Follow the document's original reading order and heading structure.
- Replace each `![image](...)` reference with a clearly marked description block,
  e.g. a blockquote starting with `> **[Figure: short title]**` followed by the
  detailed description. (Optionally keep the relative image link after it so the
  file stays traceable to the source images.)
- Keep real Markdown tables for tabular data.
- Add a short **Summary** section at the end capturing the document's key points —
  helpful as a quick LLM primer.
- Use only standard Markdown so it pastes cleanly into any chat or RAG pipeline.

### Step 5 — Report

Tell the user the path to the final `_llm.md`, its size, how many figures were
described, and note that the file is self-contained (no images required to
understand it).

## Modes

- **Default (enriched):** do all steps. Best for slides, technical docs, anything
  diagram-heavy.
- **Text-only (fast):** if the user explicitly wants a quick pass or the PDF is
  pure prose with no meaningful figures, stop after Step 2 and hand them the raw
  extraction (still better-structured than most extractors). Mention that figures
  weren't described.

## Notes & troubleshooting

- The extractor is fully local — nothing is uploaded.
- Scanned / image-only PDFs: opendataloader-pdf can OCR, but the most reliable path
  here is still Step 3 — your vision reading of the page images.
- Very large PDFs (many images): read images in parallel batches; if the document is
  huge, process it in sections and concatenate.
- If extraction misses a page's content but an image of that page exists, fall back
  to describing the page image directly.
- The first run is slower (venv creation + package install + Java font cache). Later
  runs are fast.
