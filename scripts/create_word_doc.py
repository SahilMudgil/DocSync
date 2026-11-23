"""
Generate a professional, fully formatted Microsoft Word (.docx) document
for the DocSync Mid-Semester Viva Defense, Speaker Notes, and Technical Guide.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc = Document()

# Set page margins (1 inch)
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Colors
COLOR_PRIMARY = RGBColor(15, 23, 42)      # Deep Navy
COLOR_SECONDARY = RGBColor(30, 58, 138)   # Royal Blue
COLOR_ACCENT = RGBColor(14, 116, 144)     # Cyan / Slate
COLOR_MUTED = RGBColor(71, 85, 105)       # Slate Gray
COLOR_HIGHLIGHT = RGBColor(220, 38, 38)   # Red / Alert

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner margins (padding) for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_callout(text, prefix="💡 KEY TAKEAWAY FOR VIVA:"):
    """Add a shaded callout block."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    
    cell = table.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    # Left border
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="0284C7"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run_pre = p.add_run(f"{prefix} ")
    run_pre.bold = True
    run_pre.font.size = Pt(10)
    run_pre.font.color.rgb = COLOR_SECONDARY
    
    run_txt = p.add_run(text)
    run_txt.font.size = Pt(10)
    run_txt.font.color.rgb = COLOR_PRIMARY
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

# ==============================================================================
# TITLE & HEADER
# ==============================================================================
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after = Pt(4)
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_title = title_p.add_run("DOCSYNC")
run_title.font.name = "Arial"
run_title.font.size = Pt(26)
run_title.font.bold = True
run_title.font.color.rgb = COLOR_PRIMARY

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_before = Pt(0)
sub_p.paragraph_format.space_after = Pt(6)
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_sub = sub_p.add_run("Autonomous AI DevOps Documentation Drift Platform\nMid-Semester Presentation Speaker Notes & Comprehensive Technical Guide")
run_sub.font.name = "Arial"
run_sub.font.size = Pt(13)
run_sub.font.bold = True
run_sub.font.color.rgb = COLOR_SECONDARY

meta_p = doc.add_paragraph()
meta_p.paragraph_format.space_before = Pt(0)
meta_p.paragraph_format.space_after = Pt(16)
meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_meta = meta_p.add_run("Course: CSE 4011 Intelligent Developer Tools & AI DevOps Workflows\nFaculty: Dr. Kiran Khatter  ·  Institution: BML Munjal University")
run_meta.font.name = "Calibri"
run_meta.font.size = Pt(10)
run_meta.font.italic = True
run_meta.font.color.rgb = COLOR_MUTED

# Divider
p_div = doc.add_paragraph()
p_div.paragraph_format.space_before = Pt(0)
p_div.paragraph_format.space_after = Pt(12)
run_d = p_div.add_run("━" * 58)
run_d.font.color.rgb = RGBColor(203, 213, 225)
p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ==============================================================================
# SECTION 1: SLIDE-BY-SLIDE SPEAKER NOTES
# ==============================================================================
h1 = doc.add_heading(level=1)
r = h1.add_run("1. Slide-by-Slide Speaker Notes (What to Say in 20–30 Seconds)")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.color.rgb = COLOR_PRIMARY

