"""
Generador de PDF para el Documento de Diseño de Xolix 3.0.
Convierte los archivos Markdown en docs/ a un PDF profesional.
"""
import re
import os
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.platypus import NextPageTemplate
from reportlab.lib.units import inch

# ── Paths ──────────────────────────────────────────────────────────────────

BASE = Path(__file__).parent
SECTIONS = [
    BASE / "DISENO.md",
    BASE / "secciones" / "01_organizacion_diseno.md",
    BASE / "secciones" / "02_arquitectura.md",
    BASE / "secciones" / "03_diseno_estatico.md",
    BASE / "secciones" / "04_diseno_dinamico.md",
    BASE / "secciones" / "05_persistencia.md",
]
OUTPUT = BASE / "DISENO_Xolix_3.0.pdf"

# ── Colours ────────────────────────────────────────────────────────────────

NAVY   = colors.HexColor("#0D3B66")
BLUE   = colors.HexColor("#1A6FAF")
LBLUE  = colors.HexColor("#D6E8F7")
GREY   = colors.HexColor("#4A4A4A")
LGREY  = colors.HexColor("#F5F5F5")
BORDER = colors.HexColor("#CCCCCC")
CODE_BG= colors.HexColor("#F0F4F8")
CODE_FG= colors.HexColor("#1A1A2E")

# ── Styles ─────────────────────────────────────────────────────────────────

def build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles['Title'] = ParagraphStyle(
        'Title', parent=base['Title'],
        fontName='Helvetica-Bold', fontSize=28,
        textColor=NAVY, alignment=TA_CENTER,
        spaceAfter=12, spaceBefore=30,
    )
    styles['Subtitle'] = ParagraphStyle(
        'Subtitle', fontName='Helvetica', fontSize=14,
        textColor=BLUE, alignment=TA_CENTER,
        spaceAfter=6,
    )
    styles['Meta'] = ParagraphStyle(
        'Meta', fontName='Helvetica', fontSize=10,
        textColor=GREY, alignment=TA_CENTER,
        spaceAfter=4,
    )
    styles['H1'] = ParagraphStyle(
        'H1', fontName='Helvetica-Bold', fontSize=18,
        textColor=NAVY, spaceBefore=20, spaceAfter=10,
        borderPad=4,
    )
    styles['H2'] = ParagraphStyle(
        'H2', fontName='Helvetica-Bold', fontSize=14,
        textColor=BLUE, spaceBefore=16, spaceAfter=8,
    )
    styles['H3'] = ParagraphStyle(
        'H3', fontName='Helvetica-Bold', fontSize=12,
        textColor=GREY, spaceBefore=12, spaceAfter=6,
    )
    styles['H4'] = ParagraphStyle(
        'H4', fontName='Helvetica-BoldOblique', fontSize=11,
        textColor=GREY, spaceBefore=10, spaceAfter=4,
    )
    styles['Body'] = ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=10,
        textColor=colors.black, leading=14,
        spaceBefore=4, spaceAfter=4,
        alignment=TA_JUSTIFY,
    )
    styles['Bullet'] = ParagraphStyle(
        'Bullet', parent=styles['Body'],
        leftIndent=20, firstLineIndent=0,
        spaceBefore=2, spaceAfter=2,
        bulletIndent=10,
    )
    styles['Bullet2'] = ParagraphStyle(
        'Bullet2', parent=styles['Bullet'],
        leftIndent=36,
    )
    styles['Code'] = ParagraphStyle(
        'Code', fontName='Courier', fontSize=7.5,
        textColor=CODE_FG, backColor=CODE_BG,
        leading=11, leftIndent=8, rightIndent=8,
        spaceBefore=2, spaceAfter=2,
        borderColor=BORDER, borderWidth=0.5,
        borderPad=4,
    )
    styles['CodeLabel'] = ParagraphStyle(
        'CodeLabel', fontName='Courier-Bold', fontSize=8,
        textColor=BLUE, spaceBefore=6, spaceAfter=0,
    )
    styles['TableHeader'] = ParagraphStyle(
        'TableHeader', fontName='Helvetica-Bold', fontSize=9,
        textColor=colors.white, alignment=TA_CENTER,
    )
    styles['TableCell'] = ParagraphStyle(
        'TableCell', fontName='Helvetica', fontSize=8.5,
        textColor=colors.black, leading=12,
    )
    styles['TOCEntry1'] = ParagraphStyle(
        'TOCEntry1', fontName='Helvetica-Bold', fontSize=11,
        textColor=NAVY, spaceBefore=6,
    )
    styles['TOCEntry2'] = ParagraphStyle(
        'TOCEntry2', fontName='Helvetica', fontSize=10,
        leftIndent=16, textColor=BLUE,
    )
    styles['TOCEntry3'] = ParagraphStyle(
        'TOCEntry3', fontName='Helvetica', fontSize=9,
        leftIndent=32, textColor=GREY,
    )
    return styles

