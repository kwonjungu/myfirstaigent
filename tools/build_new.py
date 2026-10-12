# -*- coding: utf-8 -*-
"""myfirstaigent 사이트 만들기 — 홈(허브) + 페이지별 구성
   - 홈: 에이전트 AI 개념 · 시작 준비 · 영역별 실습(개수는 P에서, 기본→보통→도전) · 클로드 · 정리 카드
   - 실습 목록·배지(시작 방법·예상 시간·난이도)는 practices.py(P·INFO·MODE)에서
   - 개념·시작 준비·클로드·정리 페이지의 글은 기존 inline-ai-setup index.html 내용 그대로
   - 실습 페이지: 단계마다 가이드 + 사진 + 프롬프트(실습 폴더의 프롬프트.txt 원문). 정답·개별 다운로드 없음
   사용: python build_new.py <기존 저장소> <실습 폴더(inlineAI_실습)> <미리보기 png 폴더> <출력 폴더>"""
import os, re, sys, html, shutil, zipfile
from urllib.parse import quote, unquote
sys.stdout.reconfigure(encoding="utf-8")

OLD, MAT, SHOTS, OUT = sys.argv[1:5]
E = html.escape


def rep(s, a, b, n=1):
    """원문 고치기 — 원문이 바뀌어 못 찾으면 바로 멈춘다(조용히 놓치지 않게)"""
    assert s.count(a) == n, ("고칠 문장을 못 찾음", s.count(a), a[:80])
    return s.replace(a, b)

old = open(os.path.join(OLD, "index.html"), encoding="utf-8").read()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from practices import P, INFO, MODE  # noqa: E402
assert [x[0] for x in P] == sorted(INFO), "P와 INFO의 실습 번호가 달라요"
RANGE = f"{P[0][0]}~{P[-1][0]}"  # 예: 01~12 (개수는 P에서)


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
CMP = ('<div class="guide-mix"><p class="mix-highlight">💬 → 🛠 비교</p><h3>대화형 AI와 무엇이 다를까요?</h3>'
       '<p class="mix-lead">챗GPT 같은 대화형 AI는 <strong>답</strong>을 주고, 에이전트 AI는 <strong>일</strong>을 해요.</p>'
       '<div class="cmp-wrap"><table class="cmp"><thead><tr><th></th><th>대화형 AI (챗봇)</th><th>에이전트 AI (inline AI)</th></tr></thead><tbody><tr><th>일하는 곳</th><td>웹 채팅창</td><td>내 컴퓨터의 <b>폴더·문서</b></td></tr><tr><th>파일</th><td>하나씩 올리고, 답을 <b>복사해 붙이기</b></td><td>폴더째 맡기면 <b>직접 열고 고치고 저장</b></td></tr><tr><th>결과</th><td>채팅 답(글)</td><td>한글·엑셀·그림 <b>파일</b></td></tr><tr><th>일하는 방식</th><td>한 번 묻고 한 번 답</td><td>계획 → <b>여러 단계 실행</b> → 스스로 확인</td></tr><tr><th>내가 할 일</th><td>답을 양식에 옮기고 표 맞추기</td><td>결과 파일을 열어 보고 <b>다듬기</b></td></tr><tr><th>걸리는 시간</th><td>몇 초</td><td>1~6분 — <b>시켜 두고 다른 일</b></td></tr><tr><th>가정통신문이라면</th><td>글만 써 줘요. 한글 양식에 붙이고 표 맞추는 건 내 몫</td><td>학교 양식 파일에 <b>직접 채워 새 이름으로 저장</b>해요 (실측 약 3분)</td></tr></tbody></table></div></div>')
CONCEPT = CMP + parts[1] + parts[2]
p4 = re.sub(r" ?한 페이지로 모아 둔 .{0,200}?있어요\.", "", parts[4])
p4 = p4.replace("실습마다 <strong>[펼치기]</strong> → 프롬프트 저장소의", "실습 페이지의 프롬프트")
p3 = rep(parts[3], " 대신 폴더를 실습 폴더 하나로 막아 두고, 고치기 전에 목록을 먼저 받아요.",
         " 대신 폴더를 실습 폴더 하나로 막아 둬요.")
# 지시사항 짧은판: 실습 자료의 최신 원문(1번 '바로 실행')으로
SHORT = open(os.path.join(MAT, "00_업무지침", "01_기본지침_짧은판.txt"), encoding="utf-8-sig").read().strip()
assert "바로 실행" in SHORT
_a = parts[5].index('<span class="ptext">나는 ') + len('<span class="ptext">')
_b = parts[5].index("</span>", _a)
p5 = parts[5][:_a] + E(SHORT) + parts[5][_b:]
p6 = rep(parts[6], "프롬프트마다 <strong>'새 이름으로 저장'</strong>이 들어 있어요.",
         "지시사항에 <strong>'새 이름으로 저장'</strong>이 들어 있어요.")
