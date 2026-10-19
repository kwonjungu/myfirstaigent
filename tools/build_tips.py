# -*- coding: utf-8 -*-
"""하루 한 팁 페이지 만들기 — tips.py(단일 출처)를 읽어
   - tips.html (전체 목록 · 오늘의 팁), t01~t17.html (팁 하나당 한 페이지)
   - assets/tips/keys/NN.svg (단축키 그림 · 카드뉴스·메신저 공유용)
   - 모든 페이지 오른쪽 위(utility-bar)에 '하루 팁' 링크
   머리·꼬리(utility-bar · 탭 · 주소 QR · 꼬리말)는 지금 index.html에서 잘라 쓴다.
   캡처는 assets/tips/shot/ 에 tips.py의 파일 이름으로 넣고 다시 돌리면 '캡처 자리'가 사진으로 바뀐다.
   사용: python tools/build_tips.py"""
import os, re, sys, glob, html
from urllib.parse import quote
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tips import TIPS, CATS, START  # noqa: E402

E = html.escape
SHOT = "assets/tips/shot"
KEYS = "assets/tips/keys"
os.makedirs(os.path.join(ROOT, SHOT), exist_ok=True)
os.makedirs(os.path.join(ROOT, KEYS), exist_ok=True)
N = len(TIPS)

TIP_LINK = '<a class="deck-tab deck-tab-tip" href="tips.html" title="하루 한 팁 · 교실 단축키">하루 팁</a>'


def add_tip_link(s):
    """오른쪽 위 줄 맨 끝(주소 · QR 다음)에 '하루 팁' — 이미 있으면 그대로"""
    if "deck-tab-tip" in s or 'class="utility-bar"' not in s:
        return s
    a = '<button class="deck-tab addr-open" type="button" title="사이트 주소와 QR 크게 보기">주소 · QR</button>'
    assert s.count(a) == 1, "utility-bar의 주소 · QR 버튼을 못 찾음"
    return s.replace(a, a + "\n      " + TIP_LINK)


# ------------------------------------------------------------------ 기존 페이지에 링크 넣기
for f in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
    if re.fullmatch(r"t\d\d\.html|tips\.html", os.path.basename(f)):
        continue
    s = open(f, encoding="utf-8").read()
    t = add_tip_link(s)
    if t != s:
        open(f, "w", encoding="utf-8", newline="\n").write(t)
        print("하루 팁 링크:", os.path.basename(f))

# ------------------------------------------------------------------ 머리·꼬리는 index.html에서
idx = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
HEAD = idx[:idx.index("<body>") + len("<body>")]
TOP = idx[idx.index("<body>") + len("<body>"):idx.index("<main")]
TOP = TOP.replace(' class="tab on" href="index.html" aria-current=page>', ' class="tab" href="index.html">')
TOP = TOP.replace('class="deck-tab deck-tab-tip"', 'class="deck-tab deck-tab-tip on" aria-current=page')
FOOT = idx[idx.index("</main>") + len("</main>"):]


def head(title, desc):
    h = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", HEAD, count=1)
    return re.sub(r'<meta name="description" content="[^"]*" />', f'<meta name="description" content="{E(desc)}" />', h, count=1)


# ------------------------------------------------------------------ 단축키 SVG
KH, SH, R = 52, 5, 10           # 키 높이 · 아래 그림자 · 모서리
INK, FACE, EDGE = "#111111", "#ffffff", "#cacacb"
FONT = "Pretendard, 'Malgun Gothic', sans-serif"


def tw(t, size=20):
    """글자 폭 어림 — 영문·숫자 0.6em, 한글·기호 1em"""
    return sum(size * (0.6 if ord(c) < 128 else 1.0) for c in t)