# ── Markdown helpers ────────────────────────────────────────────────────────

def escape_xml(text: str) -> str:
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))

def inline_format(text: str) -> str:
    # 1. Extract code spans before any processing
    code_spans: list[str] = []

    def protect_code(m: re.Match) -> str:
        code_spans.append(m.group(1))
        return f'\x00C{len(code_spans)-1}\x00'

    text = re.sub(r'`([^`]+)`', protect_code, text)

    # 2. Strip markdown links [label](url) → label (before escaping)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # 3. XML-escape the main text (code spans are still protected)
    text = escape_xml(text)

    # 4. Bold-italic (*** ... ***)
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold (** or __ but NOT inside identifiers like __init__)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Italic with * only (avoid _ in identifiers entirely)
    text = re.sub(r'\*([^\s*][^*]*[^\s*]|[^\s*])\*', r'<i>\1</i>', text)

    # 5. Restore code spans (escape their content separately)
    def restore_code(m: re.Match) -> str:
        idx = int(m.group(1))
        code_text = escape_xml(code_spans[idx])
        return f'<font name="Courier" size="9"><b>{code_text}</b></font>'

    text = re.sub(r'\x00C(\d+)\x00', restore_code, text)
    return text

def is_table_row(line: str) -> bool:
    return line.strip().startswith('|') and line.strip().endswith('|')

def is_separator_row(line: str) -> bool:
    return is_table_row(line) and re.match(r'^\s*\|[\s\|\-\:]+\|\s*$', line)

def parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows = []
    i = start
    while i < len(lines) and is_table_row(lines[i]):
        if not is_separator_row(lines[i]):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            rows.append(cells)
        i += 1
    return rows, i

# ── Safe Paragraph helper ───────────────────────────────────────────────────

def safe_para(text: str, style) -> Paragraph:
    try:
        return Paragraph(text, style)
    except Exception:
        clean = re.sub(r'<[^>]+>', '', text)
        try:
            return Paragraph(escape_xml(clean), style)
        except Exception:
            return Spacer(1, 2)


# ── Markdown → Flowables ────────────────────────────────────────────────────

def md_to_flowables(md_text: str, styles: dict, skip_frontmatter=True) -> list:
    lines = md_text.splitlines()
    flowables = []
    i = 0
    n = len(lines)

    # Skip YAML frontmatter
    if skip_frontmatter and lines and lines[0].strip() == '---':
        i = 1
        while i < n and lines[i].strip() != '---':
            i += 1
        i += 1  # skip closing ---

    in_code = False
    code_lines = []
    code_lang = ''

    while i < n:
        line = lines[i]

        # ── Code block start/end ──────────────────────────────────────────
        if line.strip().startswith('```'):
            if not in_code:
                in_code = True
                code_lang = line.strip()[3:].strip()
                code_lines = []
                i += 1
                continue
            else:
                # Render code block
                in_code = False
                if code_lang:
                    flowables.append(Paragraph(
                        f'<font color="#1A6FAF">[{code_lang.upper()}]</font>',
                        styles['CodeLabel']
                    ))
                # Chunk long code into multiple paragraphs to avoid overflow
                chunk_size = 60
                for j in range(0, len(code_lines), chunk_size):
                    chunk = code_lines[j:j+chunk_size]
                    code_text = '<br/>'.join(
                        escape_xml(cl).replace(' ', '&nbsp;') for cl in chunk
                    )
                    flowables.append(Paragraph(code_text, styles['Code']))
                code_lines = []
                i += 1
                continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # ── Horizontal rule ───────────────────────────────────────────────
        if re.match(r'^---+$', line.strip()) or re.match(r'^\*\*\*+$', line.strip()):
            flowables.append(HRFlowable(width="100%", thickness=0.5,
                                        color=BORDER, spaceAfter=6, spaceBefore=6))
            i += 1
            continue

        # ── Table ─────────────────────────────────────────────────────────
        if is_table_row(line):
            rows, i = parse_table(lines, i)
            if rows:
                flowables.append(build_table(rows, styles))
                flowables.append(Spacer(1, 6))
            continue

        # ── Headers ───────────────────────────────────────────────────────
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            text = inline_format(m.group(2).strip())
            style_key = f'H{level}' if level <= 4 else 'H4'
            flowables.append(safe_para(text, styles[style_key]))
            i += 1
            continue

        # ── Bullet lists ──────────────────────────────────────────────────
        m2 = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if m2:
            indent = len(m2.group(1))
            text = inline_format(m2.group(2))
            style = styles['Bullet2'] if indent >= 2 else styles['Bullet']
            flowables.append(safe_para(f'&#8226;&nbsp;{text}', style))
            i += 1
            continue

        # ── Numbered lists ────────────────────────────────────────────────
        m3 = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if m3:
            text = inline_format(m3.group(2))
            flowables.append(safe_para(f'&#8226;&nbsp;{text}', styles['Bullet']))
            i += 1
            continue

        # ── Empty line → spacer ───────────────────────────────────────────
        if not line.strip():
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # ── Normal paragraph ──────────────────────────────────────────────
        text = inline_format(line.strip())
        if text:
            flowables.append(safe_para(text, styles['Body']))
        i += 1

    return flowables


