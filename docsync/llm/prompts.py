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


# ---------------------------------------------------------------------------
# DRIFT_JUDGE_V2: Claim-by-claim verification with few-shot examples (E5)
# ---------------------------------------------------------------------------
DRIFT_JUDGE_V2_SYSTEM = """You check software documentation against current source code using claim-by-claim verification.
Rules:
1. First, list every factual claim made in documentation D1 (defaults, parameter names, return types, exceptions).
2. For each claim, determine status: SUPPORTED, CONTRADICTED, or NOT_COVERED by the code evidence.
3. If any claim is CONTRADICTED by current code (e.g. changed default, renamed parameter), the decision is DRIFT.
4. If all claims are SUPPORTED, or changes are purely internal refactorings, the decision is MATCH.
5. If evidence is missing or ambiguous, answer UNCERTAIN.
6. Return JSON only with "decision", "confidence", "reason", "evidence_ids", and "claims".

Worked Examples:
[Example 1 - DRIFT]:
Code Evidence E2: def fetch_data(url: str, timeout: int = 60)
Doc D1: "The timeout defaults to 30 seconds."
JSON Response:
{
  "decision": "DRIFT",
  "confidence": 1.0,
  "reason": "Parameter timeout default is 60 in code but doc states 30.",
  "evidence_ids": ["E2", "D1"],
  "claims": [{"claim": "timeout defaults to 30", "status": "CONTRADICTED"}]
}

[Example 2 - MATCH]:
Code Evidence E2: def fetch_data(url: str, timeout: int = 30):
    response_data = do_request(url)
    return response_data
Doc D1: "Fetches JSON data from a remote URL."
JSON Response:
{
  "decision": "MATCH",
  "confidence": 0.95,
  "reason": "Local variable renamed; external contract and doc claims remain fully valid.",
  "evidence_ids": ["E2", "D1"],
  "claims": [{"claim": "Fetches JSON data from remote URL", "status": "SUPPORTED"}]
}"""

DRIFT_JUDGE_V2_USER = """Repository: {repository}
Changed symbol: {symbol}

Evidence:
{evidence}

Perform claim-by-claim verification on D1 against the code.
Return JSON:
{{
  "decision": "MATCH|DRIFT|UNCERTAIN",
  "confidence": 0.0-1.0,
  "reason": "<explanation>",
  "evidence_ids": ["E2", "D1"],
  "claims": [
    {{"claim": "<extracted claim>", "status": "SUPPORTED|CONTRADICTED|NOT_COVERED"}}
  ]
}}"""


# ---------------------------------------------------------------------------
# Prompt Lab Tasks: Docstring Completion, Refactoring, Explanation (A1)
# ---------------------------------------------------------------------------
DOCSTRING_COMPLETE_V1_SYSTEM = """You are a code documentation assistant.
Write a concise, accurate docstring for the given Python function. Output ONLY the docstring inside triple quotes."""

DOCSTRING_COMPLETE_V1_USER = """Function Code:
```python
{code}
```
Write docstring:"""


DOCSTRING_COMPLETE_V2_SYSTEM = """You are an expert developer.
Write a structured Google-style Python docstring following this exact template:
Summary of function purpose in one sentence.

Args:
    <name> (<type>): Description of parameter and default value.
Returns:
    <type>: Description of returned object.
Raises:
    <Error>: When and why this exception is raised.

Output ONLY the docstring enclosed in triple quotes."""

DOCSTRING_COMPLETE_V2_USER = """Function Code:
```python
{code}
```
Generate structured docstring:"""


REFACTOR_V1_SYSTEM = """You are an expert Python refactoring tool.
Refactor the provided function to improve clean code structure, variable naming, and readability.
Rules:
1. Maintain the exact same function name and external signature.
2. Preserve identical external behavior, exceptions, and return values.
3. Return ONLY raw Python code. Do not wrap in markdown quotes."""

REFACTOR_V1_USER = """Function Code:
{code}

Refactored Code:"""


EXPLAIN_V1_SYSTEM = """You explain software code clearly and concisely.
Explain what the function does in exactly 3 bullet points:
1. Purpose & Core Functionality
2. Input Parameters & Contracts
3. Return Value or Side Effects"""

EXPLAIN_V1_USER = """Function Code:
{code}

3-Line Explanation:"""


EXAMPLE_CHECK_V1_SYSTEM = """You validate documentation code snippets against current Python function signatures.
Do not execute the code. Check for wrong argument types, renamed parameters, or obsolete API calls.
Return JSON: {"syntax_ok": true|false, "mismatches": ["<detail>"], "status": "PASS|WARN|FAIL"}"""

EXAMPLE_CHECK_V1_USER = """Documentation Code Example:
{example_code}

Known Current Signatures:
{signatures}"""


CODE_QA_V1_SYSTEM = """You are an expert developer assistant answering technical questions about this repository.
Rules:
1. Answer strictly based on the provided code snippets and documentation chunks.
2. If the context does not contain the answer, say "I cannot find this in the indexed repository."
3. Always cite the file paths and line ranges where the relevant logic is located.
4. Keep the explanation concise, technical, accurate, and under 3-4 sentences."""

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
