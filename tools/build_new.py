# -*- coding: utf-8 -*-
"""myfirstaigent 사이트 만들기 — 홈(허브) + 페이지별 구성
   - 홈: 에이전트 AI 개념 · 시작 준비 · 영역별 실습 01~09 · 클로드 · 정리 카드
   - 개념·시작 준비·클로드·정리 페이지의 글은 기존 inline-ai-setup index.html 내용 그대로
   - 실습 페이지: 단계마다 가이드 + 사진 + 프롬프트(실습 폴더의 프롬프트.txt 원문). 정답·개별 다운로드 없음
   사용: python build_new.py <기존 저장소> <실습 폴더(inlineAI_실습)> <미리보기 png 폴더> <출력 폴더>"""
import os, re, sys, html, shutil, zipfile
from urllib.parse import quote, unquote
sys.stdout.reconfigure(encoding="utf-8")

OLD, MAT, SHOTS, OUT = sys.argv[1:5]
E = html.escape
old = open(os.path.join(OLD, "index.html"), encoding="utf-8").read()


def url(p):
    return quote(p.replace(os.sep, "/"), safe="/")


def size(p):
    s = os.path.getsize(p)
    return f"{s/1024/1024:.0f}MB" if s > 1024 * 1024 else f"{max(1, round(s/1024))}KB"


# ------------------------------------------------------------------ 전체 zip 하나만
os.makedirs(os.path.join(OUT, "download"), exist_ok=True)
ZIP = os.path.join(OUT, "download", "inlineAI_실습.zip")
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(MAT):
        for fn in sorted(fs):
            full = os.path.join(dp, fn)
            z.write(full, os.path.join("inlineAI_실습", os.path.relpath(full, MAT)))
ZIP_HREF = "download/" + quote("inlineAI_실습.zip")
ZIP_SIZE = size(ZIP)
shutil.copy(os.path.join(OLD, "download", "클로드_스킬_school-official-docs.zip"), os.path.join(OUT, "download"))

# ------------------------------------------------------------------ 기존 글 잘라 오기


def section(sid):
    a = old.index(f'<section class="lecture" id="{sid}"')
    b = old.index("</section>", a) + len("</section>")
    return old[a:b]


def detail_inner(sec):
    a = sec.index('<div class="lecture-detail-inner">') + len('<div class="lecture-detail-inner">')
    b = sec.rindex("</div>\n      </div>\n    </section>")
    return sec[a:b]


s00 = detail_inner(section("s00"))
parts = re.split(r'(?=<div class="guide-mix|<div class="guide-key|<h3 class="sec-h)', s00)
# 0 빈칸 1 로컬이라 좋은 점 2 에이전트 AI라서 3 여섯 단계 4 복사 안내 5 지시사항 6 안전장치 7 업무 지침
assert "로컬이라" in parts[1] and "에이전트 AI라서" in parts[2] and "여섯 단계" in parts[3] and "업무 지침" in parts[7]
CONCEPT = parts[1] + parts[2]
p4 = re.sub(r" ?한 페이지로 모아 둔 .{0,200}?있어요\.", "", parts[4])
p4 = p4.replace("실습마다 <strong>[펼치기]</strong> → 프롬프트 저장소의", "실습 페이지의 프롬프트")
p6 = parts[6].replace("프롬프트마다 <strong>'새 이름으로 저장'</strong>이 들어 있어요.",
                      "지시사항에 <strong>'새 이름으로 저장'</strong>이 들어 있어요.")