slides_data = [
    (
        "Slide 1: Title Slide (Hero Slide — DOCSYNC)",
        "Good morning, ma'am/sir. Today we present DocSync, an Autonomous AI DevOps and Documentation Drift Detection Platform. In modern software engineering, code changes constantly, but documentation rots because tests do not fail on stale docs. DocSync acts as an automated CI/CD quality gate that detects documentation drift on pull requests, cites exact verifiable evidence, and proposes self-healing unified diff patches."
    ),
    (
        "Slide 2: The Problem (01 · THE PROBLEM)",
        "Here is the critical blind spot in modern CI/CD: when a developer modifies a function—for example, changing a default timeout from 30 seconds to 60 seconds—linters check syntax, and Pytest tests execution logic. The build passes cleanly! But zero existing tools check whether the README or docstrings are still accurate. Developers are misled by stale docs, creating silent technical debt and broken API integrations."
    ),
    (
        "Slide 3: Motivation (02 · MOTIVATION)",
        "Traditionally, documentation review is manual, and under tight sprint deadlines, it gets skipped. With DocSync, we replace manual guesswork with an automated feedback loop: on every Git pull request, DocSync parses the AST contract difference, runs hybrid search across the repo, judges drift with evidence guardrails, and auto-generates unified diff patches before code merges."
    ),
    (
        "Slide 4: The Solution (03 · THE SOLUTION)",
        "What is DocSync? It operates on a 5-stage loop: (1) Ingest Git diff line ranges. (2) Parse code contracts using Python AST. (3) Retrieve candidate docs via Hybrid Search (BM25 + FAISS). (4) Judge MATCH vs. DRIFT citing verifiable tokens (E2 vs D1). (5) Generate self-healing patches and provide an interactive Repository Code Q&A bot."
    ),
    (
        "Slide 5: Technology Stack (04 · TECHNOLOGY)",
        "Our tech stack bridges modern DevOps with AI: our frontend is a Dark Obsidian Streamlit dashboard on port 8501. Static analysis uses Python's native ast and Tree-sitter. For retrieval, we combine BM25 keyword search with FAISS dense vector embeddings using Reciprocal Rank Fusion. For inference, we use an AWS EC2 Ubuntu instance running Ollama with DeepSeek-Coder 6.7B, alongside Google Gemini, automated by GitHub Actions and multi-stage Docker containers."
    ),
    (
        "Slide 6: System Architecture (05 · ARCHITECTURE)",
        "Looking at our architecture: the Streamlit dashboard communicates with the DocSync core engine. When a PR diff is ingested, the AST engine extracts signatures while the hybrid retriever pulls candidate docs. For AI reasoning, our local app makes remote HTTP calls across port 11434 to our AWS EC2 cloud worker running Ollama. The entire application is containerized with live health probes on port 8501."
    ),
    (
        "Slide 7: How the System Works (06 · WORKFLOW)",
        "Our workflow follows 3 distinct phases across 9 steps: (1) Ingest & Parse: We isolate Git diff lines and parse AST signatures and defaults. (2) Retrieve & Judge: BM25 and vector search retrieve candidate docs, RRF ranks the best match, and our judge checks for contradictions. (3) Heal & Interact: If drift is found, difflib generates a unified diff patch that can be applied to disk in 1 click or handed to Sweep.dev."
    ),
    (
        "Slide 8: Prototype Demonstration (07 · DEMO)",
        "We built a deterministic benchmark to prove our tool: in Commit C0 to C1, we added a harmless comment. DocSync returned MATCH—proving 0% false alarms on refactors. In Commit C1 to C2, code changed timeout=30 to 60 with docs untouched. DocSync caught DRIFT in 0.159s, cited Token E2 (Code 60) against Token D1 (Doc 30), and generated an exact unified diff to repair both the docstring and usage.md."
    ),
    (
        "Slide 9: Future Scope (08 · NEXT STEPS)",
        "For our A3 milestone, we are expanding: (1) Multi-Language AST Support: expanding Tree-sitter from Python to TypeScript, Go, and Java. (2) Inline GitHub PR Bot: posting review comments directly on drifted lines via the GitHub API. (3) Docs Server Sync: auto-syncing doc repairs into Sphinx and MkDocs. (4) Enterprise Monorepo Call-Graphs: using Sourcegraph LSIF to trace downstream API consumers."
    ),
    (
        "Slide 10: Conclusion & Thank You (CONCLUSION)",
        "In conclusion, DocSync closes the documentation debt gap, turning static, rotting documentation into a living, repository-aware self-healing feedback loop. Thank you, and we are now open for questions!"
    ),
]

