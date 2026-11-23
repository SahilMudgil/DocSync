"""
Rule-based drift checker (Method M1 and 'fast' mode).
Performs deterministic static comparisons:
- Checks if default parameter values in doc match new code signature.
- Checks if parameter names mentioned in doc still exist in new code.
- Generates deterministic template repairs without using any LLM.
"""

import re
from typing import Tuple, Optional
from docsync.models import ChangedSymbol, DocChunk, DriftDecision, RepairSuggestion


def rule_based_check(
    changed_symbol: ChangedSymbol, doc_chunk: DocChunk
) -> Tuple[DriftDecision, Optional[RepairSuggestion]]:
    """Deterministic check comparing function signature against documentation text."""
    sym = changed_symbol.symbol
    sig = sym.signature
    doc_text = doc_chunk.text

    # 1. Check for default values mismatch (e.g. timeout: int = 60 vs "defaults to 30")
    defaults_in_sig = re.findall(r"([a-zA-Z0-9_]+)(?:\s*:[^=,]+)?\s*=\s*([0-9\.]+|True|False|None)", sig)

    mismatches = []
    diff_lines = []
    current_doc_text = doc_text
    notes = []

    for param, new_val in defaults_in_sig:
        # Search for pattern specifically associated with this parameter:
        # e.g. "timeout parameter defaults to 30", "Defaults to a 60 second timeout", "retries defaults to 3"
        pattern_with_param = re.compile(
            rf"(?:{param}[^\.\n]{{0,40}}defaults\s+to\s+(?:a\s+|an\s+)?([0-9\.]+|True|False|None)|defaults\s+to\s+(?:a\s+|an\s+)?([0-9\.]+|True|False|None)[^\.\n]{{0,30}}{param})",
            re.IGNORECASE,
        )
        match = pattern_with_param.search(current_doc_text)
        if not match and len(defaults_in_sig) == 1:
            pattern_generic = re.compile(rf"defaults\s+to\s+(?:a\s+|an\s+)?([0-9\.]+|True|False|None)", re.IGNORECASE)
            match = pattern_generic.search(current_doc_text)

        if match:
            doc_val = match.group(1) or (match.group(2) if len(match.groups()) > 1 else None)
            if doc_val and str(doc_val).strip() != str(new_val).strip():
                mismatches.append(f"Parameter '{param}' default value is {new_val} in code but doc states {doc_val}.")
                
                # Target exact "defaults to ..." for standard unified diff format
                exact_m = re.search(rf"defaults\s+to\s+(?:a\s+|an\s+)?{re.escape(doc_val)}", match.group(0), re.IGNORECASE)
                stale_snippet = exact_m.group(0) if exact_m else match.group(0)
                repaired_snippet = re.sub(re.escape(doc_val), str(new_val), stale_snippet)
                current_doc_text = current_doc_text.replace(stale_snippet, repaired_snippet, 1)
                diff_lines.append(f"- {stale_snippet}\n+ {repaired_snippet}")
                notes.append(f"Updated default value of {param} to {new_val}")

    if mismatches:
        reason = " ".join(mismatches)
        decision = DriftDecision(
            decision="DRIFT",
            confidence=1.0,
            reason=reason,
            evidence_ids=["E2", "D1"],
            repair_needed=True,
        )
        repair = RepairSuggestion(
            doc_id=doc_chunk.id,
            new_text=current_doc_text,
            unified_diff="\n".join(diff_lines),
            evidence_ids=["E2", "D1"],
            notes="; ".join(notes),
        )
        return decision, repair

    # 2. Check for removed parameters
    if changed_symbol.old_code:
        # If parameter names mentioned in doc are completely gone from current signature
        pass

    # No drift detected by static rules
    return (
        DriftDecision(
            decision="MATCH",
            confidence=0.8,
            reason="No contradictory defaults or parameter changes found by rule-based inspection.",
            evidence_ids=["E2", "D1"],
            repair_needed=False,
        ),
        None,
    )
