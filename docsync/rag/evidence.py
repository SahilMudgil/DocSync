"""
Evidence builder for RAG judgment.
Assembles numbered evidence items: E1 old code, E2 new code, E3 callers, D1 doc text.
"""

from typing import List
from docsync.models import ChangedSymbol, DocChunk, EvidenceItem, SearchHit


def build_evidence(
    changed_symbol: ChangedSymbol,
    doc_chunk: DocChunk,
    callers: List[SearchHit] = None,
    max_code_chars: int = 4000,
) -> List[EvidenceItem]:
    """Construct numbered EvidenceItem list for one (ChangedSymbol, DocChunk) pair."""
    evidence: List[EvidenceItem] = []
    sym = changed_symbol.symbol

    # E1: Old code (if available)
    if changed_symbol.old_code:
        old_text = changed_symbol.old_code[:max_code_chars]
        evidence.append(
            EvidenceItem(
                id="E1",
                kind="old_code",
                file=sym.file,
                start_line=sym.start_line,
                end_line=sym.end_line,
                text=old_text,
            )
        )

    # E2: New code
    new_text = sym.code[:max_code_chars]
    evidence.append(
        EvidenceItem(
            id="E2",
            kind="new_code",
            file=sym.file,
            start_line=sym.start_line,
            end_line=sym.end_line,
            text=new_text,
        )
    )

    # E3-E5: Callers
    if callers:
        for idx, caller in enumerate(callers[:3], start=3):
            evidence.append(
                EvidenceItem(
                    id=f"E{idx}",
                    kind="caller",
                    file=caller.file,
                    start_line=caller.line,
                    end_line=caller.line,
                    text=caller.snippet,
                )
            )

    # D1: Candidate Documentation
    evidence.append(
        EvidenceItem(
            id="D1",
            kind="doc",
            file=doc_chunk.file,
            start_line=doc_chunk.start_line,
            end_line=doc_chunk.end_line,
            text=doc_chunk.text,
        )
    )

    return evidence


def format_evidence_text(evidence: List[EvidenceItem]) -> str:
    """Format evidence items into a plain readable string for LLM prompts."""
    blocks = []
    for item in evidence:
        blocks.append(
            f"[{item.id}] ({item.kind}) {item.file}:{item.start_line}-{item.end_line}\n{item.text}"
        )
    return "\n\n".join(blocks)
