"""
LLM Judge for Documentation Drift.
Calls chat model with numbered evidence, parses JSON output,
and enforces deterministic post-processing guardrails against hallucinations.
"""

import json
import re
from typing import List, Tuple, Optional
from docsync.models import ChangedSymbol, DocChunk, EvidenceItem, DriftDecision, RepairSuggestion
from docsync.rag.evidence import format_evidence_text
from docsync.llm.factory import ChatModelInterface
from docsync.llm.prompts import (
    DRIFT_JUDGE_V1_SYSTEM,
    DRIFT_JUDGE_V1_USER,
    DRIFT_JUDGE_V2_SYSTEM,
    DRIFT_JUDGE_V2_USER,
)
from docsync.drift.repair import generate_llm_repair


def judge_drift(
    changed_symbol: ChangedSymbol,
    doc_chunk: DocChunk,
    evidence: List[EvidenceItem],
    chat_model: ChatModelInterface,
    repo_name: str = "repo",
    prompt_version: str = "V1",
) -> Tuple[DriftDecision, Optional[RepairSuggestion]]:
    """Judge if documentation chunk drifts from the code using LLM reasoning."""
    sym = changed_symbol.symbol
    evidence_text = format_evidence_text(evidence)
    valid_ids = {item.id for item in evidence}

    if prompt_version.upper() == "V2":
        system_prompt = DRIFT_JUDGE_V2_SYSTEM
        user_prompt = DRIFT_JUDGE_V2_USER.format(
            repository=repo_name,
            symbol=sym.name,
            evidence=evidence_text,
        )
    else:
        system_prompt = DRIFT_JUDGE_V1_SYSTEM
        user_prompt = DRIFT_JUDGE_V1_USER.format(
            repository=repo_name,
            symbol=sym.name,
            evidence=evidence_text,
        )

    raw_response = chat_model.complete(system_prompt, user_prompt)
    decision = _parse_judge_json(raw_response, valid_ids)

    repair = None
    if decision.decision == "DRIFT":
        repair = generate_llm_repair(doc_chunk, evidence, decision.reason, chat_model)

    return decision, repair


def _parse_judge_json(raw_text: str, valid_ids: set) -> DriftDecision:
    """Parse and clean JSON response with guardrails."""
    clean = raw_text.strip()
    # Strip markdown ```json blocks if present
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        clean = match.group(0)

    try:
        data = json.loads(clean)
    except Exception:
        return DriftDecision(
            decision="MODEL_ERROR",
            confidence=0.0,
            reason="Model returned invalid JSON format.",
            evidence_ids=[],
            claims=[],
            repair_needed=False,
        )

    dec_val = str(data.get("decision", "UNCERTAIN")).upper()
    if dec_val not in ["MATCH", "DRIFT", "UNCERTAIN"]:
        dec_val = "UNCERTAIN"

    conf = float(data.get("confidence", 0.5))
    conf = max(0.0, min(1.0, conf))

    reason = str(data.get("reason", "No reason provided."))

    # Filter hallucinated evidence IDs
    ev_ids = [eid for eid in data.get("evidence_ids", []) if eid in valid_ids]

    # Extract claims list if present
    raw_claims = data.get("claims", [])
    claims = [c for c in raw_claims if isinstance(c, dict)] if isinstance(raw_claims, list) else []

    # Guardrail: DRIFT without valid evidence -> downgrade to UNCERTAIN
    if dec_val == "DRIFT" and not ev_ids:
        dec_val = "UNCERTAIN"
        reason += " (Downgraded to UNCERTAIN: no valid evidence cited)."

    return DriftDecision(
        decision=dec_val,
        confidence=conf,
        reason=reason,
        evidence_ids=ev_ids,
        claims=claims,
        repair_needed=(dec_val == "DRIFT"),
    )

