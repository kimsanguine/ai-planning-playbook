"""Render the authored planning handbook and package only learner-facing files."""
from pathlib import Path
import hashlib
import html
import json
import re
from urllib.parse import urlsplit
from html.parser import HTMLParser

import fitz
import markdown

from public_files import manifest_files

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "assets/fonts/PretendardVariable.ttf"
DIST = ROOT / "dist"
WEB = "https://habix.ai/playbook/ai-planning"
GITHUB = "https://github.com/kimsanguine/ai-planning-playbook/blob/main/"
TITLE = "AI를 쓰는 기획자의 판단법"
DESCRIPTION = "고객의 문제에서 시작해 선택과 포기, 실행 경계와 7일 뒤 재판단을 네 문서에 남깁니다."
LINK_MAP = {"README.md": "README.md", "handbook.md": "manuscript/README.md", "handbook.pdf": "https://habix.ai/assets/ai-planning/handbook.pdf", "handbook.html": WEB, **{name: "docs/" + name for name in ("hplan-guide.md", "decision-checklist.md", "instruction-practice.md")}}


def resolve_link(href):
    if urlsplit(href).scheme or href.startswith("#"):
        return href
    target = LINK_MAP.get(href, href)
    if target.startswith("../"):
        target = target[3:]
    return target if urlsplit(target).scheme else GITHUB + target


class LinkMapper(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        mapped = [(k, resolve_link(v) if k == "href" and v is not None else v) for k, v in attrs]
        self.parts.append("<" + tag + "".join(" " + k + ('=\"' + html.escape(v, quote=True) + '\"' if v is not None else "") for k, v in mapped) + ">")

    def handle_endtag(self, tag): self.parts.append("</" + tag + ">")
    def handle_data(self, data): self.parts.append(data)
    def handle_entityref(self, name): self.parts.append("&" + name + ";")
    def handle_charref(self, name): self.parts.append("&#" + name + ";")


CSS = """
@font-face {font-family: Planner; src: url('PretendardVariable.ttf');}
body {font-family: Planner, sans-serif; font-size:15px; line-height:1.5; color:#1a1a1a;}
h1 {font-size:27px; line-height:1.25; margin:0 0 18px; color:#1a1a1a; font-weight:bold;}
h2 {font-size:18px; line-height:1.35; margin:14px 0 7px; color:#e07a5f; font-weight:bold;}
h3 {font-size:16px; line-height:1.35; margin:14px 0 7px; font-weight:bold;}
p {margin:0 0 11px;} ul,ol {padding-left:22px; margin:6px 0 12px;} li {margin-bottom:5px;}
table {border-collapse:collapse; width:100%; margin:13px 0; font-size:13px;}
td,th {border:1px solid #e8e4dc; padding:9px; text-align:left; vertical-align:top;}
th {background:#f8e9e4; font-weight:bold;} tr:nth-child(even) td {background:#faf9f6;}
pre {font-family:Planner,sans-serif; font-size:13px; line-height:1.5; white-space:pre-wrap;
     background:#f7f2ed; border:1px solid #e8e4dc; padding:10px; margin:8px 0 11px;}
code {font-family:Planner,sans-serif; overflow-wrap:anywhere;}
a {color:#b95e47; text-decoration:underline;} blockquote {margin:12px 0; padding:0 0 0 15px; border-left:3px solid #e07a5f;}
"""


def md_to_html(text):
    mapper = LinkMapper()
    mapper.feed(markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"]))
    return "".join(mapper.parts)


def pdf_body(text, font, width, archive):
    output = md_to_html(text)
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    probe = fitz.open()
    probe_page = probe.new_page()
    probe_page.insert_htmlbox(fitz.Rect(0, 0, width, 160), "<h1>" + html.escape(title) + "</h1>", css=CSS, archive=archive, scale_low=1)
    title_lines = [line.strip() for line in probe_page.get_text().splitlines() if line.strip()]
    probe.close()
    if " " in title and len(title_lines) > 1 and len(title_lines[-1]) <= 3:
        words = title.split()
        choices = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
        left, right = min(choices, key=lambda pair: max(font.text_length(part) for part in pair))
        output = output.replace("<h1>" + html.escape(title) + "</h1>", "<h1>" + html.escape(left) + "<br>" + html.escape(right) + "</h1>", 1)
    return output


def cover_flow(page, area, spare):
    top = area.y1 - spare + 20
    if top + 145 > area.y1:
        raise ValueError("Cover needs room for the decision-to-record diagram")
    page.insert_text((area.x0, top), "내가 고른 결정 한 건이 네 문서로 이어집니다", fontname="Planner", fontsize=10, color=fitz.sRGB_to_pdf(0xE07A5F))
    labels = [
        ("고객의 근거", "customer.md", "최근 사건과 현재 대안", 0xF8E9E4),
        ("선택과 실행 경계", "prd.md / architecture.md", "범위, 품질과 사람 책임", 0xF7F2ED),
        ("다음 선택", "progress.md", "이유, 실제 결과와 재판단", 0xF6F4EE),
    ]
    width = (area.width - 20) / 3
    for i, (title, file, meaning, color) in enumerate(labels):
        x = area.x0 + i * (width + 10)
        page.draw_rect(fitz.Rect(x, top + 18, x + width, top + 133), color=fitz.sRGB_to_pdf(0xE8E4DC), fill=fitz.sRGB_to_pdf(color), width=0.6)
        page.insert_text((x + 10, top + 43), f"0{i + 1}  {title}", fontname="Planner", fontsize=10, color=fitz.sRGB_to_pdf(0x1A1A1A))
        page.insert_text((x + 10, top + 72), file, fontname="Planner", fontsize=8, color=fitz.sRGB_to_pdf(0xE07A5F))
        page.insert_textbox(fitz.Rect(x + 10, top + 87, x + width - 10, top + 122), meaning, fontname="Planner", fontsize=9, color=fitz.sRGB_to_pdf(0x6B6B6B))


def parse_pages(text):
    parts = re.split(r"<!--\s*page:\s*([a-z0-9-]+)\s*-->", text)
    if parts[0].strip():
        raise ValueError("Handbook must start with a page marker")
    pages = [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts), 2)]
    if len(pages) != 28 or len({slug for slug, _ in pages}) != 28:
        raise ValueError("Expected 28 distinct authored pages")
    for slug, text in pages:
        if len(re.findall(r"^# ", text, re.M)) != 1:
            raise ValueError(f"One H1 per page is required: {slug}")
    return pages