for title, script in slides_data:
    p_st = doc.add_paragraph()
    p_st.paragraph_format.space_before = Pt(8)
    p_st.paragraph_format.space_after = Pt(2)
    r_t = p_st.add_run(f"📌 {title}")
    r_t.font.name = "Arial"
    r_t.font.size = Pt(11)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_SECONDARY
    
    p_sc = doc.add_paragraph()
    p_sc.paragraph_format.space_before = Pt(0)
    p_sc.paragraph_format.space_after = Pt(6)
    p_sc.paragraph_format.left_indent = Inches(0.2)
    r_s = p_sc.add_run(f'"{script}"')
    r_s.font.name = "Calibri"
    r_s.font.size = Pt(10.5)
    r_s.font.italic = True
    r_s.font.color.rgb = COLOR_PRIMARY

# ==============================================================================
# SECTION 2: TECHNICAL TERMS DICTIONARY
# ==============================================================================
doc.add_page_break()
h2 = doc.add_heading(level=1)
r = h2.add_run("2. Complete Technical Terms Dictionary")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.color.rgb = COLOR_PRIMARY

tech_terms = [
    ("AST (Abstract Syntax Tree)", "A tree representation of the abstract syntactic structure of source code. Compilers and parsers use it to understand code grammar. Instead of viewing code as unstructured characters, AST breaks code down into structured nodes: FunctionDef, arguments, default values, return types, and docstrings."),
    ("Tree-sitter", "A fast, incremental parsing library used across modern developer tooling (like GitHub and Neovim). It builds syntax trees for multiple programming languages (Python, Go, JS, Rust) and provides robust error recovery even when code contains syntax errors."),
    ("RAG (Retrieval-Augmented Generation)", "An AI architecture pattern that retrieves verified source documents from a database or repository first, and then injects those retrieved chunks into the prompt for the LLM. This grounds the model in real facts and eliminates hallucinations."),
    ("FAISS (Facebook AI Similarity Search)", "An open-source library developed by Meta AI for fast dense vector similarity search. In DocSync, docstrings and markdown chunks are embedded into vectors, and FAISS finds the top-K chunks closest in semantic meaning to a changed function."),
    ("Dense Vector Embeddings", "Converting text into dense numerical arrays (e.g., 384 numbers using all-MiniLM-L6-v2). Sentences with similar meanings produce vectors that are close to each other in vector space, allowing semantic matching beyond literal keywords."),
    ("BM25 (Best Matching 25)", "A classic, highly effective lexical (keyword) ranking algorithm based on Term Frequency and Inverse Document Frequency. It ensures that documents explicitly mentioning exact symbol names (like 'fetch_data' or 'timeout') are retrieved with high priority."),
    ("RRF (Reciprocal Rank Fusion)", "An algorithmic rank aggregation method that combines multiple ranked lists. Formula: Score = Σ 1 / (60 + rank). In DocSync, RRF seamlessly fuses keyword results from BM25 with semantic results from FAISS to produce superior retrieval quality."),
    ("Evidence Tokens (E2 vs D1)", "Hallucination guardrail tokens created by DocSync's evidence builder. E2 is the exact code token (e.g., timeout=60) and D1 is the doc token (e.g., defaults to 30). The judge model must cite both tokens to justify a DRIFT verdict."),
    ("Unified Diff (difflib)", "The universal standard text format for showing code changes with '-' and '+' lines. DocSync uses Python's native difflib to generate clean unified diffs for documentation repair on disk."),
    ("Hallucination Guardrails", "Prompts and constraints designed to stop LLMs from making up false drift claims. If no contradictory evidence tokens are found, DocSync mandates that the decision must be MATCH or UNCERTAIN."),
]

table_tech = doc.add_table(rows=1, cols=2)
table_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
table_tech.autofit = False
table_tech.columns[0].width = Inches(2.2)
table_tech.columns[1].width = Inches(4.3)

# Header row
hdr_cells = table_tech.rows[0].cells
hdr_cells[0].text = "Technical Term"
hdr_cells[1].text = "Viva-Ready Definition & Explanation"
for cell in hdr_cells:
    set_cell_background(cell, "0F172A")
    set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
    for p in cell.paragraphs:
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)

for term, desc in tech_terms:
    row_cells = table_tech.add_row().cells
    row_cells[0].text = term
    row_cells[1].text = desc
    set_cell_background(row_cells[0], "F8FAFC")
    set_cell_background(row_cells[1], "FFFFFF")
    for cell in row_cells:
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        p = cell.paragraphs[0]
        p.runs[0].font.size = Pt(9.5)
        p.runs[0].font.color.rgb = COLOR_PRIMARY
    row_cells[0].paragraphs[0].runs[0].font.bold = True

