"""Build the downloadable complete edition as a polished Chinese PDF."""
from pathlib import Path
from xml.sax.saxutils import escape
import json
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "职场拆局100问-完整正文.pdf"
FONT_REGULAR = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")

pdfmetrics.registerFont(TTFont("CN", str(FONT_REGULAR), subfontIndex=0))
pdfmetrics.registerFont(TTFont("CN-Bold", str(FONT_BOLD), subfontIndex=0))

INK = colors.HexColor("#202A44")
MUTED = colors.HexColor("#697386")
BLUE = colors.HexColor("#5266D8")
PALE_BLUE = colors.HexColor("#EDF3FF")
ACCENT = colors.HexColor("#E75B3C")
PALE_ORANGE = colors.HexColor("#FFF7E8")
GREEN = colors.HexColor("#EAF8F3")
LINE = colors.HexColor("#E1E6EF")
WHITE = colors.white

questions = json.loads((ROOT / "content" / "questions.json").read_text("utf-8"))
sources = {
    s["id"]: s
    for s in json.loads((ROOT / "content" / "sources.json").read_text("utf-8"))
}
reading_map = json.loads((ROOT / "content" / "reading-map.json").read_text("utf-8"))
questions_by_id = {q["id"]: q for q in questions}
for raw_id, extra in reading_map.items():
    ref = questions_by_id[int(raw_id)]["reference"]
    ref["sourceIds"] = list(dict.fromkeys(ref["sourceIds"] + extra["sourceIds"]))
    prior = ref.get("readingNote", "").strip()
    ref["readingNote"] = " ".join(x for x in (prior, extra["note"].strip()) if x)
labels = {
    "up": "向上沟通",
    "peer": "同事协作",
    "manage": "团队管理",
    "self": "工作自保",
    "talk": "表达与发展",
    "org": "组织判断",
}
volumes = {1: "第一册 · 基础应对", 2: "第二册 · 协作进阶", 3: "第三册 · 高阶判断与选择"}

base = getSampleStyleSheet()
styles = {
    "body": ParagraphStyle("BodyCN", parent=base["BodyText"], fontName="CN", fontSize=9.2, leading=16, textColor=INK, spaceAfter=7),
    "small": ParagraphStyle("SmallCN", parent=base["BodyText"], fontName="CN", fontSize=7.5, leading=12, textColor=MUTED),
    "meta": ParagraphStyle("MetaCN", parent=base["BodyText"], fontName="CN-Bold", fontSize=7.6, leading=12, textColor=BLUE),
    "h1": ParagraphStyle("H1CN", parent=base["Heading1"], fontName="CN-Bold", fontSize=27, leading=36, textColor=INK, spaceAfter=12),
    "h2": ParagraphStyle("H2CN", parent=base["Heading2"], fontName="CN-Bold", fontSize=16, leading=24, textColor=INK, spaceAfter=10),
    "h3": ParagraphStyle("H3CN", parent=base["Heading3"], fontName="CN-Bold", fontSize=10.5, leading=16, textColor=INK, spaceBefore=8, spaceAfter=4),
    "cover_title": ParagraphStyle("CoverTitle", parent=base["Title"], fontName="CN-Bold", fontSize=36, leading=47, textColor=WHITE, alignment=TA_LEFT),
    "cover_sub": ParagraphStyle("CoverSub", parent=base["BodyText"], fontName="CN", fontSize=11, leading=19, textColor=colors.HexColor("#EEF1FF")),
    "toc": ParagraphStyle("TocCN", parent=base["BodyText"], fontName="CN", fontSize=8, leading=12, textColor=INK),
    "quote": ParagraphStyle("QuoteCN", parent=base["BodyText"], fontName="CN", fontSize=9.4, leading=17, textColor=colors.HexColor("#6A4C23")),
    "card": ParagraphStyle("CardCN", parent=base["BodyText"], fontName="CN", fontSize=8.5, leading=14, textColor=INK),
}


def para(text, style="body"):
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), styles[style])


def panel(text, background, border, style="body", padding=9):
    table = Table([[para(text, style)]], colWidths=[A4[0] - 84])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 0.7, border),
        ("LINEBEFORE", (0, 0), (0, -1), 3, border),
        ("LEFTPADDING", (0, 0), (-1, -1), padding),
        ("RIGHTPADDING", (0, 0), (-1, -1), padding),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
    ]))
    return table