GUIDE = ('<div class="guide-mix"><p class="mix-highlight">🧭 업무 지침</p><h3>00_업무지침 — AI의 업무 매뉴얼</h3>'
         '<p class="mix-lead">AI가 일하기 전에 먼저 읽는 <strong>업무 매뉴얼</strong>이에요. inlineAI_실습 안에 들어 있어서 폴더를 초대하면 같이 들어가요.</p>'
         '<div class="key-grid hz">'
         '<div class="key-item"><span class="key-label">01 짧은판</span><p class="key-text">지시사항에 붙여 <strong>매번 같은 규칙</strong>으로</p></div>'
         '<div class="key-item"><span class="key-label">공문서 작성 규정</span><p class="key-text">경기도교육청 원문 PDF — <strong>근거 자료</strong></p></div>'
         '<div class="key-item"><span class="key-label">AI 학습용</span><p class="key-text">규정을 AI가 읽기 좋게 정리 — <strong>기안문 표기·점검표</strong></p></div>'
         '</div><p class="key-foot">쓰는 법은 한 줄: "00_업무지침 폴더의 규칙을 따라서, 열려 있는 계획서로 기안문 본문을 써 줘."</p></div>')
ZIPBOX = (f'<div class="guide-mix"><p class="mix-highlight">📦 실습 자료</p><h3>실습 자료는 이것 하나만 받아요</h3>'
          f'<p class="mix-lead">받아서 <strong>바탕화면</strong>에 압축을 풀면 <strong>inlineAI_실습</strong> 폴더가 생겨요. 실습 01~09 파일이 모두 들어 있어요.</p>'
          f'<div class="practice-download row"><a class="btn btn-primary" href="{ZIP_HREF}" download>실습 자료 전체 내려받기 (zip · {ZIP_SIZE}) ↓</a></div></div>')
START = ZIPBOX + parts[3] + p4 + parts[5] + p6 + GUIDE

CLAUDE = detail_inner(section("s09"))
WRAP = detail_inner(section("s10"))
WRAP = WRAP.replace('href="download/inlineAI_실습.zip"', f'href="{ZIP_HREF}"')
# 「빠른 AI가 좋은 AI일까요?」 쇼츠는 도입(개념)으로
_i = WRAP.index('<div class="guide-mix"><p class="mix-highlight">▶ 쇼츠</p>')
_j = WRAP.index('<div class="guide-key"><h3>오늘 가져가는 것</h3>', _i)
CONCEPT += WRAP[_i:_j]
WRAP = WRAP[:_i] + WRAP[_j:]
# 오늘 가져가는 것: 새 실습 폴더에 맞게 (정답 파일·04 학교기본정보 없음)
WRAP = WRAP.replace('<span class="key-label">00_업무지침</span><p class="key-text">04 학교기본정보만 고치면 <strong>내일부터</strong></p>',
                    '<span class="key-label">00_업무지침</span><p class="key-text">짧은판을 지시사항에 붙여 <strong>내일부터</strong></p>')
WRAP = WRAP.replace('<div class="key-item"><span class="key-label">정답 파일</span><p class="key-text">결과와 <strong>나란히</strong> 놓고 비교</p></div>', '')
WRAP = WRAP.replace('<span class="key-label">프롬프트 저장소</span><p class="key-text">이 페이지에서 <strong>복사</strong>해서 그대로</p>',
                    '<span class="key-label">프롬프트</span><p class="key-text">실습 페이지에서 <strong>복사</strong>해서 그대로</p>')


def lead_of(sid):
    return re.search(r'<p class="lead">(.*?)</p>', section(sid)).group(1)


# ------------------------------------------------------------------ 실습 데이터: (가이드 제목, 가이드 설명, [사진 키], 프롬프트 번호)
def read(p):
    return open(p, encoding="utf-8-sig").read().strip()


def prompts(folder):
    d = os.path.join(MAT, folder)
    if os.path.exists(os.path.join(d, "프롬프트.txt")):
        items = re.split(r"(?m)^\s*\d+\.\s*", read(os.path.join(d, "프롬프트.txt")))
        return [re.sub(r"\n{3,}", "\n\n", x).strip() for x in items if x.strip()]
    return [re.sub(r"^\[[^\]]*\]\s*", "", read(os.path.join(d, "시작_프롬프트.txt"))).strip()]