add_callout(
    "If the examiner asks why you use AST instead of regex: 'Regex is fragile text matching that causes false alarms whenever formatting or comments change. AST understands the syntactic grammar of the code, so it knows with mathematical certainty when an API signature or default value actually changed.'",
    "AST DEFENSE:"
)

# ==============================================================================
# SECTION 3: DEVOPS TERMS DICTIONARY
# ==============================================================================
h3 = doc.add_heading(level=1)
r = h3.add_run("3. Complete DevOps Terms Dictionary")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.color.rgb = COLOR_PRIMARY

devops_terms = [
    ("CI/CD (Continuous Integration / Delivery)", "The automated practice of building, testing, and packaging code every time changes are pushed. DocSync integrates as an automated CI step that validates documentation integrity on every pull request."),
    ("Quality Gate", "A mandatory checkpoint in a CI/CD pipeline that blocks code from merging if quality, security, or coverage checks fail. DocSync acts as a Documentation Quality Gate, preventing stale docs from reaching main."),
    ("Pull Request (PR)", "A developer's formal request to merge new code into the main branch. Pull Requests trigger CI/CD pipelines, and DocSync evaluates the exact commit diff between the base branch and the PR branch."),
    ("GitHub Actions", "GitHub's native CI/CD workflow automation platform. Configured via .github/workflows/docsync-pr.yml, it checks out the repo, executes DocSync, and posts a verification summary on the PR."),
    ("Containerization", "Encapsulating an application and all its dependencies, system libraries, and configs into a self-contained image that runs reliably across any operating system using Docker."),
    ("Multi-Stage Dockerfile", "A best-practice Docker pattern with separate 'builder' and 'runtime' stages. The builder compiles dependencies, while the runtime copies only the final Python wheels, creating a lightweight, secure image."),
    ("Docker Compose", "A multi-container orchestration tool defined in docker-compose.yml. It simplifies launching the application, port mappings, environment variables, and volume mounts with a single command."),
    ("Health Check (HEALTHCHECK)", "An automated Docker probe (curl -f http://localhost:8501/_stcore/health) that periodically checks whether the service is alive and healthy, enabling self-healing container restarts."),
    ("Volume Mounts", "Mapping directories from the host machine into the container (./results, ./demo_output, ./.docsync_cache). This ensures that generated evaluation reports and vector caches persist on disk even when containers stop."),
    ("Self-Healing / Remediation", "Moving beyond passive alert notifications by automatically generating unified diff patches and opening automated fix pull requests using AI bots like Sweep.dev."),
    ("IaaS vs. CaaS", "IaaS (Infrastructure as a Service) is an unmanaged virtual server (like our AWS EC2 Ubuntu instance) where we control the OS and run Ollama. CaaS (Containers as a Service) is a managed container platform (like AWS Fargate or Cloud Run), which we do NOT use in this project."),
]

table_dev = doc.add_table(rows=1, cols=2)
table_dev.alignment = WD_TABLE_ALIGNMENT.CENTER
table_dev.autofit = False
table_dev.columns[0].width = Inches(2.2)
table_dev.columns[1].width = Inches(4.3)

hdr_cells = table_dev.rows[0].cells
hdr_cells[0].text = "DevOps Term"
hdr_cells[1].text = "Meaning & Role in DocSync"
for cell in hdr_cells:
    set_cell_background(cell, "0F172A")
    set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
    for p in cell.paragraphs:
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)

for term, desc in devops_terms:
    row_cells = table_dev.add_row().cells
    row_cells[0].text = term
    row_cells[1].text = desc
    set_cell_background(row_cells[0], "F8FAFC")
    set_cell_background(row_cells[1], "FFFFFF")
    for cell in row_cells:
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        p = cell.paragraphs[0]
        p.runs[0].font.size = Pt(9.5)
        p.runs[0].font.color.rgb = COLOR_PRIMARY
    row_cells[0].paragraphs[0].runs[0].font.bold = True

