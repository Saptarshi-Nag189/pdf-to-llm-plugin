# pdf-to-llm (Claude Code plugin)

Convert any PDF into clean, **LLM-digestible Markdown** with minimal context loss.

- **Stage 1 — local extraction:** [`opendataloader-pdf`](https://github.com/opendataloader-project/opendataloader-pdf)
  pulls out text, tables, layout, reading order, and saves every embedded image.
  Runs fully offline; nothing is uploaded.
- **Stage 2 — vision enrichment:** Claude reads each extracted image and writes a
  detailed inline description / transcription — so figures, diagrams, plots, and
  in-image tables survive as text.

Result: a single self-contained `<name>_llm.md` an LLM can fully understand without
the original images.

## Install on any machine

```
/plugin marketplace add saptarshi/pdf-to-llm-plugin
/plugin install pdf-to-llm@saptarshi-tools
```

(Replace `saptarshi/pdf-to-llm-plugin` with your actual GitHub `owner/repo` once pushed.)

Then use either:

- **Slash command:** `/pdf2md <path-to-pdf> [output-dir]`
- **Natural language:** "Convert this PDF to Markdown for an LLM: /path/to/file.pdf"
  (the skill is picked up automatically)

## Requirements

- **Python 3.9+** on PATH
- **Java 11+** on PATH (opendataloader-pdf is Java-backed; e.g. Temurin/Adoptium or
  Microsoft OpenJDK)
- First run creates an isolated venv at `~/.pdf-to-llm/venv` and installs
  `opendataloader-pdf` into it. Your global Python packages are never touched.

## Contents

| Path | Purpose |
|------|---------|
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Marketplace manifest (so this repo is directly installable) |
| `commands/pdf2md.md` | `/pdf2md` slash command |
| `skills/pdf-to-llm/SKILL.md` | The skill definition + workflow |
| `scripts/convert_pdf.py` | Manages the isolated venv and runs local extraction |

## How it compares

`opendataloader-pdf` extracts ~2× more raw text than `marker` and preserves table
structure — but, like every text extractor, it can't read content trapped inside
figures. The vision-enrichment pass is the key augmentation that makes the output
truly LLM-ready.

## License

MIT