NEW = "<strong>새 에이전트</strong>로 시작해요. "
P = [
    ("01", "01_다운로드정리", "다운로드<br />폴더 정리", "다운로드", "폴더 하나를 통째로 맡겨요. 사진 골라 합치고, 중복 지우고, 종류별로 모아요.", [
        ("폴더 맡기기", NEW + "입력창 <strong>+</strong> → <strong>폴더 첨부하기</strong> → <strong>다운로드_흉내</strong>. 파일은 안 열어도 돼요.", ["01_folder"]),
        ("사진 보고 고르기", "AI가 사진을 <strong>직접 보고</strong> 꿀벌만 골라 한 장으로 합쳐요.", ["01_photos"]),
        ("중복 지우고 모으기", "지우기 전에 <strong>목록부터</strong> 보여 달라고 해도 돼요.", []),
    ]),
    ("02", "02_가정통신문_양식맞추기", "가정통신문<br />양식 맞추기", "가정통신문", "메모만 주면 우리 학교 양식 그대로 채워요. 다른 학교 양식으로도 옮겨요.", [
        ("기존 양식에 채우기", NEW + "<strong>실습 1</strong>을 한글로 열어요. 메모 내용은 프롬프트에 들어 있어요.", ["02_p1"]),
        ("회신서까지 바꾸기", "<strong>실습 2</strong>를 열어요. '궁금한 내용은 나에게 묻기'가 있어서 AI가 먼저 물어요.", ["02_p2"]),
        ("공문 서식 채우기", "<strong>실습 3</strong> 국외 자율연수 계획서를 열어요. 모르는 칸은 AI가 물어요.", ["02_p3"]),
        ("다른 학교 양식으로", "<strong>실습 4</strong> 백암초 안내장 양식을 열어요. 같은 내용, 다른 양식.", ["02_p4"]),
    ]),
    ("03", "03_한글표만들기", "한글<br />표 만들기", "한글 표", "줄글은 표로, 명렬표는 이름표로. 표 모양은 AI랑 같이 정해요.", [
        ("줄글을 표로", NEW + "<strong>실습 1</strong>을 열고 표로 바꿀 부분을 <strong>마우스로 선택</strong>해요. 표 모양은 AI랑 먼저 의논해요.", ["03_p1"]),
        ("명렬표로 이름 표", "한글 <strong>새 문서</strong>를 열어 두고 시켜요. 명렬표는 AI가 폴더에서 찾아요.", ["03_p3"]),
        ("삼각 이름표 복사", "<strong>실습 2</strong> 삼각 이름표 PPT를 열어요. 전체 인원만큼 복사해요.", ["03_p2"]),
        ("엑셀에서 골라내기", "<strong>실습 3</strong> 명렬표를 엑셀로 열어요.", []),
    ]),
    ("04", "04_작년도문서_업데이트", "작년 문서<br />업데이트", "작년 문서", "올해 날짜만 알려 주면 돼요. 모르는 건 AI가 먼저 물어요.", [
        ("올해로 바꾸기", NEW + "<strong>실습 1</strong> 2025 체육대회 계획을 열어요. AI가 묻는 말에 답해 주세요.", ["04_p1"]),
        ("톤 맞춰 회의록", "<strong>실습 2</strong> 회의록을 열어요. 이 양식의 말투로 협의회 회의록을 써요.", ["04_p2"]),
        ("두 계획서로 회의록", "<strong>실습 3</strong>은 두 파일(기초학력·두드림학교)을 <strong>함께</strong> 써요. AI가 폴더에서 둘 다 읽어요.", ["04_p3a", "04_p3b"]),
    ]),
    ("05", "05_행정처리_도움받기", "행정 처리<br />도움받기", "행정", "받은 견적서로 품의 업로드 양식까지 알아서 채워요.", [
        ("견적서 → 품의 양식", NEW + "<strong>품의 업로드 양식</strong>을 엑셀로 열어요. 지마켓 견적서는 AI가 폴더에서 찾아요.", ["05_quote", "05_form"]),
    ]),
    ("06", "06_계획서로_기안문쓰기", "계획서로<br />기안문 쓰기", "기안문", "계획 업데이트와 협조 공문을 한 번에. 제안서 그림은 검색해서 파악해요.", [
        ("계획 + 협조 공문", NEW + "<strong>실습 1</strong> 소방훈련 계획을 열어요. 결과물이 두 개 나와요.", ["06_p1"]),
        ("제안서로 행사 설계", "<strong>실습 2</strong> AI 과학의 날 계획을 열어요. 백암초 제안서 그림을 보고 <strong>인터넷 검색</strong>까지 해요.", ["06_p2", "06_p2b"]),
    ]),
    ("07", "07_계획서로_보고서쓰기", "계획서로<br />보고서 쓰기", "보고서", "운영계획과 만족도 결과로 결과보고서를. 먼저 묻고 시작해요.", [
        ("계획서·통계로 보고서", NEW + "<strong>결과보고서_양식</strong>을 열어요. 운영계획과 만족도 엑셀은 AI가 폴더에서 읽어요.", ["07_form", "07_plan", "07_stats"]),
    ]),
    ("08", "08_계획서_문서로_PPT만들기", "계획서로<br />PPT 만들기", "PPT", "계획서 하나로 학교 양식 PPT를, 이어서 원하는 스타일로.", [
        ("학교 양식으로", NEW + "<strong>우리학교_PPT_양식</strong>을 파워포인트로 열어요.", ["08_tpl"]),
        ("원하는 스타일로", "같은 대화에서 이어서 시켜요. 디자인 가이드와 스타일 참고 PDF를 AI가 읽어요.", ["08_style"]),
    ]),
    ("09", "09. 퀴즈 자동화", "교과서로<br />퀴즈 만들기", "퀴즈", "교과서 PDF를 주면 블루킷에 바로 올리는 퀴즈 엑셀이 나와요.", [
        ("자료 주고 퀴즈 만들기", NEW + "<strong>science_5-2-4.pdf</strong>를 채팅창에 끌어다 놓고 붙여 넣어요. 대상·문제 수는 고쳐 써도 돼요.", ["09_book", "09_tpl"]),
    ]),
]
TILES = ["tile-code", "tile-image", "tile-write", "tile-notebook", "tile-eval", "tile-video", "tile-flow"]
CIRCLE = "①②③④⑤⑥⑦⑧⑨"
os.makedirs(os.path.join(OUT, "assets", "practice"), exist_ok=True)