def render_pdf(pages):
    document = fitz.open()
    archive = fitz.Archive(str(FONT.parent))
    font = fitz.Font(fontfile=str(FONT))
    rendered = []
    for number, (slug, text) in enumerate(pages, 1):
        page = document.new_page(width=595.276, height=841.89)
        page.draw_rect(page.rect, color=None, fill=fitz.sRGB_to_pdf(0xFAF9F6))
        page.draw_rect(fitz.Rect(34, 72, 561, 794), color=fitz.sRGB_to_pdf(0xE8E4DC), fill=(1, 1, 1), width=0.6)
        page.draw_rect(fitz.Rect(44, 35, 96, 52), color=None, fill=fitz.sRGB_to_pdf(0xF8E9E4))
        page.insert_font(fontname="Planner", fontbuffer=font.buffer)
        page.insert_text((50, 47), f"{number:02d} / 28", fontname="Planner", fontsize=8, color=fitz.sRGB_to_pdf(0xE07A5F))
        page.insert_text((110, 47), "AI를 쓰는 기획자의 판단법", fontname="Planner", fontsize=9, color=fitz.sRGB_to_pdf(0x6B6B6B))
        area = fitz.Rect(48, 86, 547, 784)
        spare, scale = page.insert_htmlbox(area, pdf_body(text, font, area.width, archive), css=CSS, archive=archive, scale_low=1)
        if spare < 0 or scale < 0.999:
            raise ValueError(f"Authored page overflows; edit text instead of shrinking: {number} {slug}")
        if number == 1:
            cover_flow(page, area, spare)
        page.insert_text((45, 816), "김생근 | 고객의 문제에서 시작해 선택과 이유를 남깁니다", fontname="Planner", fontsize=8, color=fitz.sRGB_to_pdf(0x6B6B6B))
        page.insert_text((516, 816), f"{number:02d}", fontname="Planner", fontsize=9, color=fitz.sRGB_to_pdf(0xE07A5F))
        if len(page.get_text().strip()) < 100:
            raise ValueError(f"Missing extractable text: {slug}")
        rendered.append({"page": number, "slug": slug, "spare_points": round(spare, 1), "scale": scale, "text_chars": len(page.get_text())})
    document.set_metadata({"title": "AI를 쓰는 기획자의 판단법", "author": "김생근", "subject": "고객의 문제, 선택과 포기, 실행 경계와 7일 뒤 재판단"})
    document.set_toc([[1, re.search(r"^# (.+)$", text, re.M).group(1), n] for n, (_, text) in enumerate(pages, 1)])
    document.save(DIST / "handbook.pdf", garbage=4, deflate=True)
    document.close()
    return rendered



def write_manifest(pdf_report):
    manifest = {"title": TITLE, "pdf_pages": pdf_report, "files": {
        str(p.relative_to(ROOT)): {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in manifest_files(ROOT)}}
    (DIST / "build-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def build():
    DIST.mkdir(exist_ok=True)
    manuscript = (ROOT / "manuscript/README.md").read_text()
    pages = parse_pages(manuscript)
    pdf_report = render_pdf(pages)
    chapters = {"title": TITLE, "description": DESCRIPTION, "chapters": [
        {"number": n, "slug": slug, "title": re.search(r"^# (.+)$", text, re.M).group(1), "html": md_to_html(text)}
        for n, (slug, text) in enumerate(pages, 1)]}
    (DIST / "chapters.json").write_text(json.dumps(chapters, ensure_ascii=False, indent=2) + "\n")
    write_manifest(pdf_report)
    print(json.dumps({"pdf_pages": len(pages), "chapters": len(chapters["chapters"]), "minimum_spare_points": min(p["spare_points"] for p in pdf_report), "all_scale_one": all(p["scale"] == 1 for p in pdf_report)}, ensure_ascii=False))


if __name__ == "__main__":
    build()
