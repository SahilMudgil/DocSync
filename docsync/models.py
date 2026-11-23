"""
Data models for DocSync using Pydantic.
Provides schemas for code symbols, documentation chunks, retrieval hits,
drift decisions, and overall execution run results.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class CodeSymbol(BaseModel):
    name: str
    kind: Literal["function", "method", "class"] = "function"
    file: str
    start_line: int
    end_line: int
    signature: str = ""
    code: str = ""
    docstring: Optional[str] = None


class ChangedSymbol(BaseModel):
    symbol: CodeSymbol
    old_code: Optional[str] = None
    change_type: Literal["added", "modified", "deleted"] = "modified"


class DocChunk(BaseModel):
    id: str
    file: str
    start_line: int
    end_line: int
    kind: Literal["docstring", "md_section", "rst_section"] = "md_section"
    text: str
    mentioned_symbols: List[str] = Field(default_factory=list)
    code_blocks: List[str] = Field(default_factory=list)


class SearchHit(BaseModel):
    file: str
    line: int
    snippet: str
    source: Literal["local", "sourcegraph"] = "local"
    score: float = 0.0


class EvidenceItem(BaseModel):
    id: str  # e.g., "E1", "E2", "D1"
    kind: Literal["old_code", "new_code", "caller", "doc"]
    file: str
    start_line: int
    end_line: int
    text: str


class DriftDecision(BaseModel):
    decision: Literal["MATCH", "DRIFT", "UNCERTAIN", "MODEL_ERROR"]
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    reason: str
    evidence_ids: List[str] = Field(default_factory=list)
    claims: List[Dict[str, str]] = Field(default_factory=list)
    repair_needed: bool = False


class RepairSuggestion(BaseModel):
    doc_id: str
    new_text: str
    unified_diff: str
    evidence_ids: List[str] = Field(default_factory=list)
    notes: str = ""


class ExampleCheck(BaseModel):
    doc_id: str
    block_index: int
    syntax_ok: bool
    unknown_names: List[str] = Field(default_factory=list)
    status: Literal["PASS", "WARN", "FAIL", "SKIPPED"] = "PASS"


class DriftItemResult(BaseModel):
    changed_symbol: ChangedSymbol
    candidate_doc: DocChunk
    decision: DriftDecision
    repair: Optional[RepairSuggestion] = None
    example_checks: List[ExampleCheck] = Field(default_factory=list)


class RunResult(BaseModel):
    run_id: str
    repo: str
    base: str
    head: str
    mode: Literal["fast", "full"]
    provider: str
    model: str
    retrieval_mode: str
    sourcegraph_used: bool = False
    prompt_versions: Dict[str, str] = Field(default_factory=dict)
    items: List[DriftItemResult] = Field(default_factory=list)
    timings: Dict[str, float] = Field(default_factory=dict)
    token_usage: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