# ==============================================================================
# SECTION 4: ALL MODELS IN DOCSYNC
# ==============================================================================
doc.add_page_break()
h4 = doc.add_heading(level=1)
r = h4.add_run("4. All AI Models in DocSync & Their Roles")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.color.rgb = COLOR_PRIMARY

models_data = [
    (
        "deepseek-coder:6.7b",
        "Ollama on AWS EC2 (Ubuntu IaaS)",
        "Open-Source Code LLM",
        "Our primary open-source code intelligence model running in the cloud. It performs deep semantic reasoning over changed code, explains why drift occurred, and powers natural-language technical answers in the Repository Code Q&A Bot via HTTP API on port 11434."
    ),
    (
        "gemini-1.5-flash",
        "Google Cloud AI REST API",
        "Proprietary Cloud Model",
        "A commercial high-speed LLM used for multi-model empirical comparison in Tab 3. It demonstrates DocSync's vendor-agnostic architecture, providing fast cloud inference with long-context comprehension."
    ),
    (
        "all-MiniLM-L6-v2",
        "Local PyTorch / Sentence-Transformers",
        "Dense Embedding Model",
        "A lightweight, highly efficient sentence embedding model that converts documentation chunks, docstrings, and search queries into 384-dimensional dense vectors stored in our FAISS vector database."
    ),
    (
        "Fast Mode / FakeChatModel",
        "Native Python ast & rule_based.py",
        "Deterministic Rule Engine",
        "A 100% offline, zero-network engine designed for reliable, instant smoke testing and classroom presentations. It executes in 0.15s, costs $0, requires 0 API keys, and guarantees 0% false alarms on harmless code refactors."
    ),
]

table_mod = doc.add_table(rows=1, cols=4)
table_mod.alignment = WD_TABLE_ALIGNMENT.CENTER
table_mod.autofit = False
table_mod.columns[0].width = Inches(1.5)
table_mod.columns[1].width = Inches(1.4)
table_mod.columns[2].width = Inches(1.3)
table_mod.columns[3].width = Inches(2.3)

hdr_cells = table_mod.rows[0].cells
hdr_cells[0].text = "Model Name"
hdr_cells[1].text = "Deployment / Host"
hdr_cells[2].text = "Model Class"
hdr_cells[3].text = "Role in DocSync"
for cell in hdr_cells:
    set_cell_background(cell, "0F172A")
    set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
    for p in cell.paragraphs:
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(9.5)

for name, host, mclass, role in models_data:
    row_cells = table_mod.add_row().cells
    row_cells[0].text = name
    row_cells[1].text = host
    row_cells[2].text = mclass
    row_cells[3].text = role
    set_cell_background(row_cells[0], "F8FAFC")
    set_cell_background(row_cells[1], "F8FAFC")
    set_cell_background(row_cells[2], "F8FAFC")
    set_cell_background(row_cells[3], "FFFFFF")
    for cell in row_cells:
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.runs[0].font.size = Pt(9)
        p.runs[0].font.color.rgb = COLOR_PRIMARY
    row_cells[0].paragraphs[0].runs[0].font.bold = True

add_callout(
    "If the examiner asks why you use both Ollama on EC2 and Gemini: 'We designed DocSync with a multi-provider LLM Factory pattern. In Tab 3 of our dashboard, we quantitatively compare open-source on-prem models (DeepSeek-Coder via Ollama for code privacy) against commercial cloud APIs (Gemini for fast cloud inference) and rule-based AST methods (zero token cost and sub-second latency).'",
    "MULTI-MODEL ARCHITECTURE:"
)

# ==============================================================================
# SECTION 5: ARCHITECTURE DESIGN & DATA FLOW
# ==============================================================================
h5 = doc.add_heading(level=1)
r = h5.add_run("5. System Architecture & Communication Flow")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.color.rgb = COLOR_PRIMARY

