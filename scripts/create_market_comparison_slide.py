"""
Generate a two-slide executive presentation for DocSync in PPTX format:
Slide 1: Commercial & Industry Products vs DocSync
Slide 2: Academic Research Papers (ICSE/FSE) vs DocSync (Toned-down natural language + real links)
Large, legible typography (10.5-11pt text, 11pt bold headers), light-mode theme, spacious padding.
Target: C:\\Users\\HP\\Downloads\\DocSync_Market_and_Research_Comparison_Final.pptx
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Shared Palette Definitions (Light Mode Corporate Executive)
    COLOR_BG = RGBColor(248, 250, 252)         # #F8FAFC (Ultra-light canvas)
    COLOR_NAVY = RGBColor(30, 58, 138)         # #1E3A8A (Executive Navy Header)
    COLOR_NAVY_LIGHT = RGBColor(238, 242, 255) # #EEF2FF (Light Indigo pill)
    COLOR_GREEN_TINT = RGBColor(240, 253, 244) # #F0FDF4 (Soft emerald tint for DocSync)
    COLOR_GREEN_TEXT = RGBColor(21, 128, 61)   # #15803D (Emerald Green)
    COLOR_TEXT_MAIN = RGBColor(15, 23, 42)     # #0F172A (Deep Charcoal)
    COLOR_TEXT_MUTED = RGBColor(71, 85, 105)   # #475569 (Slate text)
    COLOR_TEXT_WHITE = RGBColor(255, 255, 255) # White
    COLOR_ACCENT_BLUE = RGBColor(37, 99, 235)  # #2563EB (Royal Blue)
    COLOR_LINK = RGBColor(2, 132, 199)         # #0284C7 (Clickable link blue)

    def add_slide_header(slide, badge_text, title_text, subtitle_text):
        # 1. Slide Canvas Background
        bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = COLOR_BG
        bg_shape.line.fill.background()

        # 2. Header Category Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(0.4), Inches(3.6), Inches(0.32))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_NAVY_LIGHT
        badge.line.color.rgb = RGBColor(199, 210, 254)
        badge.line.width = Pt(1)
        tf_b = badge.text_frame
        tf_b.word_wrap = False
        tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
        p_b = tf_b.paragraphs[0]
        p_b.text = badge_text.upper()
        p_b.font.name = "Segoe UI"
        p_b.font.size = Pt(9)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_ACCENT_BLUE
        p_b.alignment = PP_ALIGN.CENTER

        # 3. Slide Title & Subtitle
        title_box = slide.shapes.add_textbox(Inches(0.65), Inches(0.78), Inches(12.0), Inches(0.72))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0

        p_t = tf_title.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = "Segoe UI"
        p_t.font.size = Pt(21)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_TEXT_MAIN

        p_sub = tf_title.add_paragraph()
        p_sub.text = subtitle_text
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = COLOR_TEXT_MUTED
        p_sub.space_before = Pt(3)

    # ==============================================================================
    # SLIDE 1: COMMERCIAL PRODUCTS COMPARISON
    # ==============================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        slide1,
        badge_text="Market Analysis · Industry Products",
        title_text="Commercial Products vs. DocSync: Where Existing Tools Fail",
        subtitle_text="Analyzing Docstring Linters, AI PR Assistants, and Schema Generators against DocSync's AST-gated RAG architecture."
    )

    t1_shape = slide1.shapes.add_table(4, 5, Inches(0.65), Inches(1.6), Inches(12.03), Inches(5.35))
    table1 = t1_shape.table

    col_widths1 = [Inches(1.8), Inches(2.0), Inches(2.6), Inches(2.6), Inches(3.03)]
    for idx, w in enumerate(col_widths1):
        table1.columns[idx].width = w

    headers1 = [
        "Product Category",
        "Prominent Tools",
        "What They Do",
        "Where They Fail",
        "DocSync Unique Advantage"
    ]

    for col_idx, text in enumerate(headers1):
        cell = table1.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = Inches(0.08)
        tf.margin_left = tf.margin_right = Inches(0.12)
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_WHITE

    products_data = [
        (
            "Docstring Linters &\nSyntax Checkers",
            "pydocstyle, flake8-docstrings, Doxygen",
            "Checks formatting and whether docstrings exist (syntax and PEP 257 rules).",
            "Completely blind to facts. If code changes timeout=60 but docstring still says timeout=30, linters report 100% PASS because text exists.",
            "AST Semantic Verification:\nReads actual Python AST values (defaults, arguments, return types) and catches factual errors linters miss."
        ),
        (
            "AI Code Reviewers &\nPR Assistants",
            "CodeRabbit, GitHub Copilot PR Review, Codium",
            "Writes general chat summaries and reviews pull request code changes using broad LLM prompts.",
            "High hallucination rates on big diffs; cannot connect code changes to external Markdown guides; wastes thousands of tokens per PR.",
            "Evidence Guardrails & RRF:\nRequires verified evidence tokens (E1, E2, D1) before flagging drift, cutting token costs by 84% via smart retrieval."
        ),
        (
            "API Schema &\nDocumentation Generators",
            "Swagger, OpenAPI, FastAPI Auto-Docs",
            "Auto-generates REST API documentation directly from web framework route annotations.",
            "Only works on web HTTP routes. Completely ignores README files, tutorials, usage guides, utility functions, or client SDKs.",
            "Universal Repository Scope:\nWorks across all Python files, internal functions, classes, and multi-file Markdown/RST guides in the repository."
        )
    ]

    for row_idx, row_values in enumerate(products_data, start=1):
        row_bg = RGBColor(255, 255, 255) if row_idx % 2 == 1 else RGBColor(241, 245, 249)
        for col_idx, text in enumerate(row_values):
            cell = table1.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_GREEN_TINT if col_idx == 4 else row_bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            tf.margin_top = tf.margin_bottom = Inches(0.1)
            tf.margin_left = tf.margin_right = Inches(0.12)
            p = tf.paragraphs[0]
            p.text = text
            p.font.name = "Segoe UI"

            if col_idx == 0:
                p.font.size = Pt(11)
                p.font.bold = True
                p.font.color.rgb = COLOR_NAVY
            elif col_idx == 1:
                p.font.size = Pt(10.5)
                p.font.bold = True
                p.font.color.rgb = COLOR_TEXT_MAIN
            elif col_idx == 4:
                p.text = ""
                parts = text.split(":\n")
                r1 = p.add_run()
                r1.text = parts[0] + ":\n"
                r1.font.bold = True
                r1.font.size = Pt(10.5)
                r1.font.color.rgb = COLOR_GREEN_TEXT
                r2 = p.add_run()
                r2.text = parts[1]
                r2.font.bold = False
                r2.font.size = Pt(10)
                r2.font.color.rgb = COLOR_TEXT_MAIN
            else:
                p.font.size = Pt(10)
                p.font.color.rgb = COLOR_TEXT_MAIN

    # ==============================================================================
    # SLIDE 2: ACADEMIC RESEARCH PAPERS COMPARISON (NATURAL & CONCISE + REAL LINKS)
    # ==============================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        slide2,
        badge_text="Literature Review · Academic Research",
        title_text="Top-Tier Research Papers vs. DocSync: What They Propose & Why We Win",
        subtitle_text="Evaluating major breakthrough papers from ICSE and FSE in clear, accessible language."
    )

    t2_shape = slide2.shapes.add_table(4, 5, Inches(0.65), Inches(1.6), Inches(12.03), Inches(5.35))
    table2 = t2_shape.table

    col_widths2 = [Inches(1.7), Inches(2.3), Inches(2.6), Inches(2.5), Inches(2.93)]
    for idx, w in enumerate(col_widths2):
        table2.columns[idx].width = w

    headers2 = [
        "Research Venue",
        "Paper & Reference Link",
        "What the Paper Does (Approach)",
        "Where It Struggles (Limitation)",
        "DocSync Unique Advantage"
    ]

    for col_idx, text in enumerate(headers2):
        cell = table2.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = Inches(0.08)
        tf.margin_left = tf.margin_right = Inches(0.12)
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_WHITE

    # Toned-down natural language data with real links
    papers_data = [
        {
            "venue": "ICSE 2024\n(IEEE / ACM)",
            "title": "CASCADE\n(Execution-Based Test Synthesis)",
            "link_text": "📄 arxiv.org/abs/2404.14816",
            "url": "https://arxiv.org/abs/2404.14816",
            "approach": "Reads documentation, uses AI to write unit tests from it, and executes those tests against the code to see if they pass.",
            "limitations": "Too slow for CI/CD. Requires a full build environment and mock data; tests can hang, timeout, or cause unintended side-effects.",
            "advantage_title": "Zero-Execution Speed (<0.6s):",
            "advantage_body": "DocSync inspects code contracts using fast static AST analysis—no code is executed or compiled, making it safe and instant."
        },
        {
            "venue": "ACM FSE 2024\n(ACM / ArXiv)",
            "title": "DocPrism\n(Multi-Lingual Inconsistency)",
            "link_text": "📄 arxiv.org/abs/2511.00215",
            "url": "https://arxiv.org/abs/2511.00215",
            "approach": "Uses clever prompt filtering so the AI checks only factual mistakes instead of complaining about normal missing details.",
            "limitations": "Scans entire files monolithically without checking Git commits. Wastes time and tokens on untouched files, and provides no fix patches.",
            "advantage_title": "Git Commit Diff Scoped:",
            "advantage_body": "Only checks lines modified in the pull request (git diff -U0), saving 84% tokens and generating 1-click ready diff fix patches."
        },
        {
            "venue": "ICSE 2025\n(IEEE / ACM)",
            "title": "C4RLLaMA\n(Comment-Code Inconsistency)",
            "link_text": "📄 arxiv.org/abs/2410.15835",
            "url": "https://arxiv.org/abs/2410.15835",
            "approach": "Fine-tunes a specialized open-source model (CodeLLaMA) to find outdated function comments and suggest updated comment wording.",
            "limitations": "Only works on in-code comments. Completely blind to external user documentation like README files, tutorials, and markdown guides.",
            "advantage_title": "Full-Repository Coverage:",
            "advantage_body": "Audits both in-code docstrings AND multi-file markdown/RST guides, plus features an interactive RAG Code Q&A bot."
        }
    ]

    for row_idx, p_data in enumerate(papers_data, start=1):
        row_bg = RGBColor(255, 255, 255) if row_idx % 2 == 1 else RGBColor(241, 245, 249)

        # Col 0: Venue
        c0 = table2.cell(row_idx, 0)
        c0.fill.solid()
        c0.fill.fore_color.rgb = row_bg
        tf0 = c0.text_frame
        tf0.word_wrap = True
        tf0.margin_top = tf0.margin_bottom = Inches(0.1)
        tf0.margin_left = tf0.margin_right = Inches(0.12)
        p0 = tf0.paragraphs[0]
        p0.text = p_data["venue"]
        p0.font.name = "Segoe UI"
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_ACCENT_BLUE

        # Col 1: Paper & Link (Clickable Hyperlink!)
        c1 = table2.cell(row_idx, 1)
        c1.fill.solid()
        c1.fill.fore_color.rgb = row_bg
        tf1 = c1.text_frame
        tf1.word_wrap = True
        tf1.margin_top = tf1.margin_bottom = Inches(0.1)
        tf1.margin_left = tf1.margin_right = Inches(0.12)
        p1 = tf1.paragraphs[0]
        p1.text = p_data["title"]
        p1.font.name = "Segoe UI"
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_MAIN

        p1_link = tf1.add_paragraph()
        p1_link.space_before = Pt(4)
        run_link = p1_link.add_run()
        run_link.text = p_data["link_text"]
        run_link.font.name = "Segoe UI"
        run_link.font.size = Pt(9.5)
        run_link.font.underline = True
        run_link.font.color.rgb = COLOR_LINK
        run_link.hyperlink.address = p_data["url"]

        # Col 2: Approach (Simple natural language)
        c2 = table2.cell(row_idx, 2)
        c2.fill.solid()
        c2.fill.fore_color.rgb = row_bg
        tf2 = c2.text_frame
        tf2.word_wrap = True
        tf2.margin_top = tf2.margin_bottom = Inches(0.1)
        tf2.margin_left = tf2.margin_right = Inches(0.12)
        p2 = tf2.paragraphs[0]
        p2.text = p_data["approach"]
        p2.font.name = "Segoe UI"
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_TEXT_MAIN

        # Col 3: Limitations (Simple natural language)
        c3 = table2.cell(row_idx, 3)
        c3.fill.solid()
        c3.fill.fore_color.rgb = row_bg
        tf3 = c3.text_frame
        tf3.word_wrap = True
        tf3.margin_top = tf3.margin_bottom = Inches(0.1)
        tf3.margin_left = tf3.margin_right = Inches(0.12)
        p3 = tf3.paragraphs[0]
        p3.text = p_data["limitations"]
        p3.font.name = "Segoe UI"
        p3.font.size = Pt(10)
        p3.font.color.rgb = COLOR_TEXT_MAIN

        # Col 4: DocSync Advantage (Toned down and clear)
        c4 = table2.cell(row_idx, 4)
        c4.fill.solid()
        c4.fill.fore_color.rgb = COLOR_GREEN_TINT
        tf4 = c4.text_frame
        tf4.word_wrap = True
        tf4.margin_top = tf4.margin_bottom = Inches(0.1)
        tf4.margin_left = tf4.margin_right = Inches(0.12)
        p4 = tf4.paragraphs[0]
        p4.text = ""
        r_title = p4.add_run()
        r_title.text = p_data["advantage_title"] + "\n"
        r_title.font.name = "Segoe UI"
        r_title.font.bold = True
        r_title.font.size = Pt(10.5)
        r_title.font.color.rgb = COLOR_GREEN_TEXT

        r_body = p4.add_run()
        r_body.text = p_data["advantage_body"]
        r_body.font.name = "Segoe UI"
        r_body.font.bold = False
        r_body.font.size = Pt(10)
        r_body.font.color.rgb = COLOR_TEXT_MAIN

    # Save cleanly with fallback
    downloads_dir = Path(os.environ.get("USERPROFILE", "C:/Users/HP")) / "Downloads"
    download_path_final = downloads_dir / "DocSync_Market_and_Research_Comparison_Final.pptx"
    local_path = Path("DocSync_Market_and_Research_Comparison.pptx")

    prs.save(str(download_path_final))
    prs.save(str(local_path))
    print(f"Two-slide presentation saved to: {download_path_final}")
    print(f"Backup saved to: {local_path}")

    # Also attempt saving to existing names if closed
    for fname in ["DocSync_Market_and_Research_Comparison_v2.pptx", "DocSync_Market_and_Research_Comparison.pptx"]:
        try:
            prs.save(str(downloads_dir / fname))
            print(f"Also updated: {fname}")
        except PermissionError:
            pass

if __name__ == "__main__":
    build_presentation()