def key_svg(keys, scale=1.0, standalone=False):
    parts, x, hold = [], 0, False
    prev_key = False
    for k in keys:
        if k in ("+", "›", "/"):
            w = 30 if k != "/" else 24
            parts.append(f'<text x="{x + w / 2}" y="{KH / 2 + 8}" text-anchor="middle" font-size="24" font-weight="700" fill="#707072">{E(k)}</text>')
            x += w
            prev_key = False
            continue
        if prev_key:
            x += 6  # 이어 누르는 키(0 1 8 3)는 조금 띄우기만
        h = k.endswith("*")
        name = k.rstrip("*")
        if name == "Win":
            w = 60
        elif name == "휠":
            w = 52
        else:
            w = max(KH, tw(name) + 28)
        g = [f'<rect x="{x}" y="{SH}" width="{w}" height="{KH}" rx="{R}" fill="{EDGE}"/>',
             f'<rect x="{x}" y="0" width="{w}" height="{KH}" rx="{R}" fill="{FACE}" stroke="{INK}" stroke-width="2"/>']
        if name == "Win":  # 창 모양 네 칸
            cx, cy, s, gap = x + w / 2, KH / 2, 9, 2
            for dx in (-s - gap / 2, gap / 2):
                for dy in (-s - gap / 2, gap / 2):
                    g.append(f'<rect x="{cx + dx}" y="{cy + dy}" width="{s}" height="{s}" fill="{INK}"/>')
        elif name == "휠":  # 마우스 + 휠
            mx, mw = x + w / 2 - 11, 22
            g.append(f'<rect x="{mx}" y="9" width="{mw}" height="34" rx="11" fill="none" stroke="{INK}" stroke-width="2"/>')
            g.append(f'<line x1="{x + w / 2}" y1="9" x2="{x + w / 2}" y2="22" stroke="{INK}" stroke-width="2"/>')
            g.append(f'<rect x="{x + w / 2 - 2.5}" y="13" width="5" height="8" rx="2.5" fill="#ed1aa0"/>')
        else:
            g.append(f'<text x="{x + w / 2}" y="{KH / 2 + 7}" text-anchor="middle" font-size="20" font-weight="700" fill="{INK}">{E(name)}</text>')
        if h:
            hold = True
            g.append(f'<text x="{x + w / 2}" y="{KH + SH + 20}" text-anchor="middle" font-size="14" font-weight="700" fill="#ed1aa0">누른 채</text>')
        parts.append("".join(g))
        x += w
        prev_key = True
    W, H = x + 2, KH + SH + (26 if hold else 2)
    label = " ".join(k.rstrip("*") for k in keys)
    ns = ' xmlns="http://www.w3.org/2000/svg"' if standalone else ""
    return (f'<svg{ns} class="keys" viewBox="-1 -1 {W} {H}" width="{W * scale:.0f}" height="{H * scale:.0f}" '
            f'role="img" aria-label="단축키 {E(label)}" font-family="{E(FONT)}"><title>{E(label)}</title>'
            + "".join(parts) + "</svg>")


def shot(fname, cap):
    tag = ""
    m = re.search(r"\s*\[(사진|도식)\]$", cap)
    if m:
        tag, cap = m.group(1), cap[:m.start()]
    p = f"{SHOT}/{fname}"
    if os.path.exists(os.path.join(ROOT, p)):
        return (f'<figure class="tip-shot"><a href="{p}" target="_blank" rel="noopener"><img src="{p}" alt="{E(cap)}" loading="lazy" /></a>'
                f'<figcaption>{E(cap)}</figcaption></figure>')
    how = {"사진": "휴대폰 사진", "도식": "그림(도식)"}.get(tag, "화면 캡처")
    return (f'<figure class="tip-shot tip-shot-empty"><div><b>{how} 자리</b><code>{E(p)}</code></div>'
            f'<figcaption>{E(cap)}</figcaption></figure>')


def badges(t):
    b = f'<span class="tip-cat c-{t["cat"]}">{E(CATS[t["cat"]])}</span>'
    if t.get("app"):
        b += f'<span class="tip-app">{E(t["app"])}</span>'
    return b


def links(t):
    if not t.get("links"):
        return ""
    btn = "".join((f'<a class="btn {"btn-primary" if i == 0 else "btn-secondary"}" href="{E(u)}" download>{E(l)} ↓</a>' if u.startswith("download/") else
                   f'<a class="btn {"btn-primary" if i == 0 else "btn-secondary"}" href="{E(u)}" target="_blank" rel="noopener">{E(l)} &#8599;</a>')
                  for i, (l, u) in enumerate(t["links"]))
    note = ("직접 눌러 보는 연습 파일이에요." if t["links"][0][1].startswith("download/")
            else "무료 · 공식 배포처로 바로 가요. 학교 업무용 PC는 설치가 막혀 있을 수 있어요.")
    return f'\n      <section class="tip-dl" aria-label="내려받기"><h3>내려받기</h3><p>{note}</p><div class="tip-dl-btns">{btn}</div></section>'