def photo(key):
    shutil.copy(os.path.join(SHOTS, key + ".png"), os.path.join(OUT, "assets", "practice"))
    src = f"assets/practice/{key}.png"
    return f'<figure class="guide-shot"><a href="{src}" target="_blank" rel="noopener"><img src="{src}" alt="실습 파일 미리보기" loading="lazy" /></a></figure>'


LABEL = re.compile(r"(?m)^(할 일|조건|끝나면|메모):")


def prompt_row(cat, text):
    return (f'<div class="prompt-row"><div class="pbody">'
            f'<span class="ptext">{LABEL.sub(lambda m: "<b class=" + chr(34) + "plabel" + chr(34) + ">" + m.group(1) + ":</b>", E(text))}</span></div><button class="prompt-copy" type="button">복사</button></div>')


# ------------------------------------------------------------------ 페이지 틀
PAGES = [("concept.html", "에이전트 AI란?", ("1", "개념")), ("start.html", "시작 준비", ("2", "준비"))] + \
        [(f"p{no}.html", re.sub("<br />", " ", t), (no, nav)) for no, _, t, nav, _, _ in P] + \
        [("claude.html", "클로드 코워크로 한 걸음 더", ("4", "클로드")), ("wrap.html", "정리 · 내일부터 이렇게", ("✓", "정리"))]
PAGES = [(f, t, (str(i), n[1])) for i, (f, t, n) in enumerate(PAGES, 1)]  # 탭 번호는 1~13 차례대로
GROUP = {"concept.html": "에이전트 AI란?", "start.html": "시작 준비", "claude.html": "클로드 챕터", "wrap.html": "정리"}

HEAD = '''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light" />
  <title>{title}</title>
  <meta name="description" content="내 업무 파일, AI에게 맡겨 보기 — 학교 현장 에이전트 AI 실습" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Black+Han+Sans&display=swap" rel="stylesheet" />
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <link rel="stylesheet" href="styles.css" />
  <link rel="stylesheet" href="extra.css" />
</head>
<body>
'''


