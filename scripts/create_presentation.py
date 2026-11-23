"""
Script to generate the ultra-premium DocSync Mid-Semester Presentation (.pptx)
Matching the exact 10-slide structure, typography, card layout, and Dark Obsidian aesthetics
of the reference BML Munjal University AI DevOps presentation.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation in Widescreen 16:9 (13.333 x 7.5 inches)
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_slide_layout = prs.slide_layouts[6]

# Color Palette Constants
BG_COLOR = RGBColor(11, 15, 25)         # #0b0f19
CARD_BG = RGBColor(20, 28, 45)          # #141c2d
CARD_BORDER = RGBColor(38, 51, 77)      # #26334d
CARD_BG_ALT = RGBColor(26, 36, 56)      # #1a2438

ACCENT_BLUE = RGBColor(56, 189, 248)    # #38bdf8
ACCENT_INDIGO = RGBColor(129, 140, 248) # #818cf8
ACCENT_GREEN = RGBColor(52, 211, 153)   # #34d399
ACCENT_AMBER = RGBColor(245, 158, 11)   # #f59e0b
ACCENT_RED = RGBColor(239, 68, 68)      # #ef4444

TEXT_WHITE = RGBColor(248, 250, 252)    # #f8fafc
TEXT_MUTED = RGBColor(148, 163, 184)    # #94a3b8
TEXT_DIM = RGBColor(100, 116, 139)      # #64748b

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"
FONT_CODE = "Consolas"

def set_background(slide):
    """Fill slide with dark obsidian background."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = BG_COLOR
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, tag_text, title_text, subtitle_text=None):
    """Add standard top tag, title, and optional subtitle."""
    # Top Tag (e.g. '01 · THE PROBLEM')
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = ACCENT_BLUE

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.7))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(25)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, bg=CARD_BG, border=CARD_BORDER, border_width=1):
    """Add styled rounded rectangle card."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg
    if border:
        card.line.color.rgb = border
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card

# ==============================================================================
# SLIDE 1: TITLE SLIDE (HERO SLIDE)
# ==============================================================================
slide1 = prs.slides.add_slide(blank_slide_layout)
set_background(slide1)

# Top eyebrow tag
tb = slide1.shapes.add_textbox(Inches(0.9), Inches(1.1), Inches(7.5), Inches(0.4))
p = tb.text_frame.paragraphs[0]
p.text = "G R O U P   P R O J E C T   ·   M I D   S E M E S T E R   P R E S E N T A T I O N"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = ACCENT_INDIGO

# Title: DOCSYNC
tb = slide1.shapes.add_textbox(Inches(0.9), Inches(1.5), Inches(7.5), Inches(1.4))
p = tb.text_frame.paragraphs[0]
p.text = "DOCSYNC"
p.font.name = FONT_HEADING
p.font.size = Pt(62)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

# Subtitle
tb = slide1.shapes.add_textbox(Inches(0.9), Inches(3.0), Inches(7.2), Inches(0.8))
p = tb.text_frame.paragraphs[0]
p.text = "Autonomous AI DevOps & Documentation Drift Platform"
p.font.name = FONT_HEADING
p.font.size = Pt(20)
p.font.color.rgb = RGBColor(203, 213, 225)

# Pipeline Tagline
tb = slide1.shapes.add_textbox(Inches(0.9), Inches(3.85), Inches(7.2), Inches(0.4))
p = tb.text_frame.paragraphs[0]
p.text = "Ingest  ·  Parse AST  ·  Hybrid RAG  ·  Judge Drift  ·  Auto-Patch"
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE

# Presented By Card
add_card(slide1, Inches(0.9), Inches(4.7), Inches(7.0), Inches(1.8), bg=CARD_BG, border=CARD_BORDER)
tb = slide1.shapes.add_textbox(Inches(1.15), Inches(4.85), Inches(6.5), Inches(1.5))
tf = tb.text_frame
tf.word_wrap = True
p1 = tf.paragraphs[0]
p1.text = "P R E S E N T E D   B Y"
p1.font.size = Pt(10)
p1.font.bold = True
p1.font.color.rgb = ACCENT_INDIGO

p2 = tf.add_paragraph()
p2.text = "Team DocSync"
p2.font.size = Pt(16)
p2.font.bold = True
p2.font.color.rgb = TEXT_WHITE

p3 = tf.add_paragraph()
p3.text = "Course: Intelligent Developer Tools and AI DevOps Workflows (CSE 4011)"
p3.font.size = Pt(11)
p3.font.color.rgb = TEXT_MUTED

p4 = tf.add_paragraph()
p4.text = "Faculty: Dr. Kiran Khatter  ·  BML Munjal University"
p4.font.size = Pt(11)
p4.font.color.rgb = TEXT_MUTED

# Right Side Steps Ladder (Vertical 5 cards)
steps_data = [
    ("⚡ Ingest", "Git commit diff line ranges", ACCENT_BLUE),
    ("🌳 Parse AST", "Tree-sitter & Python AST contracts", ACCENT_AMBER),
    ("🔍 Retrieve", "Hybrid BM25 + FAISS Vector Store", ACCENT_INDIGO),
    ("⚖️ Judge", "Evidence tokens: E2 vs D1", ACCENT_GREEN),
    ("🛠️ Auto-Patch", "difflib unified diff + Sweep.dev PR", ACCENT_BLUE),
]

for i, (title, sub, color) in enumerate(steps_data):
    y = Inches(1.2 + i * 1.1)
    card = add_card(slide1, Inches(8.5), y, Inches(4.0), Inches(0.95), bg=CARD_BG, border=CARD_BORDER)
    tb = slide1.shapes.add_textbox(Inches(8.75), y + Inches(0.12), Inches(3.5), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = color
    p2 = tf.add_paragraph()
    p2.text = sub
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = TEXT_MUTED

# ==============================================================================
# SLIDE 2: THE PROBLEM (01 · THE PROBLEM)
# ==============================================================================
slide2 = prs.slides.add_slide(blank_slide_layout)
set_background(slide2)
add_header(slide2, "01 · THE PROBLEM", "What happens when code evolves but documentation is left behind?")

# 5 Sequential Cards
prob_cards = [
    ("Code Changes ↑", "functions & params modified", ACCENT_GREEN),
    ("Docs Untouched", "README & docstrings stale", ACCENT_BLUE),
    ("PR Merges", "unit tests pass cleanly", ACCENT_AMBER),
    ("Devs Misled", "wrong defaults & broken calls", ACCENT_RED),
    ("Silent Debt", "developer trust erodes", RGBColor(220, 38, 38)),
]

card_w = Inches(2.15)
card_h = Inches(2.0)
start_x = Inches(0.8)
gap = Inches(0.24)

for i, (title, desc, color) in enumerate(prob_cards):
    x = start_x + i * (card_w + gap)
    y = Inches(1.7)
    add_card(slide2, x, y, card_w, card_h, bg=CARD_BG, border=CARD_BORDER)
    
    tb = slide2.shapes.add_textbox(x + Inches(0.15), y + Inches(0.35), card_w - Inches(0.3), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.alignment = PP_ALIGN.CENTER
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = color
    
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.alignment = PP_ALIGN.CENTER
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_MUTED
    
    # Arrow between cards
    if i < 4:
        tb_arr = slide2.shapes.add_textbox(x + card_w, y + Inches(0.8), gap, Inches(0.4))
        p_arr = tb_arr.text_frame.paragraphs[0]
        p_arr.text = "➔"
        p_arr.alignment = PP_ALIGN.CENTER
        p_arr.font.size = Pt(14)
        p_arr.font.color.rgb = TEXT_DIM

# Bottom Comparison Boxes (2 Columns)
# Left Box
add_card(slide2, Inches(0.8), Inches(4.2), Inches(5.6), Inches(2.6), bg=CARD_BG, border=CARD_BORDER)
tb = slide2.shapes.add_textbox(Inches(1.1), Inches(4.4), Inches(5.0), Inches(2.2))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "A  T R A D I T I O N A L   C I / C D   T E L L S   U S"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = TEXT_DIM

p = tf.add_paragraph()
p.text = "“The build and tests passed.”"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

p = tf.add_paragraph()
p.text = "Linters verify syntax and Pytest validates logic execution — but zero existing CI tools check whether your documentation accurately reflects code reality."
p.font.size = Pt(12)
p.font.color.rgb = TEXT_MUTED

# Right Box (Highlighted Border)
add_card(slide2, Inches(6.8), Inches(4.2), Inches(5.7), Inches(2.6), bg=CARD_BG, border=ACCENT_BLUE, border_width=2)
tb = slide2.shapes.add_textbox(Inches(7.1), Inches(4.4), Inches(5.1), Inches(2.2))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "D E V E L O P E R S   A R E   L E F T   T O   A S K"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE

p = tf.add_paragraph()
p.text = "“Why is the documentation lying?”"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

p = tf.add_paragraph()
p.text = "Did timeout default change from 30s to 60s? Did parameter types invert? Finding documentation drift across hundreds of files remains painful manual work."
p.font.size = Pt(12)
p.font.color.rgb = TEXT_MUTED

# ==============================================================================
# SLIDE 3: MOTIVATION (02 · MOTIVATION)
# ==============================================================================
slide3 = prs.slides.add_slide(blank_slide_layout)
set_background(slide3)
add_header(slide3, "02 · MOTIVATION", "Why DocSync?")

# Workflow 1: Traditional
tb = slide3.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(0.3))
p = tb.text_frame.paragraphs[0]
p.text = "T R A D I T I O N A L   W O R K F L O W"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = TEXT_DIM

trad_steps = ["Code PR", "Unit Tests", "Manual Review", "Doc Drift Merged", "Devs Misled"]
w_step = Inches(2.1)
h_step = Inches(0.9)
for i, s in enumerate(trad_steps):
    x = Inches(0.8) + i * (w_step + Inches(0.3))
    bg = RGBColor(45, 20, 20) if i in [2, 3] else CARD_BG
    bdr = ACCENT_RED if i in [2, 3] else CARD_BORDER
    add_card(slide3, x, Inches(2.0), w_step, h_step, bg=bg, border=bdr)
    
    tb = slide3.shapes.add_textbox(x, Inches(2.2), w_step, Inches(0.5))
    p = tb.text_frame.paragraphs[0]
    p.text = s
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE if i not in [2, 3] else RGBColor(252, 165, 165)
    
    if i < 4:
        tb_arr = slide3.shapes.add_textbox(x + w_step, Inches(2.25), Inches(0.3), Inches(0.4))
        p_arr = tb_arr.text_frame.paragraphs[0]
        p_arr.text = "➔"
        p_arr.alignment = PP_ALIGN.CENTER
        p_arr.font.size = Pt(12)
        p_arr.font.color.rgb = TEXT_DIM

# Workflow 2: DocSync Idea
tb = slide3.shapes.add_textbox(Inches(0.8), Inches(3.2), Inches(11.7), Inches(0.3))
p = tb.text_frame.paragraphs[0]
p.text = "T H E   D O C S Y N C   I D E A"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE

docsync_steps = [
    ("Code PR", CARD_BG, CARD_BORDER, TEXT_WHITE),
    ("AST Contract Diff", CARD_BG, CARD_BORDER, TEXT_WHITE),
    ("Hybrid RAG Search", CARD_BG, ACCENT_INDIGO, ACCENT_INDIGO),
    ("Evidence Judge", CARD_BG, ACCENT_BLUE, ACCENT_BLUE),
    ("Auto-Diff Patch", CARD_BG, ACCENT_GREEN, ACCENT_GREEN),
]
for i, (s, bg, bdr, col) in enumerate(docsync_steps):
    x = Inches(0.8) + i * (w_step + Inches(0.3))
    add_card(slide3, x, Inches(3.6), w_step, h_step, bg=bg, border=bdr, border_width=1.5)
    
    tb = slide3.shapes.add_textbox(x, Inches(3.8), w_step, Inches(0.5))
    p = tb.text_frame.paragraphs[0]
    p.text = s
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = col
    
    if i < 4:
        tb_arr = slide3.shapes.add_textbox(x + w_step, Inches(3.85), Inches(0.3), Inches(0.4))
        p_arr = tb_arr.text_frame.paragraphs[0]
        p_arr.text = "➔"
        p_arr.alignment = PP_ALIGN.CENTER
        p_arr.font.size = Pt(12)
        p_arr.font.color.rgb = ACCENT_BLUE

# Bottom Big Idea Banner
add_card(slide3, Inches(0.8), Inches(5.1), Inches(11.7), Inches(1.7), bg=CARD_BG, border=CARD_BORDER)
tb = slide3.shapes.add_textbox(Inches(1.2), Inches(5.4), Inches(10.9), Inches(1.1))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "We wanted to move from passive documentation debt to automated, repository-aware self-healing documentation."
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

p2 = tf.add_paragraph()
p2.text = "By coupling Python AST static analysis with dense semantic retrieval, DocSync acts as an automated quality gate that stops stale documentation before it merges to main."
p2.font.size = Pt(12)
p2.font.color.rgb = TEXT_MUTED

# ==============================================================================
# SLIDE 4: THE SOLUTION (03 · THE SOLUTION)
# ==============================================================================
slide4 = prs.slides.add_slide(blank_slide_layout)
set_background(slide4)
add_header(
    slide4,
    "03 · THE SOLUTION",
    "What is DocSync?",
    "An AI DevOps platform that detects documentation drift in PRs, explains the mismatch with cited evidence, and generates self-healing patches."
)

# Left Side 6 Numbered Steps
sol_steps = [
    ("1", "Ingests Git commit diffs to isolate changed line ranges & symbols"),
    ("2", "Extracts function AST contracts (signatures, parameter types, defaults)"),
    ("3", "Retrieves candidate docs via Hybrid Search (BM25 + FAISS Vector Store)"),
    ("4", "Evaluates MATCH vs. DRIFT with hallucination-free cited tokens (E2 vs D1)"),
    ("5", "Generates unified diff patches & triggers Sweep.dev automated PR repair"),
    ("6", "Provides interactive Repository Code Q&A Bot with exact line citations"),
]

for i, (num, text) in enumerate(sol_steps):
    y = Inches(2.0 + i * 0.82)
    # Circle badge
    circ = slide4.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), y, Inches(0.48), Inches(0.48))
    circ.fill.solid()
    circ.fill.fore_color.rgb = RGBColor(30, 41, 59)
    circ.line.color.rgb = ACCENT_BLUE
    circ.line.width = Pt(1)
    p_num = circ.text_frame.paragraphs[0]
    p_num.text = num
    p_num.alignment = PP_ALIGN.CENTER
    p_num.font.size = Pt(12)
    p_num.font.bold = True
    p_num.font.color.rgb = ACCENT_BLUE
    
    # Text
    tb = slide4.shapes.add_textbox(Inches(1.45), y + Inches(0.04), Inches(5.8), Inches(0.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(12.5)
    p.font.color.rgb = TEXT_WHITE

# Right Side Circular / Loop Visual
add_card(slide4, Inches(7.8), Inches(2.0), Inches(4.7), Inches(4.8), bg=CARD_BG, border=CARD_BORDER)

# Central Circle
center_circ = slide4.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.35), Inches(3.6), Inches(1.6), Inches(1.6))
center_circ.fill.solid()
center_circ.fill.fore_color.rgb = RGBColor(15, 23, 42)
center_circ.line.color.rgb = ACCENT_INDIGO
center_circ.line.width = Pt(2)
tf = center_circ.text_frame
p1 = tf.paragraphs[0]
p1.text = "DocSync"
p1.alignment = PP_ALIGN.CENTER
p1.font.size = Pt(14)
p1.font.bold = True
p1.font.color.rgb = TEXT_WHITE
p2 = tf.add_paragraph()
p2.text = "Loop"
p2.alignment = PP_ALIGN.CENTER
p2.font.size = Pt(12)
p2.font.color.rgb = ACCENT_BLUE

# Surrounding Stage Nodes
loop_nodes = [
    ("1 Ingest", Inches(9.4), Inches(2.3), ACCENT_BLUE),
    ("2 Parse AST", Inches(10.9), Inches(3.1), ACCENT_AMBER),
    ("3 Retrieve", Inches(10.6), Inches(4.9), ACCENT_INDIGO),
    ("4 Judge", Inches(8.8), Inches(5.3), ACCENT_RED),
    ("5 Auto-Patch", Inches(8.1), Inches(3.6), ACCENT_GREEN),
]
for text, x, y, col in loop_nodes:
    node = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(1.45), Inches(0.65))
    node.fill.solid()
    node.fill.fore_color.rgb = RGBColor(30, 41, 59)
    node.line.color.rgb = col
    node.line.width = Pt(1.5)
    p = node.text_frame.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = col

# ==============================================================================
# SLIDE 5: TECHNOLOGY STACK (04 · TECHNOLOGY)
# ==============================================================================
slide5 = prs.slides.add_slide(blank_slide_layout)
set_background(slide5)
add_header(slide5, "04 · TECHNOLOGY", "Technology Stack")

tech_items = [
    ("FRONTEND", "Streamlit · Dark Obsidian Glassmorphism", "Interactive Dashboard, live diffs, served on port 8501", ACCENT_BLUE),
    ("BACKEND / PARSER", "Python 3.10 · Native ast Engine", "Parses code symbols, line ranges & signature contracts", ACCENT_AMBER),
    ("VECTOR RETRIEVAL", "FAISS · all-MiniLM-L6-v2", "384-dimensional dense semantic embeddings for similarity", ACCENT_INDIGO),
    ("LEXICAL RETRIEVAL", "BM25 Search + RRF (k=60)", "Reciprocal Rank Fusion merges keyword & vector candidates", ACCENT_GREEN),
    ("AI INFERENCE", "Ollama (AWS EC2) · Google Gemini", "DeepSeek-Coder 6.7B cloud worker + Gemini 1.5 Flash", ACCENT_INDIGO),
    ("CI/CD AUTOMATION", "GitHub Actions · Sweep.dev", "Automated PR drift evaluation + automated fix pull requests", ACCENT_BLUE),
    ("REMEDIATION ENGINE", "Python difflib Unified Diff", "Generates self-healing unified diff patches on disk", ACCENT_GREEN),
    ("INFRASTRUCTURE", "Docker · Docker Compose", "Multi-stage Dockerfile with live health checks & volumes", ACCENT_AMBER),
]

col_w = Inches(5.7)
row_h = Inches(1.2)
for idx, (cat, title, sub, col) in enumerate(tech_items):
    c_idx = idx % 2
    r_idx = idx // 2
    x = Inches(0.8) + c_idx * (col_w + Inches(0.3))
    y = Inches(1.6) + r_idx * (row_h + Inches(0.18))
    
    add_card(slide5, x, y, col_w, row_h, bg=CARD_BG, border=CARD_BORDER)
    
    # Category tag badge
    badge = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), y + Inches(0.18), Inches(1.6), Inches(0.3))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(30, 41, 59)
    badge.line.color.rgb = col
    p_b = badge.text_frame.paragraphs[0]
    p_b.text = cat
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(8.5)
    p_b.font.bold = True
    p_b.font.color.rgb = col
    
    # Title & Sub
    tb = slide5.shapes.add_textbox(x + Inches(1.95), y + Inches(0.12), Inches(3.6), Inches(0.95))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf.add_paragraph()
    p2.text = sub
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED

# ==============================================================================
# SLIDE 6: SYSTEM ARCHITECTURE (05 · ARCHITECTURE)
# ==============================================================================
slide6 = prs.slides.add_slide(blank_slide_layout)
set_background(slide6)
add_header(slide6, "05 · ARCHITECTURE", "System Architecture")

# Central Backend Box
add_card(slide6, Inches(4.3), Inches(1.7), Inches(4.7), Inches(3.6), bg=CARD_BG, border=ACCENT_INDIGO, border_width=2)
tb = slide6.shapes.add_textbox(Inches(4.5), Inches(1.85), Inches(4.3), Inches(0.5))
p = tb.text_frame.paragraphs[0]
p.text = "DocSync Core Pipeline Engine"
p.alignment = PP_ALIGN.CENTER
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = ACCENT_INDIGO

modules = [
    ("Git Change Detector", "maps commit diff line ranges"),
    ("AST Contract Engine", "parses signatures & defaults"),
    ("Hybrid Search (RRF)", "BM25 + FAISS Vector Index"),
    ("Evidence-Backed Judge", "hallucination-free reasoning"),
]
for i, (m_title, m_desc) in enumerate(modules):
    my = Inches(2.45 + i * 0.65)
    add_card(slide6, Inches(4.6), my, Inches(4.1), Inches(0.55), bg=RGBColor(26, 36, 56), border=CARD_BORDER)
    tb = slide6.shapes.add_textbox(Inches(4.7), my + Inches(0.08), Inches(3.9), Inches(0.4))
    tf = tb.text_frame
    p1 = tf.paragraphs[0]
    p1.text = f"{m_title}: "
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = p1.add_run()
    p2.text = m_desc
    p2.font.bold = False
    p2.font.color.rgb = TEXT_MUTED

# Left Side Components (Dashboard & CI/CD)
# Dashboard
add_card(slide6, Inches(0.8), Inches(1.7), Inches(2.9), Inches(1.6), bg=CARD_BG, border=CARD_BORDER)
tb = slide6.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(2.5), Inches(1.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Web Dashboard"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE
p = tf.add_paragraph()
p.text = "Streamlit · Port :8501"
p.font.size = Pt(11)
p.font.color.rgb = TEXT_MUTED
p = tf.add_paragraph()
p.text = "PR Drift Studio + RAG Q&A"
p.font.size = Pt(10)
p.font.color.rgb = TEXT_DIM

# CI/CD Runner
add_card(slide6, Inches(0.8), Inches(3.7), Inches(2.9), Inches(1.6), bg=CARD_BG, border=CARD_BORDER)
tb = slide6.shapes.add_textbox(Inches(1.0), Inches(3.85), Inches(2.5), Inches(1.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "CI/CD & Remediation"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = ACCENT_GREEN
p = tf.add_paragraph()
p.text = "GitHub Actions Workflow"
p.font.size = Pt(11)
p.font.color.rgb = TEXT_MUTED
p = tf.add_paragraph()
p.text = "Sweep.dev Auto-Fix PRs"
p.font.size = Pt(10)
p.font.color.rgb = TEXT_DIM

# Right Side Components (AI Inference & Memory/Cache)
# AI Inference Tier
add_card(slide6, Inches(9.6), Inches(1.7), Inches(2.9), Inches(1.6), bg=CARD_BG, border=CARD_BORDER)
tb = slide6.shapes.add_textbox(Inches(9.8), Inches(1.85), Inches(2.5), Inches(1.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "AI Inference Tier"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = ACCENT_AMBER
p = tf.add_paragraph()
p.text = "AWS EC2 Ubuntu (Ollama)"
p.font.size = Pt(11)
p.font.color.rgb = TEXT_MUTED
p = tf.add_paragraph()
p.text = "DeepSeek-Coder 6.7B (:11434)"
p.font.size = Pt(10)
p.font.color.rgb = TEXT_DIM

# Vector Store & Results Cache
add_card(slide6, Inches(9.6), Inches(3.7), Inches(2.9), Inches(1.6), bg=CARD_BG, border=CARD_BORDER)
tb = slide6.shapes.add_textbox(Inches(9.8), Inches(3.85), Inches(2.5), Inches(1.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Knowledge Storage"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = ACCENT_INDIGO
p = tf.add_paragraph()
p.text = "FAISS Vector Store"
p.font.size = Pt(11)
p.font.color.rgb = TEXT_MUTED
p = tf.add_paragraph()
p.text = "Results JSON & Disk Cache"
p.font.size = Pt(10)
p.font.color.rgb = TEXT_DIM

# Bottom Architecture Note
tb = slide6.shapes.add_textbox(Inches(0.8), Inches(5.7), Inches(11.7), Inches(0.5))
p = tb.text_frame.paragraphs[0]
p.text = "Observability Suite: Dockerized multi-stage container with live health checks (:8501/_stcore/health) and mounted volumes for results and cache."
p.alignment = PP_ALIGN.CENTER
p.font.size = Pt(11)
p.font.italic = True
p.font.color.rgb = TEXT_MUTED

# ==============================================================================
# SLIDE 7: WORKFLOW (06 · WORKFLOW)
# ==============================================================================
slide7 = prs.slides.add_slide(blank_slide_layout)
set_background(slide7)
add_header(slide7, "06 · WORKFLOW", "How the System Works")

workflow_rows = [
    ("INGEST & PARSE", [
        ("1", "Choose Target PR", "GitHub Actions or Git commit hash range"),
        ("2", "Extract Diff Range", "git diff isolates modified lines in .py files"),
        ("3", "Parse AST Contract", "Python ast maps function signature & defaults"),
    ]),
    ("RETRIEVE & JUDGE", [
        ("4", "Hybrid Retrieval", "BM25 keyword search + FAISS dense embeddings"),
        ("5", "Rank via RRF (k=60)", "Combines top candidate docstrings & guides"),
        ("6", "Evidence Judge", "Detects mismatch & cites tokens (E2 vs D1)"),
    ]),
    ("REPAIR & VERIFY", [
        ("7", "Unified Diff Patch", "difflib creates self-healing unified diff"),
        ("8", "1-Click Disk Patch", "Synchronizes documentation on host disk"),
        ("9", "Repository Q&A", "Answers codebase questions with citations"),
    ]),
]

for r_idx, (cat_name, steps) in enumerate(workflow_rows):
    y_base = Inches(1.7 + r_idx * 1.7)
    
    # Left Category Label
    tb_cat = slide7.shapes.add_textbox(Inches(0.8), y_base + Inches(0.4), Inches(1.8), Inches(0.6))
    p_c = tb_cat.text_frame.paragraphs[0]
    p_c.text = cat_name
    p_c.font.size = Pt(10.5)
    p_c.font.bold = True
    p_c.font.color.rgb = ACCENT_BLUE if r_idx == 0 else (ACCENT_INDIGO if r_idx == 1 else ACCENT_GREEN)
    
    # 3 Steps in row
    for s_idx, (num, title, desc) in enumerate(steps):
        x = Inches(2.7) + s_idx * Inches(3.4)
        add_card(slide7, x, y_base, Inches(3.1), Inches(1.35), bg=CARD_BG, border=CARD_BORDER)
        
        # Number badge
        circ = slide7.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.15), y_base + Inches(0.15), Inches(0.35), Inches(0.35))
        circ.fill.solid()
        circ.fill.fore_color.rgb = RGBColor(30, 41, 59)
        circ.line.color.rgb = ACCENT_BLUE
        p_n = circ.text_frame.paragraphs[0]
        p_n.text = num
        p_n.alignment = PP_ALIGN.CENTER
        p_n.font.size = Pt(10)
        p_n.font.bold = True
        p_n.font.color.rgb = ACCENT_BLUE
        
        # Text
        tb = slide7.shapes.add_textbox(x + Inches(0.6), y_base + Inches(0.12), Inches(2.35), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_MUTED

# ==============================================================================
# SLIDE 8: DEMO (07 · DEMO)
# ==============================================================================
slide8 = prs.slides.add_slide(blank_slide_layout)
set_background(slide8)
add_header(slide8, "07 · DEMO", "Prototype Demonstration")

# Left Column: Demo Script Steps
demo_steps = [
    ("1", "Launch Streamlit Dashboard on port 8501"),
    ("2", "Run Deterministic 5-Min Demo (scripts/run_demo.py)"),
    ("3", "Inspect Commit C0 -> C1 (Harmless Refactor = MATCH)"),
    ("4", "Detect Commit C1 -> C2 (timeout=30 -> 60 = DRIFT!)"),
    ("5", "Verify Cited Evidence Tokens (E2: Code 60 vs D1: Doc 30)"),
    ("6", "Apply 1-Click Unified Diff Remediation Patch"),
    ("7", "Query Repository Code Q&A Bot with Source Citations"),
]

for i, (num, desc) in enumerate(demo_steps):
    y = Inches(1.7 + i * 0.72)
    circ = slide8.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), y, Inches(0.42), Inches(0.42))
    circ.fill.solid()
    circ.fill.fore_color.rgb = RGBColor(30, 41, 59)
    circ.line.color.rgb = ACCENT_BLUE
    p = circ.text_frame.paragraphs[0]
    p.text = num
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    
    tb = slide8.shapes.add_textbox(Inches(1.35), y + Inches(0.04), Inches(4.5), Inches(0.45))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = desc
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

# Right Column: Live System Mockup Card
add_card(slide8, Inches(6.2), Inches(1.7), Inches(6.3), Inches(5.1), bg=CARD_BG, border=CARD_BORDER)

# Top Bar inside mockup
tb = slide8.shapes.add_textbox(Inches(6.4), Inches(1.85), Inches(5.9), Inches(0.4))
p = tb.text_frame.paragraphs[0]
p.text = "🔍 Pull Request Documentation Drift Verification Studio"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

# 4 Stat Cards in Mockup
stats = [("FAST", "MODE", ACCENT_BLUE), ("2", "DRIFT DETECTED", ACCENT_RED), ("0", "CLEAN MATCH", ACCENT_GREEN), ("0.159s", "LATENCY", ACCENT_AMBER)]
for s_idx, (val, lbl, col) in enumerate(stats):
    sx = Inches(6.4) + s_idx * Inches(1.45)
    add_card(slide8, sx, Inches(2.35), Inches(1.35), Inches(0.85), bg=RGBColor(26, 36, 56), border=CARD_BORDER)
    tb = slide8.shapes.add_textbox(sx, Inches(2.4), Inches(1.35), Inches(0.7))
    tf = tb.text_frame
    p1 = tf.paragraphs[0]
    p1.text = val
    p1.alignment = PP_ALIGN.CENTER
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = col
    p2 = tf.add_paragraph()
    p2.text = lbl
    p2.alignment = PP_ALIGN.CENTER
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = TEXT_MUTED

# Drift Incident Detail Card in Mockup
add_card(slide8, Inches(6.4), Inches(3.35), Inches(5.9), Inches(1.8), bg=RGBColor(26, 36, 56), border=CARD_BORDER)
tb = slide8.shapes.add_textbox(Inches(6.55), Inches(3.45), Inches(5.6), Inches(1.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "🔴 Incident #1: fetch_data() in client.py — DRIFT (Confidence: 1.00)"
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = RGBColor(248, 113, 113)

p = tf.add_paragraph()
p.text = "Code Contract (AST): def fetch_data(url: str, timeout: int = 60) -> dict"
p.font.size = Pt(9.5)
p.font.name = FONT_CODE
p.font.color.rgb = ACCENT_INDIGO

p = tf.add_paragraph()
p.text = "Target Documentation: 'The fetch_data timeout defaults to 30 seconds.'"
p.font.size = Pt(9.5)
p.font.name = FONT_CODE
p.font.color.rgb = ACCENT_AMBER

p = tf.add_paragraph()
p.text = "Evidence Cited: E2 (Code 60) vs D1 (Doc 30) | difflib Unified Diff Generated"
p.font.size = Pt(9.5)
p.font.color.rgb = TEXT_MUTED

# Patch Box in Mockup
add_card(slide8, Inches(6.4), Inches(5.25), Inches(5.9), Inches(1.35), bg=RGBColor(15, 23, 42), border=ACCENT_GREEN, border_width=1.5)
tb = slide8.shapes.add_textbox(Inches(6.55), Inches(5.35), Inches(5.6), Inches(1.1))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "⚡ Unified Diff Remediation Patch:"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = ACCENT_GREEN

p = tf.add_paragraph()
p.text = "- The fetch_data timeout defaults to 30 seconds."
p.font.size = Pt(9.5)
p.font.name = FONT_CODE
p.font.color.rgb = RGBColor(248, 113, 113)

p = tf.add_paragraph()
p.text = "+ The fetch_data timeout defaults to 60 seconds."
p.font.size = Pt(9.5)
p.font.name = FONT_CODE
p.font.color.rgb = RGBColor(74, 222, 128)

# ==============================================================================
# SLIDE 9: FUTURE SCOPE (08 · NEXT STEPS)
# ==============================================================================
slide9 = prs.slides.add_slide(blank_slide_layout)
set_background(slide9)
add_header(slide9, "08 · NEXT STEPS", "Future Scope (A3 Milestone & Beyond)")

# Top right pill: PLANNED FOR FULL RELEASE
pill = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.0), Inches(0.85), Inches(2.5), Inches(0.4))
pill.fill.solid()
pill.fill.fore_color.rgb = RGBColor(40, 30, 15)
pill.line.color.rgb = ACCENT_AMBER
p = pill.text_frame.paragraphs[0]
p.text = "PLANNED FOR FULL RELEASE"
p.alignment = PP_ALIGN.CENTER
p.font.size = Pt(9)
p.font.bold = True
p.font.color.rgb = ACCENT_AMBER

future_items = [
    ("01", "Multi-Language AST Support", "Extend Tree-sitter symbol parsing beyond Python to TypeScript, Go, Java, and Rust for polyglot microservice repos.", ["TYPESCRIPT", "GO", "JAVA", "RUST"], ACCENT_BLUE),
    ("02", "Inline GitHub PR Commenting", "Post inline PR review suggestions directly on drifted documentation lines with 1-click GitHub Commit Suggestion buttons.", ["GITHUB API", "INLINE COMMENTS", "OCTOKIT"], ACCENT_AMBER),
    ("03", "Live Documentation Server Sync", "Synchronize verified doc patches directly into live hosted static doc engines (Sphinx, MkDocs, Docusaurus) on merge.", ["MKDOCS", "SPHINX", "DOCUSAURUS"], ACCENT_INDIGO),
    ("04", "Monorepo Call-Graph Tracking", "Integrate Sourcegraph LSIF code-intel to trace caller references and downstream consumers across massive monorepos.", ["SOURCEGRAPH", "CALL GRAPH", "LSIF"], ACCENT_GREEN),
]

card_w = Inches(5.7)
card_h = Inches(2.3)
for idx, (num, title, desc, badges, col) in enumerate(future_items):
    c_idx = idx % 2
    r_idx = idx // 2
    x = Inches(0.8) + c_idx * (card_w + Inches(0.3))
    y = Inches(1.8) + r_idx * (card_h + Inches(0.3))
    
    add_card(slide9, x, y, card_w, card_h, bg=CARD_BG, border=CARD_BORDER)
    
    # Number tag
    tb_n = slide9.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2), Inches(0.5), Inches(0.4))
    p = tb_n.text_frame.paragraphs[0]
    p.text = num
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = col
    
    # Title & Desc
    tb = slide9.shapes.add_textbox(x + Inches(0.85), y + Inches(0.2), card_w - Inches(1.1), Inches(1.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_MUTED
    
    # Badges at bottom of card
    by = y + Inches(1.7)
    for b_i, b_text in enumerate(badges):
        bx = x + Inches(0.85) + b_i * Inches(1.1)
        b_shape = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, Inches(1.0), Inches(0.3))
        b_shape.fill.solid()
        b_shape.fill.fore_color.rgb = RGBColor(30, 41, 59)
        b_shape.line.color.rgb = CARD_BORDER
        p_b = b_shape.text_frame.paragraphs[0]
        p_b.text = b_text
        p_b.alignment = PP_ALIGN.CENTER
        p_b.font.size = Pt(7.5)
        p_b.font.bold = True
        p_b.font.color.rgb = TEXT_MUTED

# ==============================================================================
# SLIDE 10: CONCLUSION & THANK YOU (CONCLUSION)
# ==============================================================================
slide10 = prs.slides.add_slide(blank_slide_layout)
set_background(slide10)

# Top Eyebrow
tb = slide10.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(0.4))
p = tb.text_frame.paragraphs[0]
p.text = "C O N C L U S I O N"
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = ACCENT_INDIGO

# Hero Statement
tb = slide10.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.7), Inches(1.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "DocSync turns static, rotting documentation into a living, repository-aware self-healing feedback loop."
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

# Pipeline Pills
pills = [
    ("Ingest Diff", ACCENT_BLUE),
    ("Parse AST", ACCENT_AMBER),
    ("Hybrid Search", ACCENT_INDIGO),
    ("Judge Drift", ACCENT_RED),
    ("Auto-Patch", ACCENT_GREEN),
]
pill_w = Inches(1.8)
for i, (p_text, col) in enumerate(pills):
    px = Inches(0.8) + i * (pill_w + Inches(0.55))
    py = Inches(3.4)
    p_box = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, py, pill_w, Inches(0.55))
    p_box.fill.solid()
    p_box.fill.fore_color.rgb = RGBColor(26, 36, 56)
    p_box.line.color.rgb = col
    p_box.line.width = Pt(1.5)
    p = p_box.text_frame.paragraphs[0]
    p.text = p_text
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = col
    
    if i < 4:
        tb_arr = slide10.shapes.add_textbox(px + pill_w, py + Inches(0.08), Inches(0.55), Inches(0.4))
        p_arr = tb_arr.text_frame.paragraphs[0]
        p_arr.text = "➔"
        p_arr.alignment = PP_ALIGN.CENTER
        p_arr.font.size = Pt(14)
        p_arr.font.color.rgb = TEXT_DIM

# Big Thank You
tb = slide10.shapes.add_textbox(Inches(0.8), Inches(4.7), Inches(11.7), Inches(1.1))
p = tb.text_frame.paragraphs[0]
p.text = "Thank You"
p.font.size = Pt(48)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

# Subtitle / Q&A Prompt
tb = slide10.shapes.add_textbox(Inches(0.8), Inches(5.85), Inches(11.7), Inches(0.5))
p = tb.text_frame.paragraphs[0]
p.text = "Questions & Discussion  ·  DocSync AI DevOps Documentation Intelligence Platform"
p.font.size = Pt(14)
p.font.color.rgb = ACCENT_BLUE

# Save presentation
output_pptx = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DocSync_Mid_Sem_Presentation.pptx")
prs.save(output_pptx)
print(f"[OK] Presentation successfully created at: {output_pptx}")
