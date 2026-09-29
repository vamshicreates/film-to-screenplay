#!/usr/bin/env python3
"""
compile_screenplay_pdf.py
Universal Hollywood Screenplay PDF & Legal Disclaimer Compiler.
Works for ANY movie title, language/dialect, director, and production house.

Generates:
1. A strict US Letter, 12pt Courier Hollywood Screenplay PDF (<Movie>_Screenplay.pdf)
   with a dynamically tailored 4-Pillar SRT-Reconstruction & Fair-Dealing Legal
   Disclaimer permanently embedded on Page 1 (Title Page).
2. A merged master Fountain screenplay file (<Movie>_Screenplay.fountain).
3. A 1080x1080 Static Social / Giveaway Disclaimer Card (<Movie>_Disclaimer_Card.png)
   tailored to the specific film, director, and production house.
4. Optional rendered PNG page previews for visual verification.
"""

import argparse
import json
import os
import re
import sys
import textwrap
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)

PAGE_WIDTH, PAGE_HEIGHT = letter  # 8.5 x 11 inches
LEFT_MARGIN = 1.5 * inch
RIGHT_MARGIN = 1.0 * inch
TOP_MARGIN = 1.0 * inch
BOTTOM_MARGIN = 1.0 * inch
PRINT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN  # 6.0 inches


def draw_title_page(canvas, doc):
    canvas.saveState()
    canvas.restoreState()


def draw_script_page(canvas, doc):
    canvas.saveState()
    script_page_num = canvas.getPageNumber() - 1
    if script_page_num >= 2:
        canvas.setFont("Courier", 12)
        canvas.drawRightString(
            PAGE_WIDTH - RIGHT_MARGIN,
            PAGE_HEIGHT - 0.5 * inch,
            f"{script_page_num}.",
        )
    canvas.restoreState()