def build_table(rows: list[list[str]], styles: dict) -> Table:
    if not rows:
        return Spacer(1, 4)

    header = rows[0]
    data_rows = rows[1:]

    # Build table data with Paragraphs
    table_data = []
    # Header row
    table_data.append([
        Paragraph(escape_xml(h), styles['TableHeader']) for h in header
    ])
    # Data rows
    for row in data_rows:
        # Pad row to header length
        while len(row) < len(header):
            row.append('')
        table_data.append([
            safe_para(inline_format(cell), styles['TableCell'])
            for cell in row[:len(header)]
        ])

    # Calculate column widths
    page_width = A4[0] - 4*cm  # usable width
    ncols = len(header)
    col_width = page_width / ncols

    t = Table(table_data, colWidths=[col_width]*ncols, repeatRows=1)

    ts = TableStyle([
        # Header
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        # Data rows
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('TOPPADDING', (0,1), (-1,-1), 4),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        # Alternating rows
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LGREY]),
        # Grid
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ])
    t.setStyle(ts)
    return t


# ── Cover page ──────────────────────────────────────────────────────────────

def build_cover(styles: dict) -> list:
    story = []
    story.append(Spacer(1, 3*cm))

    # Logo block
    logo_data = [[Paragraph('XOLIX', ParagraphStyle(
        'Logo', fontName='Helvetica-Bold', fontSize=60,
        textColor=colors.white, alignment=TA_CENTER,
    ))]]
    logo_t = Table(logo_data, colWidths=[12*cm])
    logo_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(logo_t)
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph('3.0', ParagraphStyle(
        'Ver', fontName='Helvetica', fontSize=22,
        textColor=BLUE, alignment=TA_CENTER,
    )))
    story.append(Spacer(1, 1.5*cm))

    story.append(Paragraph(
        'DOCUMENTO DE DISEÑO DEL SISTEMA',
        ParagraphStyle('CTitle', fontName='Helvetica-Bold', fontSize=20,
                       textColor=NAVY, alignment=TA_CENTER, spaceAfter=8)
    ))
    story.append(Paragraph(
        'Plataforma de Gestión Integral de NNA',
        ParagraphStyle('CSub', fontName='Helvetica', fontSize=14,
                       textColor=BLUE, alignment=TA_CENTER, spaceAfter=4)
    ))
    story.append(HRFlowable(width="80%", thickness=2, color=NAVY,
                             spaceAfter=16, spaceBefore=8))

    meta = [
        ('Proyecto', 'Xolix — Fundación de Restitución de Derechos de NNA'),
        ('Version', '3.0'),
        ('Fecha', 'Junio 2026'),
        ('Institucion', 'Escuela Superior de Computo — IPN'),
        ('Materia', 'Analisis y Diseno de Sistemas'),
        ('Arquitecto', 'DDamianZR'),
    ]
    meta_data = [[Paragraph(f'<b>{k}</b>', styles['Body']),
                  Paragraph(v, styles['Body'])] for k, v in meta]
    meta_t = Table(meta_data, colWidths=[4*cm, 10*cm])
    meta_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LGREY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 2*cm))

    stats = [
        ['37 Tablas', '65+ Endpoints', '9 Diagramas UML'],
        ['16 Clases', '12 Consultas SQL', '8 Modulos'],
    ]
    stats_data = [[Paragraph(f'<b>{c}</b>', ParagraphStyle(
        'Stat', fontName='Helvetica-Bold', fontSize=12,
        textColor=NAVY, alignment=TA_CENTER,
    )) for c in row] for row in stats]
    stats_t = Table(stats_data, colWidths=[4.5*cm]*3)
    stats_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LBLUE),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('GRID', (0,0), (-1,-1), 1, BLUE),
    ]))
    story.append(stats_t)

    story.append(PageBreak())
    return story