# 지시사항 1번이 '바로 실행'이라 목록은 필요할 때만
p6 = rep(p6, "<span class=\"key-label\">목록 먼저</span><p class=\"key-text\">'고치기 전에 <strong>목록으로 먼저</strong> 보여 줘. 아직 고치지 마.'</p>",
         "<span class=\"key-label\">목록은 필요할 때만</span><p class=\"key-text\">기본은 바로 실행. 필요할 때만 <strong>'목록 먼저 보여 줘'</strong>.</p>")
p6 = rep(p6, "실습이 바뀌면 <strong>새 에이전트</strong>", "실습이 바뀌면 <strong>새로 시작</strong>")
GUIDE = ('<div class="guide-mix"><p class="mix-highlight">🧭 업무 지침</p><h3>00_업무지침 — AI의 업무 매뉴얼</h3>'
         '<p class="mix-lead">공문서 쓸 때 AI가 읽는 <strong>업무 매뉴얼</strong>이에요. inlineAI_실습 안에 들어 있어서 폴더를 초대하면 같이 들어가요.</p>'
         '<div class="key-grid hz">'
         '<div class="key-item"><span class="key-label">01 짧은판</span><p class="key-text">지시사항에 붙여 <strong>매번 같은 규칙</strong>으로</p></div>'
         '<div class="key-item"><span class="key-label">공문서 작성 규정</span><p class="key-text">경기도교육청 원문 PDF — <strong>근거 자료</strong></p></div>'
         '<div class="key-item"><span class="key-label">AI 학습용</span><p class="key-text">규정을 AI가 읽기 좋게 정리 — <strong>기안문 표기·점검표</strong></p></div>'
         '</div><p class="key-foot">쓰는 법은 한 줄: "공문서 작성법 md 규칙을 따라서, 열려 있는 계획서로 기안문 본문을 써 줘."</p></div>')
ZIPBOX = (f'<div class="guide-mix"><p class="mix-highlight">📦 실습 자료</p><h3>실습 자료는 이것 하나만 받아요</h3>'
          f'<p class="mix-lead">받아서 <strong>바탕화면</strong>에 압축을 풀면 <strong>inlineAI_실습</strong> 폴더가 생겨요. 실습 {RANGE} 파일이 모두 들어 있어요.</p>'
          f'<div class="practice-download row"><a class="btn btn-primary" href="{ZIP_HREF}" download>실습 자료 전체 내려받기 (zip · {ZIP_SIZE}) ↓</a></div></div>')
START = ZIPBOX + p3 + p4 + p5 + p6 + GUIDE

CLAUDE = detail_inner(section("s09"))
# ChatGPT 앱 폴더 모드 자리: 캡처(assets/shot/chatgpt/*.png)가 있으면 그림, 없으면 '캡처 예정' 칸
GPT_SHOTS = [("03_folder_connected", "폴더 연결"), ("05_running", "실행 중"), ("07_done", "결과")]


def _gpt_fig(key, cap):
    p = os.path.join(OUT, "assets", "shot", "chatgpt", key + ".png")
    if os.path.exists(p):
        return f'<figure class="gpt-fig"><a href="assets/shot/chatgpt/{key}.png" target="_blank" rel="noopener"><img src="assets/shot/chatgpt/{key}.png" alt="ChatGPT 앱 {cap}" loading="lazy" /></a><figcaption>{cap}</figcaption></figure>'
    return f'<figure class="gpt-fig gpt-empty"><div>캡처 예정</div><figcaption>{cap}</figcaption></figure>'


GPT_BLOCK = ('<div class="guide-mix"><p class="mix-highlight">🟢 ChatGPT 앱</p><h3>ChatGPT 앱 폴더 모드로도</h3>'
             '<p class="mix-lead">같은 실습을 ChatGPT 데스크톱 앱에 폴더를 연결해서 시켜 봤어요. <strong>같은 프롬프트</strong>, 다른 앱.</p>'
             '<div class="gpt-grid">' + "".join(_gpt_fig(k, c) for k, c in GPT_SHOTS) + '</div>'
             '<p class="mix-lead">한글(hwpx) 양식을 그대로 살리는 건 inline AI가 더 편하고, 대화·검색은 ChatGPT 앱이 편해요.</p></div>')
