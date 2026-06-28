# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-06-28

### Added
- Initial release.
- Two-stage **PDF → LLM-digestible Markdown** conversion:
  - **Stage 1 (local):** text, table, layout and image extraction via
    [`opendataloader-pdf`](https://github.com/opendataloader-project/opendataloader-pdf).
  - **Stage 2 (vision):** inline descriptions/transcriptions of every figure,
    diagram, chart, plot and in-image table, produced by the Claude model already
    running the session — **no API key, no local AI model required**.
- `/pdf2md` slash command.
- `pdf-to-llm` skill (auto-invoked from natural-language requests).
- Marketplace manifest (`.claude-plugin/marketplace.json`) for one-line install on
  any machine.
- Isolated virtual environment at `~/.pdf-to-llm/venv` so the user's global Python
  packages are never modified.
- Clear `Java 11+` / `Python 3.9+` prerequisite checks with actionable error messages.