arch_p = doc.add_paragraph()
arch_p.paragraph_format.space_after = Pt(8)
arch_p.add_run(
    "DocSync is architected as a decoupled, microservice-ready system where the user interface, static analysis engine, retrieval index, and AI inference workers communicate across standard networking protocols:\n\n"
    "1. Presentation Tier (Streamlit Dashboard on port 8501):\n"
    "   • Serves the interactive PR Drift Verification Studio, Live Sandbox, and Repository Code Q&A.\n"
    "   • Allows developers to review AST contracts, inspect cited tokens, and apply 1-click remediation patches to disk.\n\n"
    "2. Processing Tier (DocSync Core Engine):\n"
    "   • Ingests Git diffs using git diff base...head to isolate modified line ranges.\n"
    "   • Parses Python abstract syntax trees via docsync/ingest/code_parser.py to extract function contracts.\n"
    "   • Scans markdown files (.md) and in-code docstrings via docsync/ingest/doc_parser.py.\n"
    "   • Indexes text chunks into FAISS vector stores and BM25 lexical tables, merging candidates with Reciprocal Rank Fusion (k=60).\n\n"
    "3. Cloud Inference Tier (AWS EC2 & Gemini):\n"
    "   • An AWS EC2 Ubuntu instance hosts the Ollama inference service at http://<AWS_IP>:11434.\n"
    "   • The local application sends HTTP POST requests with prompt contexts to Ollama's /api/chat endpoint.\n"
    "   • Alternatively, requests route over HTTPS to Google Gemini REST API using GOOGLE_API_KEY.\n\n"
    "4. DevOps & Automation Tier:\n"
    "   • GitHub Actions (.github/workflows/docsync-pr.yml) runs docsync check automatically on pull requests.\n"
    "   • Sweep.dev (sweep.yaml) consumes the unified diff output to open automated draft repair PRs.\n"
    "   • Docker Compose (docker-compose.yml) containerizes the stack with health probes on http://localhost:8501/_stcore/health."
)

# ==============================================================================
# SECTION 6: THE 9-STEP WORKFLOW
# ==============================================================================
doc.add_page_break()
h6 = doc.add_heading(level=1)
r = h6.add_run("6. The 9-Step Pipeline Workflow Explained")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.color.rgb = COLOR_PRIMARY

workflow_steps = [
    ("Stage 1: Ingest & Parse", [
        ("Step 1: PR Triggered", "A pull request is opened on GitHub, or the developer invokes the CLI: docsync check <repo> <base> <head>."),
        ("Step 2: Diff Range Extraction", "git diff base...head analyzes modified files, extracting the exact starting and ending line numbers of altered code."),
        ("Step 3: AST Contract Parsing", "Python's native ast module parses the modified files, identifying which function was touched and extracting its signature, parameter types, and default values."),
    ]),
    ("Stage 2: Retrieve & Judge", [
        ("Step 4: Hybrid Candidate Retrieval", "BM25 searches for exact symbol matches ('fetch_data'), while FAISS searches dense vector embeddings for semantic matches."),
        ("Step 5: Reciprocal Rank Fusion (RRF)", "The dual ranked candidate lists are fused using RRF (k=60), prioritizing documentation chunks that rank highly in both keyword and vector search."),
        ("Step 6: Evidence-Backed Drift Judge", "The judge compares the code contract against candidate documentation. If parameters contradict, it cites exact evidence tokens (E2 vs D1) and flags DRIFT."),
    ]),
    ("Stage 3: Heal & Interact", [
        ("Step 7: Unified Diff Patch Generation", "Python's difflib generates a standard unified diff (- Stale Doc / + Fresh Code) accurately reflecting the updated parameter value."),
        ("Step 8: Automated / 1-Click Remediation", "The patch is applied directly to disk on 1-click in the dashboard, or opened as an automated GitHub fix PR via Sweep.dev."),
        ("Step 9: Interactive Repository Code Q&A", "Developers can interactively query the codebase logic and documentation with verified file and line citations."),
    ]),
]

