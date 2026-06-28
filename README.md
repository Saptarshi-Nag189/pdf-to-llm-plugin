# pdf-to-llm

<!-- Optional hero banner: generate an image (see the prompt in the project notes),
     save it as assets/hero.png, then uncomment the line below.
<p align="center"><img src="assets/hero.png" alt="pdf-to-llm — PDF to LLM-ready Markdown" width="680"></p>
-->

**Turn any PDF into Markdown an LLM can actually understand — including the figures.**

A Claude Code plugin that converts PDFs to clean, self-contained Markdown with
minimal context loss. Unlike plain text extractors, it doesn't just skip the
diagrams, plots, and tables-as-images that hold most of a technical document's
meaning — it *describes them inline* using Claude's vision.

---

## The problem

Most PDF→Markdown tools extract the text and leave you with this:

```markdown
## System Architecture
![](page_4_figure_2.png)
```

An LLM reading that learns **nothing** from the figure. And in slide decks,
technical papers, and reports, the figures *are* the content: the architecture
diagram, the trend and axis values on a chart, the rows of a table that was pasted
in as an image — all gone.

## The fix

`pdf-to-llm` runs in two stages and produces this instead:

```markdown
## System Architecture

> **[Figure: Request flow]**
> Left-to-right block diagram:
> 1. **Client** sends an HTTPS request →
> 2. **API Gateway** (authentication + rate limiting) →
> 3. **Service layer** — three microservices: Orders, Inventory, Billing →
> 4. **PostgreSQL** primary, with a read replica
>
> A dashed arrow shows the Billing service publishing events to a **Kafka** queue,
> consumed by an Analytics worker.
```

Charts become their axes, series, and key values; tables-as-images become real
Markdown tables; photos get a one-line caption. The result is a single
`<name>_llm.md` that is fully understandable **without the original images** —
ready to paste into a chat, drop into a RAG pipeline, or keep as notes.

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

## Acknowledgements

This plugin is built on top of, and would not work without,
[**OpenDataLoader PDF**](https://github.com/opendataloader-project/opendataloader-pdf)
by the [opendataloader-project](https://github.com/opendataloader-project) — the
local engine that does all of Stage 1 (text, table, layout, and image extraction).
It is an excellent open-source project; please consider starring it.

- **OpenDataLoader PDF** — © opendataloader-project, licensed under
  [Apache License 2.0](https://github.com/opendataloader-project/opendataloader-pdf/blob/main/LICENSE).

`pdf-to-llm` only orchestrates that extractor and adds the Claude-driven
vision-enrichment stage on top; all credit for the underlying PDF parsing belongs
to its authors.

## License

[MIT](LICENSE) © 2026 Saptarshi Nag

This project bundles no third-party source code. The runtime dependency
`opendataloader-pdf` (Apache-2.0) is installed separately into an isolated venv at
first run and remains under its own license.
