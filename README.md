# pdf-to-llm

**Turn any PDF into Markdown an LLM can actually understand — including the figures.**

A Claude Code plugin that converts PDFs to clean, self-contained Markdown with
minimal context loss. Unlike plain text extractors, it doesn't just skip the
diagrams, plots, and tables-as-images that hold most of a technical document's
meaning — it *describes them inline* using Claude's vision.

---

## The problem

Most PDF→Markdown tools extract the text and leave you with this:

```markdown
### uGMRT RFI Filtering System: Development Flow
![](_page_7_Figure_1.jpeg)
```

An LLM reading that learns nothing from the figure — and in slide decks or
technical papers, **the figures are the content**. The actual development pipeline,
the axis values on a plot, the rows of a table rendered as an image: all lost.

## The fix

`pdf-to-llm` runs in two stages and produces this instead:

```markdown
### uGMRT RFI Filtering System: Development Flow

> **[Figure: Development pipeline + before/after results]**
> Four-stage flow connected by ↔ arrows:
> 1. **Development** — Algorithm Selection, Simulation, Implementation, Optimization
> 2. **Testing** — Module Level, Engineering Tests, Controlled Tests
> 3. **Field Trials** — Simultaneous Testing, Astronomical tests
> 4. **Release** — Recommended settings, Book-keeping, Feature Addition
>
> Below: an unfiltered vs. filtered timeseries (~9000 samples) showing impulsive
> RFI spikes removed, and a clean radio image of the released system.
```

The result is a single `<name>_llm.md` that is fully understandable **without the
original images** — ready to paste into a chat, drop into a RAG pipeline, or keep
as notes.

---

## How it works

| Stage | What runs | What it does |
|------|-----------|--------------|
| **1. Extract** | [`opendataloader-pdf`](https://github.com/opendataloader-project/opendataloader-pdf) (local, offline) | Pulls out text, tables, layout, reading order, and saves every embedded image as a file. |
| **2. Enrich** | Claude vision (your session's own model — no API key) | Reads every extracted image and writes a detailed inline description / transcription — diagrams → flow, plots → axes & values, image-tables → real Markdown tables, photos → captions. |

Stage 1 is deterministic and never leaves your machine. Stage 2 is where the
context that other tools drop gets recovered.

> ### No API key. No local AI model.
>
> The vision in Stage 2 is performed by **the same Claude model already running your
> chat or Claude Code session** — the plugin just instructs it to read and describe
> each image. There is **nothing extra to set up**:
>
> - ❌ No `ANTHROPIC_API_KEY` or any other API key
> - ❌ No local ML model, GPU, OCR engine, or multi-gigabyte download
> - ✅ Just uses the Claude you're already talking to
>
> The only local dependency is the lightweight `opendataloader-pdf` extractor
> (Stage 1), which auto-installs into an isolated venv on first run.
>
> *(Caveat: running `scripts/convert_pdf.py` directly — outside of Claude — performs
> only Stage 1 extraction. The figure descriptions require a Claude agent to drive
> them, which is exactly what happens when you use the `/pdf2md` command or the skill.)*

---

## Install

On any machine with Claude Code:

```
/plugin marketplace add Saptarshi-Nag189/pdf-to-llm-plugin
/plugin install pdf-to-llm@saptarshi-tools
```

> Requires **Python 3.9+** and **Java 11+** on PATH (opendataloader-pdf is
> Java-backed — e.g. [Temurin/Adoptium](https://adoptium.net) or Microsoft OpenJDK).
> On first run the plugin builds an isolated venv at `~/.pdf-to-llm/venv` and
> installs `opendataloader-pdf` into it. **Your global Python packages are never
> touched.**

---

## Usage

**Slash command:**

```
/pdf2md "C:\path\to\file.pdf"
/pdf2md "C:\path\to\file.pdf" "C:\path\to\output_dir"
```

**Or just ask Claude in plain language:**

> "Convert this PDF to Markdown for an LLM: /path/to/file.pdf"

The `pdf-to-llm` skill is picked up automatically.

**Output:** `<pdf_name>_llm.md` next to the source PDF (or in the directory you
specify), plus a folder of the raw extracted images for traceability.

### Modes

- **Enriched (default):** full two-stage conversion. Best for slides, technical
  papers, anything with diagrams, plots, or scanned tables.
- **Text-only (fast):** ask for "text only" or "quick" and it stops after extraction
  — still better-structured than most extractors, but figures aren't described.

---

## Why this over `marker` / plain extractors?

- In testing, `opendataloader-pdf` pulled **~2× more raw text** than `marker` and
  preserved table structure (captions, author credits, command listings, bullet
  hierarchies that `marker` dropped).
- But **no** pure extractor — marker, opendataloader, pdfplumber — can read content
  trapped inside a figure. The Stage 2 vision pass is the differentiator that makes
  the output genuinely LLM-ready.

---

## Repository layout

```
pdf-to-llm-plugin/
├── .claude-plugin/
│   ├── plugin.json         # plugin manifest
│   └── marketplace.json    # marketplace manifest (repo is directly installable)
├── commands/
│   └── pdf2md.md           # the /pdf2md slash command
├── skills/
│   └── pdf-to-llm/
│       └── SKILL.md        # skill definition + full workflow
└── scripts/
    └── convert_pdf.py      # manages the isolated venv + runs local extraction
```

---

## Troubleshooting

| Symptom | Fix |
|--------|-----|
| `Java runtime not found` | Install Java 11+ and ensure `java` is on PATH, then retry. |
| First run is slow | Expected — it builds the venv, installs the package, and warms a Java font cache once. Later runs are fast. |
| A page's text is missing | The page may be image-only; the vision pass still captures it from the page image. |
| Want to reset the engine | Delete `~/.pdf-to-llm/venv`; it rebuilds on next run. |

---

## License

MIT