for stage_title, steps in workflow_steps:
    p_stage = doc.add_paragraph()
    p_stage.paragraph_format.space_before = Pt(8)
    p_stage.paragraph_format.space_after = Pt(2)
    r_s = p_stage.add_run(f"⚡ {stage_title}")
    r_s.font.name = "Arial"
    r_s.font.size = Pt(12)
    r_s.font.bold = True
    r_s.font.color.rgb = COLOR_SECONDARY
    
    for s_name, s_desc in steps:
        p_step = doc.add_paragraph()
        p_step.paragraph_format.space_before = Pt(1)
        p_step.paragraph_format.space_after = Pt(3)
        p_step.paragraph_format.left_indent = Inches(0.2)
        r_sn = p_step.add_run(f"• {s_name}: ")
        r_sn.font.bold = True
        r_sn.font.color.rgb = COLOR_PRIMARY
        r_sd = p_step.add_run(s_desc)
        r_sd.font.color.rgb = COLOR_MUTED

# ==============================================================================
# SECTION 7: VIVA EXAMINER FAQS & WINNING ANSWERS
# ==============================================================================
doc.add_page_break()
h7 = doc.add_heading(level=1)
r = h7.add_run("7. Top 5 Viva Examiner Questions & Winning Answers")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.color.rgb = COLOR_PRIMARY

faqs = [
    (
        "Q1: Why can't developers just remember to update documentation themselves?",
        "Answer: In real-world software engineering, developers work under intense release pressure. While unit tests and linters block broken code, zero tools verify documentation. Over time, code evolves while docs stay stale—leading to onboarding delays, broken client API calls, and developer confusion. DocSync automates this check so documentation maintenance is enforced by CI/CD rather than human memory."
    ),
    (
        "Q2: How does DocSync prevent LLM hallucinations?",
        "Answer: We use a strict 3-tier guardrail: (1) We use AST static analysis to verify the ground truth code contract. (2) We use Hybrid RAG to pass only real repository chunks into the prompt. (3) Our prompt enforces an Evidence Requirement where the LLM must cite the exact code token (E2) against the doc token (D1). If evidence is missing, the model is instructed to output MATCH or UNCERTAIN rather than guessing."
    ),
    (
        "Q3: Why did you deploy Ollama on an AWS EC2 instance?",
        "Answer: Running large code models locally requires significant GPU memory, which developers' laptops may lack. Deploying Ollama with DeepSeek-Coder 6.7B on an AWS EC2 cloud instance decouples compute resources. The local Streamlit app simply sends lightweight HTTP requests over port 11434, fulfilling the DevOps requirement of deploying cloud AI infrastructure."
    ),
    (
        "Q4: What happens if a developer just adds a harmless comment or changes indentation?",
        "Answer: A plain string diff would flag that lines changed, creating a false alarm. But because DocSync uses Python's native AST parser, it compares the semantic function nodes and recognizes that parameters and defaults are identical. In our demo, Commit C0 to C1 proves this by returning MATCH with 0% false alarms."
    ),
    (
        "Q5: What is the benefit of Reciprocal Rank Fusion (RRF) over single search?",
        "Answer: Pure vector search (FAISS) can struggle with exact variable or function names, while pure keyword search (BM25) fails when documentation describes a function using different synonyms. RRF combines both ranked lists using Score = Σ 1/(60 + rank), ensuring the top retrieved documentation chunks have both keyword exactness and semantic relevance."
    ),
]

for q, a in faqs:
    p_q = doc.add_paragraph()
    p_q.paragraph_format.space_before = Pt(8)
    p_q.paragraph_format.space_after = Pt(2)
    r_q = p_q.add_run(q)
    r_q.font.name = "Arial"
    r_q.font.size = Pt(11)
    r_q.font.bold = True
    r_q.font.color.rgb = COLOR_SECONDARY
    
    p_a = doc.add_paragraph()
    p_a.paragraph_format.space_before = Pt(0)
    p_a.paragraph_format.space_after = Pt(6)
    p_a.paragraph_format.left_indent = Inches(0.2)
    r_a = p_a.add_run(a)
    r_a.font.name = "Calibri"
    r_a.font.size = Pt(10)
    r_a.font.color.rgb = COLOR_PRIMARY

# Save document
output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DocSync_Mid_Sem_Viva_and_Presentation_Guide.docx")
doc.save(output_path)
print(f"[OK] Word document successfully created at: {output_path}")
