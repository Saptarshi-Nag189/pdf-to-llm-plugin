---
description: Convert a PDF into LLM-digestible Markdown (text + vision-described figures)
argument-hint: <path-to-pdf> [output-dir]
---

Convert a PDF into a single self-contained, LLM-digestible Markdown file with
minimal context loss, using the **pdf-to-llm** skill.

Arguments: `$ARGUMENTS`
(First argument = path to the input PDF; optional second argument = output directory.)

Steps:
1. Invoke the **pdf-to-llm** skill and follow its full workflow.
2. Run its extraction script:
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/convert_pdf.py" "<pdf>" ["<output_dir>"]`
3. Read the raw Markdown it produces, then read **every** extracted image with the
   Read tool and write detailed inline descriptions/transcriptions (diagrams → flow,
   plots → axes/trends/values, in-image tables → Markdown tables, photos → brief
   caption). Aim for zero context loss.
4. Assemble the final `<pdf_stem>_llm.md` in original reading order, replacing each
   image reference with a `> **[Figure: ...]**` description block, and add a short
   Summary section at the end.
5. Report the output path, file size, and number of figures described.

If no PDF path was given in `$ARGUMENTS`, ask the user for the path before starting.