def get_screenplay_styles():
    styles = {}

    styles["TitleMain"] = ParagraphStyle(
        "TitleMain",
        fontName="Courier-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    styles["TitleSub"] = ParagraphStyle(
        "TitleSub",
        fontName="Courier",
        fontSize=12,
        leading=15,
        alignment=TA_CENTER,
        spaceAfter=24,
    )

    styles["TitleCredit"] = ParagraphStyle(
        "TitleCredit",
        fontName="Courier",
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    styles["TitleCreditBold"] = ParagraphStyle(
        "TitleCreditBold",
        fontName="Courier-Bold",
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=16,
    )

    styles["TitleFooter"] = ParagraphStyle(
        "TitleFooter",
        fontName="Courier",
        fontSize=9.5,
        leading=12.5,
        alignment=TA_LEFT,
        spaceAfter=2,
    )

    styles["FadeIn"] = ParagraphStyle(
        "FadeIn",
        fontName="Courier-Bold",
        fontSize=12,
        leading=12,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=12,
        keepWithNext=True,
    )

    styles["SceneHeading"] = ParagraphStyle(
        "SceneHeading",
        fontName="Courier-Bold",
        fontSize=12,
        leading=13,
        alignment=TA_LEFT,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=16,
        spaceAfter=6,
        keepWithNext=True,
    )

    styles["Action"] = ParagraphStyle(
        "Action",
        fontName="Courier",
        fontSize=12,
        leading=13,
        alignment=TA_LEFT,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=4,
        spaceAfter=6,
    )

    styles["Character"] = ParagraphStyle(
        "Character",
        fontName="Courier-Bold",
        fontSize=12,
        leading=13,
        alignment=TA_LEFT,
        leftIndent=2.2 * inch,
        rightIndent=0.2 * inch,
        spaceBefore=10,
        spaceAfter=0,
        keepWithNext=True,
    )

    styles["Parenthetical"] = ParagraphStyle(
        "Parenthetical",
        fontName="Courier-Oblique",
        fontSize=11.5,
        leading=12.5,
        alignment=TA_LEFT,
        leftIndent=1.6 * inch,
        rightIndent=1.6 * inch,
        spaceBefore=0,
        spaceAfter=0,
        keepWithNext=True,
    )

    styles["Dialogue"] = ParagraphStyle(
        "Dialogue",
        fontName="Courier",
        fontSize=12,
        leading=13,
        alignment=TA_LEFT,
        leftIndent=1.0 * inch,
        rightIndent=1.5 * inch,
        spaceBefore=0,
        spaceAfter=4,
    )

    styles["Transition"] = ParagraphStyle(
        "Transition",
        fontName="Courier-Bold",
        fontSize=12,
        leading=13,
        alignment=TA_RIGHT,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=10,
        spaceAfter=10,
    )

    styles["Centered"] = ParagraphStyle(
        "Centered",
        fontName="Courier-Bold",
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        spaceBefore=14,
        spaceAfter=14,
    )

    return styles


def clean_line(text: str) -> str:
    text = text.strip()
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2014": "--",
        "\u2013": "-",
        "\u2026": "...",
        "♪": "[SONG]",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = text.encode("latin-1", errors="ignore").decode("latin-1")
    text = escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def is_scene_heading(line: str) -> bool:
    u = line.strip().upper()
    if u.startswith(("INT.", "EXT.", "INT/EXT", "INT./EXT.", "I/E.", "PROLOGUE:", "ACT ")):
        return True
    if line.strip().startswith(".") and len(line.strip()) > 2 and line.strip()[1].isalpha():
        return True
    return False


def is_transition(line: str) -> bool:
    s = line.strip()
    if s.startswith(">") and not s.endswith("<"):
        return True
    u = s.upper()
    if u in (
        "FADE IN:",
        "FADE OUT.",
        "FADE OUT:",
        "FADE TO BLACK.",
        "FADE TO BLACK:",
        "CUT TO BLACK.",
        "CUT TO BLACK:",
        "SMASH TO BLACK.",
        "SMASH TO BLACK:",
        "SMASH CUT TO:",
        "MATCH CUT TO:",
        "JUMP CUT TO:",
        "DISSOLVE TO:",
        "CUT TO:",
        "BACK TO:",
        "INTERCUT WITH:",
        "END INTERCUT.",
        "END INTERCUT:",
        "MONTAGE -",
        "END MONTAGE",
    ):
        return True
    if u.endswith("TO:") and len(u) < 35 and u == s:
        return True
    return False


def is_centered(line: str) -> bool:
    s = line.strip()
    if s.startswith(">") and s.endswith("<"):
        return True
    u = s.upper()
    if u in ("INTERMISSION", "INTERVAL", "THE END") or u.startswith("THE END OF"):
        return True
    return False


def is_character_cue(line: str, prev_blank: bool, next_line: str) -> bool:
    if not prev_blank or not next_line:
        return False
    s = line.strip()
    if not s:
        return False
    if s.startswith("@"):
        return True
    if is_scene_heading(s) or is_transition(s) or is_centered(s):
        return False
    if s.startswith("(") and s.endswith(")"):
        return False
    if s.startswith("#") or s.startswith("---") or s.startswith("==="):
        return False
    base = re.sub(r"\([^)]*\)", "", s).strip()
    if not base or len(base) > 45:
        return False
    if any(c.isalpha() for c in base) and base == base.upper():
        if base.endswith(".") and not base.endswith(("JR.", "SR.", "DR.", "ST.", "MR.", "MRS.")):
            return False
        return True
    return False


def parse_fountain_to_story(fountain_text: str, styles, char_map=None):
    if char_map is None:
        char_map = {}
    story = []
    raw_lines = fountain_text.splitlines()
    n = len(raw_lines)
    i = 0
    prev_blank = True

    while i < n:
        line = raw_lines[i].strip()

        if not line or line.startswith("===") or line.startswith("---"):
            prev_blank = True
            i += 1
            continue

        if line.startswith("#"):
            hdr = line.lstrip("#").strip().upper()
            if hdr:
                story.append(Paragraph(clean_line(hdr), styles["Centered"]))
            prev_blank = True
            i += 1
            continue

        if is_centered(line):
            c_txt = line.strip(">< ").upper()
            story.append(Paragraph(clean_line(c_txt), styles["Centered"]))
            prev_blank = True
            i += 1
            continue

        if line.upper() == "FADE IN:":
            story.append(Paragraph("FADE IN:", styles["FadeIn"]))
            prev_blank = True
            i += 1
            continue

        if is_transition(line):
            t_txt = line.lstrip("> ").strip().upper()
            story.append(Paragraph(clean_line(t_txt), styles["Transition"]))
            prev_blank = True
            i += 1
            continue

        if is_scene_heading(line):
            s_txt = line.lstrip(".").strip().upper()
            story.append(Paragraph(clean_line(s_txt), styles["SceneHeading"]))
            prev_blank = True
            i += 1
            continue

        next_line = raw_lines[i + 1].strip() if (i + 1 < n) else ""
        if is_character_cue(line, prev_blank, next_line):
            char_name = line.lstrip("@").strip().upper()
            char_name = char_map.get(char_name, char_name)
            story.append(Paragraph(clean_line(char_name), styles["Character"]))
            i += 1
            while i < n and raw_lines[i].strip():
                d_line = raw_lines[i].strip()
                if is_scene_heading(d_line) or is_transition(d_line):
                    break
                if d_line.startswith("(") and d_line.endswith(")"):
                    story.append(Paragraph(clean_line(d_line), styles["Parenthetical"]))
                else:
                    d_parts = [clean_line(d_line)]
                    while (
                        i + 1 < n
                        and raw_lines[i + 1].strip()
                        and not (
                            raw_lines[i + 1].strip().startswith("(")
                            and raw_lines[i + 1].strip().endswith(")")
                        )
                        and not is_scene_heading(raw_lines[i + 1].strip())
                        and not is_transition(raw_lines[i + 1].strip())
                    ):
                        i += 1
                        d_parts.append(clean_line(raw_lines[i].strip()))
                    story.append(Paragraph(" ".join(d_parts), styles["Dialogue"]))
                i += 1
            prev_blank = False
            continue

        act_parts = [clean_line(line)]
        while i + 1 < n:
            peek = raw_lines[i + 1].strip()
            if (
                not peek
                or peek.startswith("#")
                or peek.startswith("---")
                or is_scene_heading(peek)
                or is_transition(peek)
                or is_centered(peek)
            ):
                break
            act_parts.append(clean_line(peek))
            i += 1

        story.append(Paragraph(" ".join(act_parts), styles["Action"]))
        prev_blank = False
        i += 1

    return story


def format_creator_clause(director: str, writers: str, production_house: str) -> str:
    """Builds a natural, movie-specific attribution clause for the legal disclaimer."""
    parts = []
    if director:
        parts.append(f"the director ({director})")
    else:
        parts.append("the director")

    if writers and writers.lower() != director.lower():
        parts.append(f"writers ({writers})")
    else:
        parts.append("writers")

    if production_house and production_house.lower() != "the production house":
        parts.append(f"producers ({production_house})")
    else:
        parts.append("the producers or production house")

    if len(parts) == 3:
        return f"{parts[0]}, {parts[1]}, or {parts[2]}"
    return ", ".join(parts)


def build_title_page_story(
    styles,
    title: str,
    subtitle: str,
    director: str,
    writers: str,
    music: str,
    production_house: str,
    dialect_note: str,
):
    story = []
    story.append(Spacer(1, 1.45 * inch))
    story.append(Paragraph(f"<u>{clean_line(title.upper())}</u>", styles["TitleMain"]))
    if subtitle:
        story.append(Paragraph(clean_line(subtitle), styles["TitleSub"]))
    else:
        story.append(Spacer(1, 0.2 * inch))

    if director:
        story.append(Paragraph("Written &amp; Directed by", styles["TitleCredit"]))
        story.append(Paragraph(clean_line(director.upper()), styles["TitleCreditBold"]))
    if writers:
        story.append(Paragraph("Dialogues / Screenplay Credits", styles["TitleCredit"]))
        story.append(Paragraph(clean_line(writers.upper()), styles["TitleCreditBold"]))
    if music:
        story.append(Paragraph("Original Music by", styles["TitleCredit"]))
        story.append(Paragraph(clean_line(music.upper()), styles["TitleCreditBold"]))

    story.append(Spacer(1, 0.9 * inch))
    if dialect_note:
        story.append(
            Paragraph(
                f"<b>LANGUAGE &amp; FORMAT NOTE:</b> {clean_line(dialect_note)}",
                styles["TitleFooter"],
            )
        )
        story.append(Spacer(1, 0.08 * inch))

    creator_clause = format_creator_clause(director, writers, production_house)

    story.append(
        Paragraph(
            f"<b>EDUCATIONAL &amp; ARCHIVAL DISCLAIMER -- {clean_line(title.upper())} (UNOFFICIAL SRT RECONSTRUCTION):</b>",
            styles["TitleFooter"],
        )
    )
    story.append(
        Paragraph(
            f'This screenplay for "{clean_line(title)}" is an independent, unofficial study reconstruction',
            styles["TitleFooter"],
        )
    )
    story.append(
        Paragraph(
            "transcribed and formatted from the released film's subtitle (SRT) track (~90-95% faithful to the theatrical cut; minor errors may exist).",
            styles["TitleFooter"],
        )
    )
    story.append(
        Paragraph(
            f"It is NOT an official production script provided by {clean_line(creator_clause)}.",
            styles["TitleFooter"],
        )
    )
    story.append(
        Paragraph(
            "Created and shared strictly free of charge for non-commercial film study to help filmmakers read and analyze the script.",
            styles["TitleFooter"],
        )
    )
    story.append(
        Paragraph(
            "All underlying rights, characters, and IP belong solely to their respective copyright owners.",
            styles["TitleFooter"],
        )
    )
    story.append(NextPageTemplate("ScriptPage"))
    story.append(PageBreak())
    return story


def generate_disclaimer_card_png(
    output_png: str,
    title: str,
    director: str,
    writers: str,
    production_house: str,
):
    """Generates a clean 1080x1080 dark-mode editorial static disclaimer card tailored to the movie."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1080, 1080
    img = Image.new("RGB", (width, height), color=(14, 14, 16))
    draw = ImageDraw.Draw(img)

    draw.rectangle([48, 48, width - 48, height - 48], outline=(65, 65, 72), width=2)
    draw.rectangle([60, 60, width - 60, height - 60], outline=(35, 35, 40), width=1)

    def load_font(size, bold=False):
        candidates = [
            "/System/Library/Fonts/Courier.dfont",
            "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Courier New.ttf",
            "/Library/Fonts/Courier New.ttf",
            "C:\\Windows\\Fonts\\courbd.ttf" if bold else "C:\\Windows\\Fonts\\cour.ttf",
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    return ImageFont.truetype(c, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    font_tag = load_font(22, bold=True)
    font_title = load_font(36, bold=True)
    font_body = load_font(25, bold=False)
    font_footer = load_font(20, bold=False)

    draw.text(
        (100, 125),
        "FOR FILMMAKERS & SCREENWRITING STUDY ONLY",
        fill=(212, 175, 55),
        font=font_tag,
    )

    # Wrap long movie titles cleanly if needed
    title_lines = textwrap.wrap(title.upper(), width=34)[:2]
    y_title = 180
    for t_ln in title_lines:
        draw.text((100, y_title), t_ln, fill=(245, 245, 247), font=font_title)
        y_title += 44

    divider_y = y_title + 15
    draw.line([(100, divider_y), (980, divider_y)], fill=(70, 70, 78), width=2)

    creator_clause = format_creator_clause(director, writers, production_house)
    paragraph = (
        f'This screenplay for "{title}" is an independent, unofficial '
        f"reconstruction transcribed and formatted from the released film's "
        f"SRT subtitle track (~90-95% faithful to the theatrical cut, with "
        f"minor variations possible).\n\n"
        f"It was NOT provided by {creator_clause}, and is shared strictly "
        f"free of charge as a non-commercial educational resource to help "
        f"aspiring writers and filmmakers read and study the script.\n\n"
        f"All underlying characters, story, and intellectual property belong "
        f"solely to the original creators and copyright holders."
    )

    y_cursor = divider_y + 45
    for block in paragraph.split("\n\n"):
        wrapped = textwrap.wrap(block, width=52)
        for ln in wrapped:
            draw.text((100, y_cursor), ln, fill=(220, 220, 225), font=font_body)
            y_cursor += 38
        y_cursor += 26

    draw.line([(100, 910), (980, 910)], fill=(50, 50, 58), width=1)
    draw.text(
        (100, 940),
        "UNOFFICIAL SRT STUDY TRANSCRIPT  •  NON-COMMERCIAL FAIR DEALING",
        fill=(140, 140, 150),
        font=font_footer,
    )
    img.save(output_png)


def main():
    parser = argparse.ArgumentParser(
        description="Compile Fountain screenplay parts into a Hollywood Screenplay PDF + Movie-Specific Legal Disclaimer."
    )
    parser.add_argument("--title", required=True, help="Film title (e.g. 'ANIMAL', 'RRR', 'OPPENHEIMER')")
    parser.add_argument(
        "--subtitle",
        default="Complete Feature Screenplay (Unofficial SRT Study Reconstruction)",
        help="Subtitle on Title Page",
    )
    parser.add_argument("--director", default="", help="Director / Writer credit")
    parser.add_argument("--writers", default="", help="Co-writers / Dialogue credit")
    parser.add_argument("--music", default="", help="Music composer credit")
    parser.add_argument(
        "--production-house",
        default="the production house",
        help="Production company name for the legal disclaimer",
    )
    parser.add_argument(
        "--dialect-note",
        default="",
        help="Optional note on language/transliteration dialect",
    )
    parser.add_argument(
        "--char-map-json",
        default="",
        help="Optional JSON string or file path mapping character name variants to canonical names",
    )
    parser.add_argument("--output-pdf", required=True, help="Output PDF path")
    parser.add_argument("--output-fountain", default="", help="Optional output merged .fountain path")
    parser.add_argument(
        "--disclaimer-image",
        default="",
        help="Optional output path for 1080x1080 static disclaimer PNG",
    )
    parser.add_argument(
        "--preview-dir",
        default="",
        help="Optional directory to render PNG previews of Page 1, 2, Middle, and Last Page",
    )
    parser.add_argument("parts", nargs="+", help="Input .fountain files in chronological order")
    args = parser.parse_args()

    char_map = {}
    if args.char_map_json:
        if os.path.exists(args.char_map_json):
            with open(args.char_map_json, "r", encoding="utf-8") as jf:
                char_map = json.load(jf)
        else:
            char_map = json.loads(args.char_map_json)

    combined_text = []
    for p in args.parts:
        with open(p, "r", encoding="utf-8") as f:
            combined_text.append(f.read().strip())
    full_fountain = "\n\n".join(combined_text)

    if args.output_fountain:
        os.makedirs(os.path.dirname(os.path.abspath(args.output_fountain)), exist_ok=True)
        with open(args.output_fountain, "w", encoding="utf-8") as f:
            f.write(full_fountain + "\n")

    os.makedirs(os.path.dirname(os.path.abspath(args.output_pdf)), exist_ok=True)
    styles = get_screenplay_styles()
    doc = BaseDocTemplate(
        args.output_pdf,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title=f"{args.title} - Unofficial SRT Study Screenplay",
        author=args.director or "Unofficial SRT Study Reconstruction",
    )

    frame = Frame(
        LEFT_MARGIN,
        BOTTOM_MARGIN,
        PRINT_WIDTH,
        PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN,
        id="normal",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="TitlePage", frames=[frame], onPage=draw_title_page),
            PageTemplate(id="ScriptPage", frames=[frame], onPage=draw_script_page),
        ]
    )

    story = []
    story.extend(
        build_title_page_story(
            styles=styles,
            title=args.title,
            subtitle=args.subtitle,
            director=args.director,
            writers=args.writers,
            music=args.music,
            production_house=args.production_house,
            dialect_note=args.dialect_note,
        )
    )
    story.extend(parse_fountain_to_story(full_fountain, styles, char_map=char_map))
    doc.build(story)
    print(f"Built PDF: {args.output_pdf}")

    if args.disclaimer_image:
        os.makedirs(os.path.dirname(os.path.abspath(args.disclaimer_image)), exist_ok=True)
        generate_disclaimer_card_png(
            args.disclaimer_image,
            args.title,
            args.director,
            args.writers,
            args.production_house,
        )
        print(f"Built Disclaimer Card PNG: {args.disclaimer_image}")

    if args.preview_dir:
        try:
            import pypdfium2 as pdfium

            os.makedirs(args.preview_dir, exist_ok=True)
            pdf = pdfium.PdfDocument(args.output_pdf)
            total_pages = len(pdf)
            print(f"Total PDF pages: {total_pages}")
            for pno in sorted({0, 1, total_pages // 2, total_pages - 1}):
                if 0 <= pno < total_pages:
                    img = pdf[pno].render(scale=2).to_pil()
                    out_p = os.path.join(args.preview_dir, f"page_{pno + 1}.png")
                    img.save(out_p)
                    print(f"Saved preview: {out_p}")
        except Exception as e:
            print(f"Preview rendering skipped: {e}")


if __name__ == "__main__":
    main()
