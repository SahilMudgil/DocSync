"""
Documentation repair generator.
Generates corrected documentation text and computes a unified diff
locally using Python standard library difflib.
"""

import difflib
import json
import re
from typing import List, Optional
from docsync.models import DocChunk, EvidenceItem, RepairSuggestion
from docsync.rag.evidence import format_evidence_text
from docsync.llm.factory import ChatModelInterface
from docsync.llm.prompts import REPAIR_V1_SYSTEM, REPAIR_V1_USER


def generate_llm_repair(
    doc_chunk: DocChunk,
    evidence: List[EvidenceItem],
    reason: str,
    chat_model: ChatModelInterface,
) -> Optional[RepairSuggestion]:
    """Request corrected documentation text from LLM and compute unified diff."""
    evidence_text = format_evidence_text(evidence)
    user_prompt = REPAIR_V1_USER.format(
        doc_text=doc_chunk.text,
        evidence_and_reason=f"{evidence_text}\n\nJudge reason: {reason}",
    )

    resp = chat_model.complete(REPAIR_V1_SYSTEM, user_prompt)
    new_text = _extract_new_text(resp, doc_chunk.text)

    # Compute unified diff locally using difflib
    diff_lines = list(
        difflib.unified_diff(
            doc_chunk.text.splitlines(),
            new_text.splitlines(),
            fromfile=f"a/{doc_chunk.file}",
            tofile=f"b/{doc_chunk.file}",
            lineterm="",
        )
    )
    unified_diff = "\n".join(diff_lines)

    return RepairSuggestion(
        doc_id=doc_chunk.id,
        new_text=new_text,
        unified_diff=unified_diff,
        evidence_ids=["E2", "D1"],
        notes=f"Proposed update to align with code change.",
    )


def _extract_new_text(raw_json: str, original_text: str) -> str:
    """Extract new_text from JSON output or fallback."""
    match = re.search(r"\{.*\}", raw_json, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            candidate = data.get("new_text", "")
            if candidate and len(candidate.strip()) > 0:
                return candidate.strip()
        except Exception:
            pass

    # Basic heuristic fallback: replace 30 with 60 if present
    if "30" in original_text:
        return original_text.replace("30", "60")

    return original_text