CLAUDE += GPT_BLOCK
WRAP = detail_inner(section("s10"))
WRAP = WRAP.replace('href="download/inlineAI_실습.zip"', f'href="{ZIP_HREF}"')
WRAP = rep(WRAP, "<span class=\"key-label\">고치기 전 목록</span><p class=\"key-text\">'목록 먼저, <strong>아직 고치지 마</strong>'</p>",
           "<span class=\"key-label\">목록은 필요할 때만</span><p class=\"key-text\">기본은 바로 실행, 필요하면 <strong>'목록 먼저'</strong></p>")
# 여러 AI에게 동시에: 새 에이전트끼리는 동시에, 한/글·Excel 편집은 한 번에 하나
_i = WRAP.index('<h3>여러 AI에게 동시에</h3>')
_j = WRAP.index('</div>', WRAP.index('<p class="key-foot">', _i))
WRAP = WRAP[:_i] + ('<h3>여러 AI에게 동시에</h3><p class="key-lead"><strong>새 에이전트</strong>끼리는 동시에 돼요. '
                    '<strong>한/글·Excel 편집</strong>은 한 번에 하나만 해요.</p>'
                    '<div class="key-grid" style="grid-template-columns:repeat(2,1fr)">'
                    '<div class="key-item"><span class="key-label">에이전트 1</span><p class="key-text">다운로드 <strong>폴더 정리</strong></p></div>'
                    '<div class="key-item"><span class="key-label">에이전트 2</span><p class="key-text">엑셀 숫자로 <strong>인포그래픽</strong></p></div>'
                    '<div class="key-item"><span class="key-label">에이전트 3</span><p class="key-text">명렬표로 <strong>삼각 이름표</strong></p></div>'
                    '<div class="key-item"><span class="key-label">에이전트 4</span><p class="key-text">교과서 PDF로 <strong>퀴즈</strong></p></div></div>'
                    '<p class="key-foot">그동안 <strong>한/글 편집하기</strong>로는 가정통신문 <strong>한 개</strong>만. 크레딧은 맡긴 만큼 쓰여요.</p>') + WRAP[_j:]
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
                    '<span class="key-label">프롬프트</span><p class="key-text">실습 페이지에서 <strong>복사</strong>해서 그대로</p></div>'
                    '<div class="key-item"><span class="key-label">실제 업무에선</span><p class="key-text"><strong>짧게</strong> 쓰고 · 자료를 <strong>던지고</strong> · &#x27;모르면 <strong>물어봐</strong>&#x27;</p>')


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



TILES = ["tile-code", "tile-image", "tile-write", "tile-notebook", "tile-eval", "tile-video", "tile-flow"]
CIRCLE = "①②③④⑤⑥⑦⑧⑨"
os.makedirs(os.path.join(OUT, "assets", "practice"), exist_ok=True)


MISSING = []  # 아직 캡처 안 된 미리보기 키 (빌드 끝에 목록 출력)


def photo(key):
    if not os.path.exists(os.path.join(SHOTS, key + ".png")):
        MISSING.append(key)
        return ""
    src_png, dst_dir = os.path.join(SHOTS, key + ".png"), os.path.join(OUT, "assets", "practice")
    if os.path.abspath(os.path.dirname(src_png)) != os.path.abspath(dst_dir):
        shutil.copy(src_png, dst_dir)
    src = f"assets/practice/{key}.png"
    return f'<figure class="guide-shot"><a href="{src}" target="_blank" rel="noopener"><img src="{src}" alt="실습 파일 미리보기" loading="lazy" /></a></figure>'


LABEL = re.compile(r"(?m)^(할 일|조건|끝나면|메모):")


def prompt_row(cat, text):
    return (f'<div class="prompt-row"><div class="pbody">'
            f'<span class="ptext">{LABEL.sub(lambda m: "<b class=" + chr(34) + "plabel" + chr(34) + ">" + m.group(1) + ":</b>", E(text))}</span></div><button class="prompt-copy" type="button">복사</button></div>')


# ------------------------------------------------------------------ 페이지 틀
LEVELS = ["기본", "보통", "도전"]
LVCLS = {"기본": "lv1", "보통": "lv2", "도전": "lv3"}


def when(t):
    return t if ("안팎" in t or "이상" in t) else "약 " + t


def badges(no):
    """시작 방법 · 예상 시간 · 난이도 배지 (practices.INFO)"""
    i = INFO[no]
    return (f'<span class="pbadges"><span class="pb pb-lv {LVCLS[i["level"]]}">{E(i["level"])}</span>'
            f'<span class="pb pb-mode"><i>시작</i>{E(MODE[i["mode"]])}</span>'
            f'<span class="pb"><i>시간</i>{E(when(i["time"]))}</span></span>')