def topbar(current):
    def tab(f, num, name):
        on = f == current
        return (f'<a class="tab{" on" if on else ""}" href="{f}"{" aria-current=page" if on else ""}>'
                + (f'<span class="tab-no">{E(num)}</span>' if num else "") + f'{E(name)}</a>')
    tabs = tab("index.html", "", "홈") + "".join(tab(f, n[0], n[1]) for f, _, n in PAGES)
    return f'''  <div class="utility-bar">
    <div class="shell">
      <a class="caption-sm" href="start.html">처음 준비</a>
      <a class="caption-sm deck-tab-pdf" href="{ZIP_HREF}" download>실습 자료 zip ↓</a>
      <a class="deck-tab deck-tab-padlet" href="https://portal.inline-ai.com/invitation-promotion?code=K2YERY3H" target="_blank" rel="noopener">초대 이벤트 &#8599;</a>
      <a class="deck-tab" href="lecture.html" title="강의안 (번호 입력 후 열려요)">강의안 &#128274;</a>
      <button class="deck-tab addr-open" type="button" title="사이트 주소와 QR 크게 보기">주소 · QR</button>
    </div>
  </div>
  <header class="primary-nav">
    <div class="shell">
      <a class="brand" href="index.html"><span class="swoosh">내 첫</span> 에이전트 AI</a>
    </div>
    <nav class="tabs" aria-label="목차"><div class="shell tabs-row">{tabs}</div></nav>
  </header>
'''


FOOT = '''
  <div class="addr" id="addr" role="dialog" aria-label="사이트 주소와 QR" hidden>
    <button class="addr-x" type="button" aria-label="닫기">✕</button>
    <div class="addr-box"><p class="addr-k">사이트 주소</p><p class="addr-url">joo.is/오현에이전트</p>
    <div class="addr-qr">{QR}</div><p class="addr-hint">휴대폰 카메라로 찍어도 열려요 · Esc로 닫기</p></div>
  </div>
  <footer class="site-footer shell">
    <div class="footer-fine utility-xs">
      <span>내 첫 에이전트 AI · 학교 현장 실습</span>
      <span class="grow">실습 자료 속 학교·사람 이름은 실습용이에요. 화면은 2026. 10. 기준이라 앱 업데이트로 바뀔 수 있어요.</span>
    </div>
  </footer>
  <div class="toast" id="toast" role="status" aria-live="polite"></div>
  <script src="site.js"></script>
</body>
</html>
'''


def page(fname, title, kicker, h2, lead, tile, no, body):
    i = [f for f, _, _ in PAGES].index(fname)
    prev = PAGES[i - 1] if i > 0 else None
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    pn = ('<nav class="pager" aria-label="이전 다음">'
          + (f'<a class="btn btn-secondary" href="{prev[0]}">← {E(prev[1])}</a>' if prev else "<span></span>")
          + '<a class="btn btn-primary" href="index.html">홈</a>'
          + (f'<a class="btn btn-secondary" href="{nxt[0]}">{E(nxt[1])} →</a>' if nxt else "<span></span>") + "</nav>")
    html_ = (HEAD.format(title=E(title) + " · 내 첫 에이전트 AI") + topbar(fname)
             + f'''  <main class="shell page" id="top">
    <p class="crumb"><a class="btn btn-secondary btn-sm" href="index.html">← 홈</a><span class="here">지금 여기 · {GROUP.get(fname, "영역별 실습")} › <strong>{E(PAGES[i][2][0])} {E(PAGES[i][2][1])}</strong><span class="pos">{i+1} / {len(PAGES)}</span></span></p>
    <section class="lecture open" aria-label="{E(title)}">
      <div class="lecture-row">
        <div class="lecture-media {tile}"><span class="lecture-no">{no}</span></div>
        <div class="lecture-copy">
          <p class="lecture-kicker">{kicker}</p>
          <h2>{h2}</h2>
          <p class="lead">{lead}</p>
        </div>
      </div>
      <div class="lecture-detail">
        <div class="lecture-detail-inner">{body}
        </div>
      </div>
    </section>
    {pn}
  </main>
''' + FOOT)
    open(os.path.join(OUT, fname), "w", encoding="utf-8").write(html_)
    return html_