# ── Page numbering ──────────────────────────────────────────────────────────

class NumberedCanvas:
    pass  # not needed with SimpleDocTemplate footer


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(GREY)
    page_num = canvas.getPageNumber()
    if page_num > 1:
        canvas.drawRightString(
            A4[0] - 1.5*cm, 1.2*cm,
            f'Xolix 3.0 — Documento de Diseno   |   Pagina {page_num}'
        )
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(1.5*cm, 1.5*cm, A4[0]-1.5*cm, 1.5*cm)
    canvas.restoreState()


# ── Section separator ───────────────────────────────────────────────────────

def section_title_page(number: int, title: str, subtitle: str, styles: dict) -> list:
    story = [PageBreak()]
    story.append(Spacer(1, 5*cm))

    num_data = [[Paragraph(str(number), ParagraphStyle(
        'Num', fontName='Helvetica-Bold', fontSize=72,
        textColor=colors.white, alignment=TA_CENTER,
    ))]]
    num_t = Table(num_data, colWidths=[3*cm], rowHeights=[3.5*cm])
    num_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(num_t)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(title.upper(), ParagraphStyle(
        'SecTitle', fontName='Helvetica-Bold', fontSize=22,
        textColor=NAVY, spaceBefore=10, spaceAfter=6,
    )))
    story.append(Paragraph(subtitle, ParagraphStyle(
        'SecSub', fontName='Helvetica', fontSize=13,
        textColor=BLUE,
    )))
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=10))
    story.append(PageBreak())
    return story


# ── Main ────────────────────────────────────────────────────────────────────

SECTION_META = [
    (None, None, None),  # index file — no separator
    (1, "Organización del Diseño",
     "Principios SOLID · DRY · KISS · Clean Architecture · Metodología · Notación"),
    (2, "Diseño Arquitectónico",
     "Objetivos · Diagrama de Componentes · Capas · Beneficios y Limitaciones"),
    (3, "Diseño Estático",
     "Subsistemas · Módulos · Paquetes · Clases BCE (Boundary · Control · Entity)"),
    (4, "Diseño Dinámico",
     "9 Diagramas de Secuencia UML · Casos de Uso CU-01 a CU-09"),
    (5, "Diseño de Persistencia",
     "Modelo Relacional · Diccionario de Datos · 12 Consultas SQL · Índices"),
]


def main():
    print("Generando DISENO_Xolix_3.0.pdf ...")
    styles = build_styles()

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2*cm, rightMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Xolix 3.0 — Documento de Diseño del Sistema",
        author="DDamianZR",
        subject="Análisis y Diseño de Sistemas — IPN ESCOM",
    )

    story = []

    # Cover
    story.extend(build_cover(styles))

    # Sections
    for idx, (path, meta) in enumerate(zip(SECTIONS, SECTION_META)):
        num, sec_title, sec_sub = meta

        if not path.exists():
            print(f"  [WARNING] No encontrado: {path}")
            continue

        text = path.read_text(encoding='utf-8')

        if idx == 0:
            # Index file — render as introduction, skip title duplication
            flowables = md_to_flowables(text, styles, skip_frontmatter=True)
            # Remove first few H1/H2 (already on cover)
            story.extend(flowables)
            story.append(PageBreak())
        else:
            # Section separator page
            story.extend(section_title_page(num, sec_title, sec_sub, styles))
            flowables = md_to_flowables(text, styles, skip_frontmatter=False)
            story.extend(flowables)

    print(f"  Construyendo PDF ({len(story)} elementos)...")
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    size_mb = OUTPUT.stat().st_size / 1_048_576
    print(f"  PDF generado: {OUTPUT}")
    print(f"  Tamaño: {size_mb:.1f} MB")


if __name__ == '__main__':
    main()