# 모든 실습 페이지 공통 한 줄 안내 (실제 앱과 다른 점)
TIPS = ('<div class="ptips" role="note"><p class="ptips-h">막히면 이렇게</p><ul>'
        '<li>문서 실습은 왼쪽 <strong>한/글 편집하기</strong> · <strong>Excel 편집하기</strong>로 시작해요.</li>'
        '<li>다 됐는데 멈춰 있으면 <strong>전체 수락하기</strong>를 눌러요.</li>'
        '<li>질문이 <strong>선택지 카드</strong>로 뜨면 하나를 눌러요.</li></ul></div>')

# (파일, 제목, (탭 번호, 탭 이름)) — 실습 탭은 실습 번호, 나머지는 홈 묶음 번호(1·2·4·✓)
PAGES = [("concept.html", "에이전트 AI란?", ("1", "개념")), ("start.html", "시작 준비", ("2", "준비"))] +         [(f"p{no}.html", re.sub("<br />", " ", t), (no, nav)) for no, _, t, nav, _, _ in P] +         [("claude.html", "클로드 코워크로 한 걸음 더", ("4", "클로드")), ("wrap.html", "정리 · 내일부터 이렇게", ("✓", "정리"))]
PNO = {f"p{x[0]}.html": x[0] for x in P}  # 실습 페이지 → 실습 번호
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
        if f in PNO:  # 실습은 번호 칩 (지금 보는 칩만 이름까지)
            lv = INFO[PNO[f]]["level"]
            return (f'<a class="tab tab-p {LVCLS[lv]}{" on" if on else ""}" href="{f}" title="실습 {E(num)} · {E(name)} ({E(lv)})"'
                    f'{" aria-current=page" if on else ""}><span class="tab-no">{E(num)}</span><span class="tab-name">{E(name)}</span></a>')
        return (f'<a class="tab{" on" if on else ""}" href="{f}"{" aria-current=page" if on else ""}>'
                + (f'<span class="tab-no">{E(num)}</span>' if num else "") + f'{E(name)}</a>')
    tabs = tab("index.html", "", "홈")
    for k, (f, _, n) in enumerate(PAGES):
        if f in PNO and (k == 0 or PAGES[k - 1][0] not in PNO):
            tabs += '<span class="tab-group" aria-hidden="true"><span class="tab-no">3</span>실습</span>'
        tabs += tab(f, n[0], n[1])
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
    <div class="addr-box"><p class="addr-k">사이트 주소</p><p class="addr-url">joo.is/처음에이전트</p>
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


