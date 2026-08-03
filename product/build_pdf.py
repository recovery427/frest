#!/usr/bin/env python3
"""원고 마크다운을 판매용 PDF로 변환한다.

의존성: markdown, weasyprint, fonts-nanum
실행:  python3 product/build_pdf.py
"""
import pathlib
import re

import markdown
from weasyprint import HTML, CSS

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "manuscript.md"
OUT = ROOT / "AI광고영상이_어색한_진짜_이유.pdf"

TITLE = "AI 광고영상이 어색한 진짜 이유"
SUBTITLE = "프롬프트 원문과 실패 로그 전부"

CSS_TEXT = """
@page {
  size: A4;
  margin: 22mm 20mm 20mm 20mm;
  @bottom-center {
    content: counter(page);
    font-family: 'NanumGothic';
    font-size: 8pt;
    color: #9a958c;
  }
}
@page :first { margin: 0; @bottom-center { content: none; } }

* { box-sizing: border-box; }

body {
  font-family: 'NanumGothic', sans-serif;
  font-size: 10pt;
  line-height: 1.75;
  color: #23201c;
  word-break: keep-all;
}

/* ── 표지 ─────────────────────────────── */
.cover {
  page-break-after: always;
  height: 297mm;
  padding: 45mm 22mm 22mm 22mm;
  background: #1a1714;
  color: #f2ede4;
  display: flex;
  flex-direction: column;
}
.cover .kicker {
  font-size: 8.5pt;
  letter-spacing: 0.22em;
  color: #b8865a;
  margin-bottom: 14mm;
}
.cover h1 {
  font-family: 'NanumMyeongjo', serif;
  font-size: 33pt;
  line-height: 1.28;
  font-weight: 800;
  margin: 0 0 8mm 0;
  color: #f6f1e8;
  border: none;
  padding: 0;
}
.cover .sub {
  font-size: 12pt;
  color: #b8865a;
  margin-bottom: auto;
}
.cover .meta {
  font-size: 9pt;
  line-height: 2;
  color: #8d867c;
  border-top: 1px solid #3a342d;
  padding-top: 6mm;
}
.cover .meta b { color: #d8d0c4; font-weight: 400; }

/* ── 본문 ─────────────────────────────── */
h1 {
  font-family: 'NanumMyeongjo', serif;
  font-size: 20pt;
  line-height: 1.35;
  margin: 0 0 7mm 0;
  padding-bottom: 3mm;
  border-bottom: 2.5px solid #1a1714;
  page-break-before: always;
  page-break-after: avoid;
}
h2 {
  font-size: 13pt;
  margin: 9mm 0 3.5mm 0;
  padding-left: 3mm;
  border-left: 3px solid #b8865a;
  page-break-after: avoid;
}
h3 {
  font-size: 11pt;
  margin: 6mm 0 2.5mm 0;
  color: #4a4239;
  page-break-after: avoid;
}
p { margin: 0 0 3.5mm 0; }
strong { color: #8a5a2b; }

hr { border: none; border-top: 1px solid #ddd6ca; margin: 8mm 0; }

blockquote {
  margin: 4mm 0;
  padding: 3.5mm 5mm;
  background: #f7f3ec;
  border-left: 3px solid #b8865a;
  font-size: 9.5pt;
}
blockquote p:last-child { margin-bottom: 0; }

ul, ol { margin: 0 0 4mm 0; padding-left: 6mm; }
li { margin-bottom: 1.5mm; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: 4mm 0 6mm 0;
  font-size: 8.5pt;
  page-break-inside: avoid;
}
th {
  background: #2c2722;
  color: #f2ede4;
  text-align: left;
  padding: 2mm 2.5mm;
  font-weight: 400;
}
td {
  padding: 2mm 2.5mm;
  border-bottom: 1px solid #e2dbcf;
  vertical-align: top;
}
tbody tr:nth-child(even) { background: #faf7f2; }

code {
  font-family: 'NanumGothicCoding', monospace;
  font-size: 8.5pt;
  background: #f2ede4;
  padding: 0.4mm 1.2mm;
  color: #7a4a1e;
}
pre {
  background: #201c18;
  color: #ddd4c6;
  padding: 4mm;
  margin: 3mm 0 5mm 0;
  font-size: 7.6pt;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  page-break-inside: avoid;
}
pre code {
  background: none;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

em { color: #6b635a; font-style: normal; font-size: 9pt; }
"""


def build():
    raw = SRC.read_text(encoding="utf-8")

    # 원고 맨 앞의 제목·부제 블록은 표지로 대체하므로 첫 구분선까지만 걷어낸다.
    # (구분선을 두 번 자르면 '들어가며' 장이 통째로 사라진다.)
    body_md = raw.split("---", 1)[-1].lstrip()

    html_body = markdown.markdown(
        body_md,
        extensions=["tables", "fenced_code", "sane_lists"],
    )

    # 체크박스 목록을 PDF에서 읽히는 문자로 바꾼다.
    html_body = re.sub(r"\[ \]", "☐", html_body)

    cover = f"""
    <div class="cover">
      <div class="kicker">AI VIDEO PRODUCTION · FIELD MANUAL</div>
      <h1>{TITLE}</h1>
      <div class="sub">{SUBTITLE}</div>
      <div class="meta">
        프롬프트 원문 <b>전체 공개</b><br>
        실패 사례 <b>12가지</b>와 각각의 수정 문장<br>
        실측 크레딧 단가 <b>이미지 7 / 영상 45</b>
      </div>
    </div>
    """

    html = f"<html><head><meta charset='utf-8'></head><body>{cover}{html_body}</body></html>"
    HTML(string=html).write_pdf(OUT, stylesheets=[CSS(string=CSS_TEXT)])
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