import qrcode as _qr
from urllib.parse import quote as _q
def _qrsvg(text):
    q = _qr.QRCode(border=2); q.add_data(text); q.make(); m = q.get_matrix(); n = len(m)
    r = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return f'<svg viewBox="0 0 {n} {n}" role="img" aria-label="QR: joo.is/오현에이전트" shape-rendering="crispEdges"><rect width="{n}" height="{n}" fill="#fff"/><g fill="#111">{r}</g></svg>'
FOOT = FOOT.replace("{QR}", _qrsvg("https://joo.is/" + _q("오현에이전트")))
ALLHTML = []
ALLHTML.append(page("concept.html", "에이전트 AI란?", "STEP 1 · 개념", "에이전트 AI란?",
                    "묻는 말에 답만 하는 챗봇이 아니에요. 내 컴퓨터에서 <strong>일을 맡는</strong> AI예요.", "tile-flow", "AI", CONCEPT))
ALLHTML.append(page("start.html", "시작 준비", "STEP 2 · 준비", "시작 준비<br />AI를 내 컴퓨터에",
                    "실습 자료 받기, 설치·가입, 폴더 초대, 지시사항까지. 여기만 따라 하면 끝나요.", "tile-flow", "00", START))

for k, (no, folder, title, nav, lead, steps) in enumerate(P):
    ps = prompts(folder)
    assert len(ps) == len(steps), (folder, len(ps), len(steps))
    out = []
    for j, ((gt, gd, keys), pr) in enumerate(zip(steps, ps)):
        shots = "".join(photo(x) for x in keys)
        out.append(f'<div class="pstep"><div class="pstep-head"><span class="guide-no">{j+1}</span><h3>{E(gt)}</h3></div>'
                   f'<p class="guide-desc">{gd}</p>'
                   + f'<div class="prompt-list">{prompt_row(CIRCLE[j], pr)}</div>'
                   + (f'<div class="pstep-shots n{min(len(keys), 3)}">{shots}</div>' if shots else "") + '</div>')
    body = (f'<p class="pnote">순서: <strong>파일 열기</strong> → 프롬프트 <strong>[복사]</strong> → 입력창 <strong>Ctrl+V</strong> → AI가 물으면 답하기 → 결과 확인. '
            f'파일은 바탕화면 <strong>inlineAI_실습/{E(folder)}</strong> 폴더에 있어요.</p>' + "".join(out))
    ALLHTML.append(page(f"p{no}.html", re.sub("<br />", " ", title), f"실습 {no}", title, lead, TILES[k % len(TILES)], no, body))

ALLHTML.append(page("claude.html", "클로드 코워크로 한 걸음 더", "STEP 4 · 클로드", "클로드 코워크로<br />한 걸음 더", lead_of("s09"), "tile-video", "C", CLAUDE))
ALLHTML.append(page("wrap.html", "정리 · 내일부터 이렇게", "마무리", "정리 ·<br />내일부터 이렇게", lead_of("s10"), "tile-flow", "✓", WRAP))

# ------------------------------------------------------------------ 홈
hero = old[old.index('<section class="hero"'):old.index('<div class="howto">')]
hero = re.sub(r"실습 자료 전체 내려받기 \([\d.]+MB\)", f"실습 자료 전체 내려받기 ({ZIP_SIZE})", hero)
hero = hero.replace('href="download/inlineAI_%EC%8B%A4%EC%8A%B5.zip"', f'href="{ZIP_HREF}"')
hero = hero.replace('<a class="btn btn-ghost" href="lecture.html">강의 화면 보기</a>', '<a class="btn btn-ghost" href="start.html">처음 준비 →</a>')
hero = hero.replace("교원 연수 · inline AI", "교원 연수 · 학교 현장 에이전트 AI")


