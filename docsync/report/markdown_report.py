"""
Markdown report generator for PR comments and CLI display.
Formats Drift decisions, evidence citations, suggested diffs, and example checks.
"""

from docsync.models import RunResult


def generate_markdown_report(result: RunResult) -> str:
    """Render a structured Markdown report from a RunResult object."""
    drift_items = [it for it in result.items if it.decision.decision == "DRIFT"]
    match_items = [it for it in result.items if it.decision.decision == "MATCH"]

    lines = [
        "## [DocSync] Documentation Verification Report",
        f"**Mode:** `{result.mode}` | **Provider/Model:** `{result.provider}:{result.model}` | **Retrieval:** `{result.retrieval_mode}` | **Sourcegraph:** `{'Active' if result.sourcegraph_used else 'Local Fallback'}`",
        f"**Changed Symbols:** {len(result.items)} | **Drift Detected:** {len(drift_items)} | **Matches:** {len(match_items)}",
        "",
        "### Summary Table",
        "| Symbol | Doc Location | Decision | Confidence | Evidence Cited |",
        "|---|---|---|---:|---|",
    ]

    for it in result.items:
        sym_name = it.changed_symbol.symbol.name
        doc_loc = f"{it.candidate_doc.file}:{it.candidate_doc.start_line}-{it.candidate_doc.end_line}"
        ev_str = ", ".join(it.decision.evidence_ids) or "None"
        dec_badge = f"**{it.decision.decision}**"
        lines.append(f"| `{sym_name}()` | {doc_loc} | {dec_badge} | {it.decision.confidence:.2f} | `{ev_str}` |")

    # Drift details
    if drift_items:
        lines.append("\n---")
        lines.append("### [DRIFT] Documentation Drift Details")

        for idx, it in enumerate(drift_items, 1):
            doc = it.candidate_doc
            sym = it.changed_symbol.symbol
            lines.append(f"\n#### {idx}. Drift in `{doc.file}` (lines {doc.start_line}-{doc.end_line})")
            lines.append(f"- **Triggered by Symbol:** `{sym.name}` in `{sym.file}:{sym.start_line}`")
            lines.append(f"- **Reason:** {it.decision.reason}")
            lines.append(f"- **Evidence:** `{'`, `'.join(it.decision.evidence_ids)}`")

            if it.repair and it.repair.unified_diff:
                lines.append("\n**Suggested Fix (Unified Diff):**")
                lines.append(f"```diff\n{it.repair.unified_diff}\n```")

            if it.example_checks:
                status_list = [f"Block #{ec.block_index}: {ec.status}" for ec in it.example_checks]
                lines.append(f"- **Example Code Check:** {', '.join(status_list)}")

    lines.append("\n---")
    lines.append("> [Note] Human review is required before changes are applied. DocSync never auto-merges.")

    return "\n".join(lines)