def page_frame(canvas, doc):
    page = canvas.getPageNumber()
    canvas.saveState()
    canvas.setTitle("职场拆局100问")
    canvas.setAuthor("职场拆局100问")
    if page > 1:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(21 * mm, A4[1] - 16 * mm, A4[0] - 21 * mm, A4[1] - 16 * mm)
        canvas.setFont("CN", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(21 * mm, A4[1] - 12.5 * mm, "职场拆局100问 · 少一点内耗，多一点选择")
        canvas.drawRightString(A4[0] - 21 * mm, 12 * mm, f"{page}")
    canvas.restoreState()


story = []

# Cover
cover = Table([
    [Paragraph("WORKPLACE PLAYBOOK", ParagraphStyle("K", fontName="CN-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#DCE2FF"), tracking=2))],
    [Spacer(1, 16)],
    [Paragraph("职场拆局<br/><font color='#FF8668'>100问</font>", styles["cover_title"])],
    [Spacer(1, 16)],
    [Paragraph("少一点内耗，多一点选择。", ParagraphStyle("S", fontName="CN-Bold", fontSize=15, leading=22, textColor=WHITE))],
    [Spacer(1, 72)],
    [Paragraph("一份遇到难题时，可以回来查的工作手册<br/>判断 · 行动 · 边界 · 参考输入", styles["cover_sub"])],
], colWidths=[A4[0] - 70 * mm])
cover.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#3E54C5")),
    ("LEFTPADDING", (0, 0), (-1, -1), 18 * mm),
    ("RIGHTPADDING", (0, 0), (-1, -1), 18 * mm),
    ("TOPPADDING", (0, 0), (-1, 0), 18 * mm),
    ("BOTTOMPADDING", (0, -1), (-1, -1), 18 * mm),
]))
story += [Spacer(1, 30 * mm), cover, Spacer(1, 12 * mm), para("不用一次读完，也不用全部照做。先找到与你处境相近的一题，做一个低成本动作，再根据反馈决定下一步。", "small"), PageBreak()]

# Clickable directory
story += [Paragraph("目录", styles["h1"]), para("点击题目可跳转。网页版支持搜索、筛选、收藏和复制话术。", "small"), Spacer(1, 5)]
for volume in (1, 2, 3):
    story.append(Paragraph(volumes[volume], styles["h2"]))
    rows = []
    for q in (x for x in questions if x["volume"] == volume):
        title = escape(f'{q["id"]:02d}  {q["title"]}')
        rows.append([Paragraph(f'<link href="#q{q["id"]}" color="#202A44">{title}</link>', styles["toc"])])
    toc = Table(rows, colWidths=[A4[0] - 84], repeatRows=0)
    toc.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
    ]))
    story += [toc, Spacer(1, 8)]

for q in questions:
    story.append(PageBreak())
    story.append(Paragraph(f'<a name="q{q["id"]}"/><font color="#E75B3C">{q["id"]:02d}</font>  {escape(q["title"])}', styles["h2"]))
    story.append(Paragraph(f'{escape(volumes[q["volume"]])}　·　{escape(labels[q["category"]])}　·　准备约{q["minutes"]}分钟', styles["meta"]))
    story.append(Spacer(1, 7))
    story.append(panel("先判断｜" + q["verdict"], PALE_BLUE, BLUE))
    story += [Spacer(1, 8), Paragraph("今天先做这一件事", styles["h3"]), para(q["firstAction"])]
    effort = Table([
        [Paragraph("要付出什么", styles["meta"]), Paragraph("可能换回什么", styles["meta"])],
        [para(q["cost"], "small"), para(q["gain"], "small")],
    ], colWidths=[(A4[0] - 84) / 2] * 2)
    effort.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F6F8FC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [effort, Spacer(1, 10), Paragraph("一句可以改成你自己的话", styles["h3"]), panel(q["say"], PALE_ORANGE, colors.HexColor("#F0B44C"), "quote")]
    story += [Spacer(1, 10), Paragraph("完整拆解", styles["h2"])]
    for text in q["body"]:
        match = re.match(r"^【([^】]+)】(.*)$", text)
        if match:
            story.append(Paragraph(escape(match.group(1)), styles["h3"]))
            story.append(para(match.group(2)))
        else:
            story.append(para(text))
    story += [Spacer(1, 5), Paragraph("沟通前，填一张行动卡", styles["h3"])]
    card = Table([[para(item, "card")] for item in q["worksheet"]], colWidths=[A4[0] - 84])
    card.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("LINEBELOW", (0, 0), (-1, -2), 0.35, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F9FC")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [card, Spacer(1, 9), panel("使用边界｜" + q["limit"], GREEN, colors.HexColor("#58B596"), "small", 8)]
    story += [Spacer(1, 7), Paragraph("参考与可信范围", styles["h3"]), para(q["reference"]["note"], "small")]
    for key in ("ruleNote", "readingNote"):
        if q["reference"].get(key):
            story.append(para(q["reference"][key], "small"))
    for source_id in q["reference"]["sourceIds"]:
        source = sources[source_id]
        story.append(Paragraph(f'• <link href="{escape(source["url"])}" color="#5266D8">{escape(source["title"])}</link> - {escape(source["status"])}', styles["small"]))
    story.append(para("一起看：" + " · ".join(f"第{n}问" for n in q["related"]), "small"))

OUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(
    str(OUT), pagesize=A4, rightMargin=21 * mm, leftMargin=21 * mm,
    topMargin=21 * mm, bottomMargin=18 * mm,
    title="职场拆局100问", author="职场拆局100问",
)
doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
print(OUT)
