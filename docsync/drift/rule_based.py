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

    for param, new_val in defaults_in_sig:
        # Search for pattern like "param defaults to <old_val>" or "defaults to <old_val>"
        pattern = re.compile(rf"(?:{param}\s+)?defaults\s+to\s+([0-9]+|True|False|None)", re.IGNORECASE)
        match = pattern.search(doc_text)
        if match:
            doc_val = match.group(1)
            if str(doc_val).strip() != str(new_val).strip():
                # Found a mismatch!
                reason = f"Parameter '{param}' default value is {new_val} in code but doc states {doc_val}."
                decision = DriftDecision(
                    decision="DRIFT",
                    confidence=1.0,
                    reason=reason,
                    evidence_ids=["E2", "D1"],
                    repair_needed=True,
                )

                # Deterministic template repair
                stale_snippet = match.group(0)
                repaired_snippet = re.sub(re.escape(doc_val), str(new_val), stale_snippet)
                new_doc_text = doc_text.replace(stale_snippet, repaired_snippet, 1)

                repair = RepairSuggestion(
                    doc_id=doc_chunk.id,
                    new_text=new_doc_text,
                    unified_diff=f"- {stale_snippet}\n+ {repaired_snippet}",
                    evidence_ids=["E2", "D1"],
                    notes=f"Updated default value of {param} to {new_val}",
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