def card(href, tag, name, sub, accent=False):
    return (f'<a class="hub-card" href="{href}"><span class="hub-tag{" p" if accent else ""}">{E(tag)}</span>'
            f'<b>{E(name)}</b><span class="hub-sub">{E(sub)}</span></a>')


home_body = (hero
             + '<section class="hub"><h2 class="hub-h"><span>1</span>에이전트 AI란?</h2><div class="hub-grid">'
             + card("concept.html", "개념", "챗봇이 아니라 일을 맡는 AI", "로컬이라 좋은 점 · 에이전트 AI라서 · 빠른 AI가 좋은 AI일까요?")
             + '</div></section>'
             + '<section class="hub"><h2 class="hub-h"><span>2</span>시작 준비</h2><div class="hub-grid">'
             + card("start.html", "준비", "설치 · 가입 · 폴더 초대", "여섯 단계 · 지시사항 · 안전장치 · 업무 지침")
             + f'<a class="hub-card" href="{ZIP_HREF}" download><span class="hub-tag">실습 자료</span><b>inlineAI_실습.zip ↓</b><span class="hub-sub">{ZIP_SIZE} · 바탕화면에 압축 풀기</span></a>'
             + card("https://portal.inline-ai.com/invitation-promotion?code=K2YERY3H", "초대 이벤트", "무료 1,000 크레딧", "초대 코드 K2YERY3H", True)
             + '</div></section>'
             + '<section class="hub"><h2 class="hub-h"><span>3</span>영역별 실습</h2><p class="hub-lead">영역마다 단계별 가이드 · 사진 · 프롬프트만 있어요. 프롬프트는 평소 말하듯 쓴 그대로예요.</p><div class="hub-grid">'
             + "".join(card(f"p{no}.html", f"실습 {no}", re.sub("<br />", " ", t), l) for no, _, t, _, l, _ in P)
             + '</div></section>'
             + '<section class="hub"><h2 class="hub-h"><span>4</span>클로드 챕터</h2><div class="hub-grid">'
             + card("claude.html", "클로드", "클로드 코워크로 한 걸음 더", "앱 준비 · 업무 지침 스킬 · 예약")
             + card("wrap.html", "정리", "내일부터 이렇게", "아침 루틴 · 여러 AI에게 동시에 · 오늘 가져가는 것")
             + '</div></section>')
home = HEAD.format(title="내 첫 에이전트 AI") + topbar("index.html") + f'  <main class="shell" id="top">\n{home_body}\n  </main>\n' + FOOT
home = home.replace('<link rel="stylesheet" href="extra.css" />', '<link rel="stylesheet" href="extra.css" />')
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(home)
ALLHTML.append(home)

# ------------------------------------------------------------------ 정적 파일
shutil.copy(os.path.join(OLD, "styles.css"), OUT)
# 강의안: 기존 lecture.html (번호 1111 잠금 내장) + 쓰는 그림
shutil.copy(os.path.join(OLD, "lecture.html"), OUT)
ALLHTML_LECTURE = open(os.path.join(OLD, "lecture.html"), encoding="utf-8").read()
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra.css"), OUT)
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site.js"), OUT)
open(os.path.join(OUT, ".nojekyll"), "w").close()
refs = set()
for h in ALLHTML:
    refs |= set(re.findall(r'(?:src|href)="(assets/shot/[^"]+|assets/files/[^"]+)"', h))
refs |= set(re.findall(r'(?:src|href)="(assets/[^"]+)"', ALLHTML_LECTURE))
for r in sorted(refs):
    src, dst = os.path.join(OLD, unquote(r)), os.path.join(OUT, unquote(r))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)

bad = []
for h in ALLHTML:
    for r in re.findall(r'(?:src|href)="([^"#]+)"', h):
        if not r.startswith(("http", "mailto")) and not os.path.exists(os.path.join(OUT, unquote(r))):
            bad.append(r)
print("페이지", len(ALLHTML), "· 그림", len(refs), "· zip", ZIP_SIZE, "· 깨진 링크", sorted(set(bad)) or "없음")