def page(fname, title, kicker, h2, lead, tile, no, body, extra=""):
    i = [f for f, _, _ in PAGES].index(fname)
    prev = PAGES[i - 1] if i > 0 else None
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    pn = ('<nav class="pager" aria-label="이전 다음">'
          + (f'<a class="btn btn-secondary" href="{prev[0]}">← {E(prev[1])}</a>' if prev else "<span></span>")
          + '<a class="btn btn-primary" href="index.html">홈</a>'
          + (f'<a class="btn btn-secondary" href="{nxt[0]}">{E(nxt[1])} →</a>' if nxt else "<span></span>") + "</nav>")
    html_ = (HEAD.format(title=E(title) + " · 내 첫 에이전트 AI") + topbar(fname)
             + f'''  <main class="shell page" id="top">
    <p class="crumb"><a class="btn btn-secondary btn-sm" href="index.html">← 홈</a><span class="here">지금 여기 · {GROUP.get(fname, "영역별 실습")} › <strong>{"실습 " if fname in PNO else ""}{E(PAGES[i][2][0])} {E(PAGES[i][2][1])}</strong><span class="pos">{i+1} / {len(PAGES)}</span></span></p>
    <section class="lecture open" aria-label="{E(title)}">
      <div class="lecture-row">
        <div class="lecture-media {tile}"><span class="lecture-no">{no}</span></div>
        <div class="lecture-copy">
          <p class="lecture-kicker">{kicker}</p>
          <h2>{h2}</h2>
          <p class="lead">{lead}</p>{extra}
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
    return f'<svg viewBox="0 0 {n} {n}" role="img" aria-label="QR: joo.is/처음에이전트" shape-rendering="crispEdges"><rect width="{n}" height="{n}" fill="#fff"/><g fill="#111">{r}</g></svg>'
FOOT = FOOT.replace("{QR}", _qrsvg("https://joo.is/" + _q("처음에이전트")))
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
                   + (f'<div class="pstep-shots n{min(shots.count("<figure"), 3)}">{shots}</div>' if shots else "") + '</div>')
    body = (f'<p class="pnote">순서: <strong>파일 열기</strong> → 프롬프트 <strong>[복사]</strong> → 입력창 <strong>Ctrl+V</strong> → AI가 물으면 답하기 → 결과 확인. '
            f'파일은 바탕화면 <strong>inlineAI_실습/{E(folder)}</strong> 폴더에 있어요.</p>' + TIPS + "".join(out))
    ALLHTML.append(page(f"p{no}.html", re.sub("<br />", " ", title), f"실습 {no}", title, lead, TILES[k % len(TILES)], no, body, badges(no)))

ALLHTML.append(page("claude.html", "클로드 코워크로 한 걸음 더", "STEP 4 · 클로드", "클로드 코워크로<br />한 걸음 더", lead_of("s09"), "tile-video", "C", CLAUDE))
ALLHTML.append(page("wrap.html", "정리 · 내일부터 이렇게", "마무리", "정리 ·<br />내일부터 이렇게", lead_of("s10"), "tile-flow", "✓", WRAP))

# ------------------------------------------------------------------ 홈
hero = old[old.index('<section class="hero"'):old.index('<div class="howto">')]
hero, _n = re.subn(r"실습 자료 전체 내려받기 \([\d.]+MB\)", f"실습 자료 전체 내려받기 ({ZIP_SIZE})", hero)
assert _n == 1, "홈 zip 크기 문구를 못 찾음"
hero = hero.replace('href="download/inlineAI_%EC%8B%A4%EC%8A%B5.zip"', f'href="{ZIP_HREF}"')
hero = hero.replace('<a class="btn btn-ghost" href="lecture.html">강의 화면 보기</a>', '<a class="btn btn-ghost" href="start.html">처음 준비 →</a>')
hero = hero.replace("교원 연수 · inline AI", "교원 연수 · 학교 현장 에이전트 AI")


def card(href, tag, name, sub, accent=False, extra=""):
    return (f'<a class="hub-card" href="{href}"><span class="hub-tag{" p" if accent else ""}">{E(tag)}</span>'
            f'<b>{E(name)}</b><span class="hub-sub">{E(sub)}</span>{extra}</a>')


def level_grids():
    """실습 카드: 기본 → 보통 → 도전 묶음"""
    h = ""
    for lv in LEVELS:
        ps = [x for x in P if INFO[x[0]]["level"] == lv]
        if ps:
            h += (f'<h3 class="hub-lv {LVCLS[lv]}">{lv}</h3><div class="hub-grid">'
                  + "".join(card(f"p{no}.html", f"실습 {no}", re.sub("<br />", " ", t), l, extra=badges(no)) for no, _, t, _, l, _ in ps)
                  + '</div>')
    return h


home_body = (hero
             + '<section class="hub"><h2 class="hub-h"><span>1</span>에이전트 AI란?</h2><div class="hub-grid">'
             + card("concept.html", "개념", "챗봇이 아니라 일을 맡는 AI", "로컬이라 좋은 점 · 에이전트 AI라서 · 빠른 AI가 좋은 AI일까요?")
             + '</div></section>'
             + '<section class="hub"><h2 class="hub-h"><span>2</span>시작 준비</h2><div class="hub-grid">'
             + card("start.html", "준비", "설치 · 가입 · 폴더 초대", "여섯 단계 · 지시사항 · 안전장치 · 업무 지침")
             + f'<a class="hub-card" href="{ZIP_HREF}" download><span class="hub-tag">실습 자료</span><b>inlineAI_실습.zip ↓</b><span class="hub-sub">{ZIP_SIZE} · 바탕화면에 압축 풀기</span></a>'
             + card("https://portal.inline-ai.com/invitation-promotion?code=K2YERY3H", "초대 이벤트", "무료 1,000 크레딧", "초대 코드 K2YERY3H", True)
             + '</div></section>'
             + '<section class="hub"><h2 class="hub-h"><span>3</span>영역별 실습</h2><p class="hub-lead">영역마다 단계별 가이드 · 사진 · 프롬프트만 있어요. 프롬프트는 평소 말하듯 쓴 그대로예요. 기본 → 보통 → 도전 순서예요.</p>'
             + level_grids()
             + '</section>'
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
print("미리보기 없음(건너뜀):", ", ".join(sorted(set(MISSING))) or "없음")
