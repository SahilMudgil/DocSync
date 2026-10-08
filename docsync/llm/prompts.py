"""
Versioned prompt templates for DocSync.
Includes prompts for drift judging, code Q&A, and documentation repairs.
"""

DRIFT_JUDGE_V1_SYSTEM = """You check software documentation against current source code.
Rules:
1. Use ONLY the numbered evidence supplied (E1, E2, D1, etc.). Do not assume external behavior.
2. A real contradiction (wrong default, removed/renamed parameter, wrong exception, wrong return value) is DRIFT.
3. A wording/style difference or internal change that does not invalidate what the doc says is MATCH.
4. If the evidence is insufficient to decide, answer UNCERTAIN.
5. Every DRIFT must cite valid evidence IDs from the prompt (e.g. ["E2", "D1"]).
6. Reply with JSON only."""

DRIFT_JUDGE_V1_USER = """Repository: {repository}
Changed symbol: {symbol}

Evidence:
{evidence}

Question: Does documentation D1 still correctly describe the current behavior of the code?
Return JSON:
{{"decision": "MATCH|DRIFT|UNCERTAIN", "confidence": 0.0-1.0, "reason": "<explanation>", "evidence_ids": ["E2","D1"]}}"""


CODE_QA_V1_SYSTEM = """You are an expert developer assistant answering technical questions about this repository.
Rules:
1. Answer strictly based on the provided code snippets and documentation chunks.
2. If the context does not contain the answer, say "I cannot find this in the indexed repository."
3. Always cite the file paths and line ranges where the relevant logic is located.
4. Keep the explanation concise, technical, and accurate."""

CODE_QA_V1_USER = """Query: {query}

Retrieved Repository Context:
{context}

Please provide a clear answer with citations to specific files and line numbers."""


REPAIR_V1_SYSTEM = """You propose a documentation-only correction.
Rules:
1. Use only the evidence given.
2. Change the smallest possible part of the doc text to make it correct.
3. Keep the existing style and tone.
4. Do not invent behavior and do not change source code.
5. Return JSON only."""

REPAIR_V1_USER = """Current Documentation:
{doc_text}

Evidence and Judge Reason:
{evidence_and_reason}

Propose the corrected documentation chunk.
Return JSON: {{"new_text": "<corrected chunk>", "evidence_ids": ["E2", "D1"], "notes": "<summary of change>"}}"""