# ------------------------------------------------------------------ 팁 한 페이지
for i, t in enumerate(TIPS):
    prev = TIPS[i - 1] if i > 0 else None
    nxt = TIPS[i + 1] if i + 1 < N else None
    svg = key_svg(t["keys"])
    open(os.path.join(ROOT, KEYS, f'{t["no"]}.svg'), "w", encoding="utf-8", newline="\n").write(
        key_svg(t["keys"], standalone=True) + "\n")
    a = [s for s in t["shots"] if s[0].endswith("_a.png")]
    rest = [s for s in t["shots"] if not s[0].endswith("_a.png")]
    steps = "".join(f"<li>{E(s)}</li>" for s in t["steps"])
    body = f'''<main class="shell page tip-page" id="top">
    <p class="crumb"><a class="btn btn-secondary btn-sm" href="tips.html">← 하루 팁 목록</a><span class="here">지금 여기 · 하루 한 팁 › <strong>Day {t["no"]}</strong><span class="pos">{i + 1} / {N}</span></span></p>
    <article class="tip" aria-labelledby="tip-h">
      <header class="tip-head">
        <p class="tip-kicker">하루 한 팁 · Day {t["no"]}</p>
        <h2 id="tip-h">{E(t["title"])}</h2>
        <p class="tip-badges">{badges(t)}</p>
        <div class="tip-keys">{svg}</div>
      </header>
      <section class="tip-sec">
        <h3><span class="tip-step">1</span>이런 때</h3>
        <p class="tip-when">{E(t["when"])}</p>
        <div class="tip-shots n{len(a)}">{"".join(shot(*s) for s in a)}</div>
      </section>
      <section class="tip-sec">
        <h3><span class="tip-step">2</span>이렇게</h3>
        <ol class="tip-how">{steps}</ol>
        <div class="tip-shots n{len(rest)}">{"".join(shot(*s) for s in rest)}</div>
      </section>
      <p class="tip-extra"><b>덧붙임</b>{E(t["extra"])}</p>{links(t)}
    </article>
    <nav class="pager" aria-label="이전 다음">''' + (
        f'<a class="btn btn-secondary" href="t{prev["no"]}.html">← Day {prev["no"]}</a>' if prev else "<span></span>") + \
        '<a class="btn btn-primary" href="tips.html">목록</a>' + (
        f'<a class="btn btn-secondary" href="t{nxt["no"]}.html">Day {nxt["no"]} →</a>' if nxt else "<span></span>") + '''</nav>
  </main>'''
    page = head(f'Day {t["no"]} {t["title"]} · 하루 한 팁', f'{t["title"]} — {t["when"]}') + TOP + body + FOOT
    open(os.path.join(ROOT, f't{t["no"]}.html'), "w", encoding="utf-8", newline="\n").write(page)

# ------------------------------------------------------------------ 목록
PZIP = "download/하루팁_설치프로그램.zip"
PACK = ""
if os.path.exists(os.path.join(ROOT, PZIP)):
    mb = os.path.getsize(os.path.join(ROOT, PZIP)) / 1024 / 1024
    PACK = (f'      <div class="tip-pack"><div><b>무료 프로그램 한 번에 받기</b>'
            f'<span>줌잇 · 디토 · 에브리싱(파일 찾기) · 연수 소리 끊김 알림 + 직접 만드는 프롬프트. PowerToys(Day 18)는 커서 따로 받아요.</span></div>'
            f'<div class="tip-pack-btns"><a class="btn btn-primary" href="{quote(PZIP)}" download>설치 프로그램 zip ({mb:.0f}MB) ↓</a>'
            f'<a class="btn btn-secondary" href="https://github.com/microsoft/PowerToys/releases/latest" target="_blank" rel="noopener">PowerToys &#8599;</a></div></div>')

cards = "".join(
    f'<a class="tip-card" id="tip-{t["no"]}" href="t{t["no"]}.html"><span class="tip-card-no">Day {t["no"]}</span>'
    f'<span class="tip-card-keys">{key_svg(t["keys"], scale=0.6)}</span><b>{E(t["title"])}</b>'
    f'<span class="hub-sub">{E(t["when"])}</span><span class="tip-badges">{badges(t)}</span></a>'
    for t in TIPS)
body = f'''<main class="shell page tip-page" id="top">
    <p class="crumb"><a class="btn btn-secondary btn-sm" href="index.html">← 홈</a><span class="here">지금 여기 · <strong>하루 한 팁</strong></span></p>
    <section class="tip-hero">
      <p class="tip-kicker">하루 한 팁 · 교실 단축키 {N}선</p>
      <h2>오늘 하나만<br />손에 익혀요</h2>
      <div class="tip-today" data-tip-start="{START}" data-tip-count="{N}" hidden>
        <span class="tip-today-k">오늘의 팁</span><a class="tip-today-a" href="t01.html"></a>
      </div>
{PACK}
    </section>
    <div class="tip-grid">{cards}</div>
  </main>'''
open(os.path.join(ROOT, "tips.html"), "w", encoding="utf-8", newline="\n").write(
    head("하루 한 팁 · 교실 단축키", "교실 현장 선생님을 위한 하루 한 개 단축키 팁") + TOP + body + FOOT)

have = sum(os.path.exists(os.path.join(ROOT, SHOT, s[0])) for t in TIPS for s in t["shots"])
total = sum(len(t["shots"]) for t in TIPS)
print(f"tips.html + t01~t{TIPS[-1]['no']}.html + 단축키 SVG {N}개 · 캡처 {have}/{total}장")
