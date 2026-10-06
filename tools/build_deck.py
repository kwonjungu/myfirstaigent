# -*- coding: utf-8 -*-
"""강의안(lecture.html) 만들기 — 사이트와 같은 구성(개념 · 준비 · 실습 01~09 · 클로드 · 정리)
   - 엔진: 기존 lecture.css / lecture.js / gate.html(번호 1111) 재사용
   - 실습 장: 프롬프트는 실습 폴더의 프롬프트.txt 원문, 사진은 사이트와 같은 미리보기
   사용: python build_deck.py <기존 저장소> <실습 폴더> <사이트 폴더(출력)>"""
import os, re, sys, html, json
import qrcode, subprocess, pathlib
from urllib.parse import quote
from pypdf import PdfReader, PdfWriter
sys.stdout.reconfigure(encoding="utf-8")

OLD, MAT, OUT = sys.argv[1:4]
LEC = os.path.join(OLD, "tools", "lecture")
HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape
SITE = "https://joo.is/" + quote("오현에이전트")  # QR용(어느 카메라든 열리게 퍼센트 인코딩)
SHORT = "joo.is/오현에이전트"  # 화면에 보이는 주소

# 사이트 빌드 스크립트의 실습 데이터(P) 그대로 가져오기
_src = open(os.path.join(HERE, "build_new.py"), encoding="utf-8").read()
_p = _src[_src.index("NEW = "):_src.index("TILES = [")]
_ns = {}
exec(_p, _ns)
P = _ns["P"]


def read(p):
    return open(p, encoding="utf-8-sig").read().strip()


def prompts(folder):
    d = os.path.join(MAT, folder)
    if os.path.exists(os.path.join(d, "프롬프트.txt")):
        items = re.split(r"(?m)^\s*\d+\.\s*", read(os.path.join(d, "프롬프트.txt")))
        return [re.sub(r"\n{3,}", "\n\n", x).strip() for x in items if x.strip()]
    return [re.sub(r"^\[[^\]]*\]\s*", "", read(os.path.join(d, "시작_프롬프트.txt"))).strip()]


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


# ------------------------------------------------------------------ 조각
PINK, TEAL, RED, INK = "#ED1AA0", "#0A7281", "#D30005", "#111111"
SL = []  # (sec, title, acc, dark, body, notes, secs)


def add(sec, title, body, notes, secs, acc=PINK, dark=False):
    SL.append((sec, title, acc, dark, body, notes, secs))


def br(*lines):
    return "<br>".join(E(x) for x in lines)


def cover(chip, l1, l2, sub):
    return (f'<div class="pad cover-pad"><span class="chip-k">{E(chip)}</span>'
            f'<h1 class="d-xxl">{br(l1, l2)}</h1><p class="cover-sub">{E(sub)}</p><p class="cover-url">{E(SHORT)}</p>'
            '<div class="cover-dots" aria-hidden="true"><i></i><i></i><i></i></div></div>')


def section(num, title, lead, acc):
    return (f'<div class="ghost">{E(num)}</div><div class="pad"><span class="kick" style="color:{acc}">SECTION {E(num)}</span>'
            f'<h2 class="d-lg">{title}</h2><p class="lead-dk">{lead}</p></div>')


def sentence(lines, sub, acc, size="d-lg"):
    return (f'<div class="pad center-v"><span class="rule" style="background:{acc}"></span>'
            f'<h1 class="{size}">{br(*lines)}</h1>' + (f'<p class="sub">{sub}</p>' if sub else "") + "</div>")


def cards(title, items, acc, cap=""):
    cells = "".join(f'<div class="card"><span class="lab" style="background:{acc}">{E(a)}</span><p>{b}</p></div>' for a, b in items)
    return (f'<div class="pad vc"><span class="rule sm" style="background:{acc}"></span><h2 class="d-md">{E(title)}</h2>'
            f'<div class="grid{len(items)}">{cells}</div>' + (f'<p class="cap">{cap}</p>' if cap else "") + "</div>")


def steps(title, items, acc, cap=""):
    cells = "".join(f'<div class="scell" style="border-color:{acc}"><span class="sno" style="background:{acc}">{i+1}</span><h3>{E(a)}</h3><p>{b}</p></div>'
                    for i, (a, b) in enumerate(items))
    return (f'<div class="pad vc"><span class="rule sm" style="background:{acc}"></span><h2 class="d-md">{E(title)}</h2>'
            f'<div class="steps">{cells}</div>' + (f'<p class="cap mt">{cap}</p>' if cap else "") + "</div>")


def shot(title, src, acc, sub=""):
    return (f'<div class="pad tight"><div class="hd"><span class="tick" style="background:{acc}"></span><h2 class="d-sm">{E(title)}'
            + (f' <span class="hl2">{E(sub)}</span>' if sub else "") + '</h2></div>'
            f'<div class="figwrap grow"><div class="panel"><img src="{src}" alt="{E(title)} 화면" style="max-width:1120px;max-height:520px"></div></div></div>')


LABEL = re.compile(r"(?m)^(할 일|조건|끝나면|메모):")


def pbox(text, fs):
    memo = ""
    if "\n메모:" in text:  # 메모가 붙은 프롬프트: 지시 세 줄은 크게, 메모는 안쪽 칸에 작게
        text, memo = text.split("\n메모:", 1)
        fs = min(fsize(text, 700), 21 if len(memo) > 260 else 23)
        mfs = 15 if len(memo) < 260 else 12.5
        memo = f'<div class="km" style="font-size:{mfs}px"><b class="kl">메모</b><br>{E(memo.strip()).replace(chr(10), "<br>")}</div>'
    t = LABEL.sub(lambda m: f'<b class="kl">{m.group(1)}:</b>', E(text)).replace("\n", "<br>")
    return f'<div class="kp" style="font-size:{fs}px">{t}{memo}</div>'


def fsize(text, w):
    n = len(text) + text.count("\n") * 30
    for fs in (30, 27, 24, 21, 19, 17, 15, 14, 13):
        if n * fs * fs / (w * 430) < 0.62:
            return fs
    return 12


def practice(no, j, gt, gd, keys, pr, acc):
    imgs = [f"assets/practice/{k}.png" for k in keys][:2]
    right = ""
    if imgs:
        right = '<div class="kr">' + "".join(f'<div class="panel"><img src="{s}" alt="실습 파일 미리보기"></div>' for s in imgs) + "</div>"
    w = 700 if imgs else 1120
    return (f'<div class="pad kx{" one" if not imgs else ""}"><div class="kl-col">'
            f'<span class="tag" style="background:{acc}">실습 {no} · {j}</span>'
            f'<h2 class="kt">{E(gt)}</h2><p class="kg">{gd}</p>{pbox(pr, fsize(pr, w))}</div>{right}</div>')


def video(vid, title, cap, acc, short=True):
    w, h = (300, 533) if short else (760, 428)
    v = (f'<div class="vid" style="width:{w}px;height:{h}px;background-image:url(https://i.ytimg.com/vi/{vid}/hqdefault.jpg)" '
         f'data-embed="https://www.youtube.com/embed/{vid}?autoplay=1" role="button" tabindex="0" aria-label="영상 재생: {E(title)}">'
         '<span class="play" aria-hidden="true"><svg viewBox="0 0 68 48" width="76" height="54"><path d="M66.5 7.7A8.5 8.5 0 0 0 60.5 1.7C55.2.3 34 .3 34 .3S12.8.3 7.5 1.7A8.5 8.5 0 0 0 1.5 7.7 89 89 0 0 0 .1 24a89 89 0 0 0 1.4 16.3 8.5 8.5 0 0 0 6 6C12.8 47.7 34 47.7 34 47.7s21.2 0 26.5-1.4a8.5 8.5 0 0 0 6-6A89 89 0 0 0 67.9 24a89 89 0 0 0-1.4-16.3z" fill="#111"/><path d="M27 34l18-10-18-10z" fill="#fff"/></svg></span>'
         f'<a class="vlink" href="https://www.youtube.com/{"shorts/" if short else "watch?v="}{vid}" target="_blank" rel="noopener">▶ {E(title)}</a></div>')
    return (f'<div class="pad kv"><div class="kl-col"><span class="rule sm" style="background:{acc}"></span>'
            f'<h2 class="d-md">{E(title)}</h2><p class="kg big">{cap}</p></div>{v}</div>')


def qr_svg(text, size=280):
    q = qrcode.QRCode(border=2)
    q.add_data(text)
    q.make()
    m = q.get_matrix()
    n = len(m)
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return (f'<svg class="qr" viewBox="0 0 {n} {n}" width="{size}" height="{size}" role="img" aria-label="QR: {E(text)}" shape-rendering="crispEdges">'
            f'<rect width="{n}" height="{n}" fill="#fff"/><g fill="#111">{rects}</g></svg>')


def qr_slide(title, lines, acc):
    return (f'<div class="pad kv"><div class="kl-col"><span class="rule sm" style="background:{acc}"></span><h2 class="d-md">{E(title)}</h2>'
            + "".join(f'<p class="kg big">{x}</p>' for x in lines)
            + f'<p class="kurl">{E(SHORT)}</p></div><div class="kq">{qr_svg(SITE)}</div></div>')


# ================================================================== 여는 말 · 1 개념
S1 = "1 개념"
add(S1, "표지", cover("교원 연수 · 학교 현장 에이전트 AI", "내 업무 파일,", "AI에게 맡겨 보기", "일단 던지고, 내 컴퓨터에 초대하고, 정해진 양식을 주세요."),
    "안녕하세요. 오늘은 AI에게 '묻는 법'이 아니라 내 업무 파일을 '맡기는 법'을 해 봅니다. 끝날 때쯤엔 가정통신문, 기안문, 품의, 퀴즈까지 직접 맡겨 본 상태가 돼요.", 30, dark=True)
add(S1, "답하는 AI가 아니라 일을 맡는 AI", sentence(["묻는 말에 답하는 AI가 아니라", "일을 맡는 AI"], "이걸 <b>에이전트 AI</b>라고 불러요", PINK),
    "챗GPT처럼 묻고 답하는 AI는 답을 복사해 붙이는 일이 제 몫이었죠. 에이전트 AI는 파일을 직접 열고, 고치고, 저장까지 해요. 오늘 쓰는 inline AI가 그런 AI예요.", 60)
add(S1, "로컬이라 좋은 점", cards("내 컴퓨터에 깔려서 좋은 점", [("용량", "<b>큰 파일도 OK</b><br>채팅창 올리기 제한에 덜 걸려요"),
    ("여러 파일", "계획서·예산표·통신문을<br><b>한 번에</b> 읽고 맞춰 봐요"), ("일괄", "폴더 하나를 맡겨<br><b>50개도 한꺼번에</b>")], PINK,
    "그래도 학생 실명·연락처가 든 진짜 파일은 쓰지 마세요"),
    "웹 채팅은 파일을 하나씩 올려야 하죠. inline AI는 내 컴퓨터에 깔려서 폴더째 맡길 수 있어요. 단, 오늘은 실습용 가상 자료만 써요. 실제 학생 정보가 든 파일은 넣지 않는 게 원칙입니다.", 75)
add(S1, "에이전트 AI라서", cards("에이전트 AI라서 달라지는 것", [("알아서", "시켜 두면 <b>열고 고치고 저장</b><br>그동안 다른 일을 해요"),
    ("누적", "결과가 폴더에 <b>쌓여서</b><br>다음 달엔 그 위에 이어 가요"), ("맥락", "학교 양식·작년 문서가<br>AI의 <b>맥락</b>이 돼요")], PINK),
    "가장 큰 차이는 '맡기고 자리를 비울 수 있다'는 거예요. 그리고 폴더에 우리 학교 양식과 작년 문서가 쌓일수록 AI가 우리 학교 방식대로 일해요.", 75)
add(S1, "빠른 AI가 좋은 AI일까요?", video("ffSpxalmi9E", "빠른 AI가 좋은 AI일까요?",
    "사람처럼 화면을 보고 마우스를 움직이는 AI예요.<br>빠르진 않죠? 대신 처음부터 끝까지 <b>스스로</b> 해요.", PINK),
    "영상을 잠깐 보죠(30초). 느려 보이지만 사람 손을 전혀 안 빌리고 끝까지 갑니다. 이게 에이전트의 본질이에요.", 60)
add(S1, "오래 걸려도 검토할 게 적은 AI", sentence(["오래 걸려도", "검토할 게 적은 AI"], "기다리지 말고, 시켜 두고 다른 일을 하세요", PINK),
    "요즘 AI는 빨리 대충 하는 쪽보다 오래 걸려도 검토할 게 적은 쪽으로 가요. 오늘 실습에서도 AI가 일하는 동안 화면을 지켜보지 말고 다음 파일을 준비해 보세요.", 45)
add(S1, "오늘의 세 가지", steps("오늘 기억할 세 가지", [("일단 던지기", "잘 쓴 프롬프트보다<br>한 줄 먼저"), ("내 컴퓨터에 초대", "복사·붙여넣기 말고<br>폴더째 맡기기"),
    ("정해진 양식 주기", "'알아서 예쁘게'보다<br>'우리 학교 양식 그대로'")], PINK, "긴 설명보다 자료 하나가 더 강력해요"),
    "오늘 하루 이 세 가지만 기억하시면 됩니다. 특히 세 번째, 양식을 주면 AI 결과가 훨씬 정확해져요.", 60)

# ================================================================== 2 준비
S2 = "2 준비"
add(S2, "시작 준비", section("00", "시작 준비<br>AI를 내 컴퓨터에", "실습 자료 받기 · 설치 · 폴더 초대 · 지시사항", TEAL),
    "이제 준비를 해요. 15분이면 충분합니다. 막히는 분은 손 들어 주세요.", 15, TEAL, True)
add(S2, "사이트 열기", qr_slide("사이트 하나면 돼요", ["실습 자료 zip · 설치 안내 · 프롬프트 [복사]", "모든 실습이 이 사이트에 있어요"], TEAL),
    "QR을 찍거나 주소를 쳐서 사이트를 여세요. 맨 위 '실습 자료 zip'을 받아 바탕화면에 압축을 풀면 inlineAI_실습 폴더가 생겨요. 프롬프트는 전부 사이트에서 [복사]로 씁니다.", 120)
add(S2, "설치 · 로그인 · 초대 코드", steps("세 단계로 설치", [("설치", "inline-ai.com → 개인용<br>→ Windows용 다운로드"), ("로그인", "계정 만들고 로그인<br>입력창이 보이면 성공"),
    ("초대 코드", "<b>K2YERY3H</b><br>무료 1,000 크레딧")], TEAL, "막히면: 오른쪽 클릭 → 관리자 권한으로 실행 · 파란 창은 추가 정보 → 실행"),
    "설치 파일이 막히면 관리자 권한으로 실행, 파란 SmartScreen 창은 '추가 정보 → 실행'을 누르세요. 초대 코드를 넣으면 무료 크레딧 1,000이 더 들어와요.", 240)
add(S2, "설치 화면", shot("inline-ai.com → 개인용 → Windows용 다운로드", "assets/shot/inline/01_install_site_personal_1280.png", TEAL),
    "사이트 위쪽 '개인용'을 먼저 누르고 Windows용 다운로드예요. 기관용과 헷갈리지 않게 해 주세요.", 30)
add(S2, "폴더는 하나만 초대", shot("폴더는 하나만 초대", "assets/files/shot_07_work_panel_1280.png", TEAL, "작업 패널 → 접근 가능한 폴더 → inlineAI_실습"),
    "오른쪽 위 네모 아이콘이 작업 패널이에요. 접근 가능한 폴더에 바탕화면의 inlineAI_실습 하나만 추가하세요. 바탕화면 전체나 다운로드 폴더는 절대 넣지 않아요. 이게 첫 번째 안전장치예요.", 120)
SHORT = read(os.path.join(MAT, "00_업무지침", "01_기본지침_짧은판.txt"))
add(S2, "지시사항 붙이기", (f'<div class="pad kx"><div class="kl-col"><span class="tag" style="background:{TEAL}">지시사항 · 한 번만</span>'
    f'<h2 class="kt">모든 대화에 같은 규칙</h2><p class="kg">설정 → 일반 설정 → inline AI 지시사항에 <b>Ctrl+V</b></p>{pbox(SHORT, 15)}</div>'
    '<div class="kr"><div class="panel"><img src="assets/files/shot_11_settings_general_1280.png" alt="지시사항 설정 화면"></div></div></div>'),
    "사이트 '시작 준비'의 짧은판을 복사해서 설정 → 일반 설정 → 지시사항에 붙여 넣어요. 목록 먼저 보여 주기, 원본은 새 이름으로, 모르는 건 [확인 필요]. 이 세 가지가 매 대화에 자동으로 들어가요.", 120)
add(S2, "안전장치 세 가지", cards("안전장치 세 가지", [("폴더 하나만", "AI가 보는 폴더는<br><b>inlineAI_실습 하나</b>"), ("원본은 새 이름", "고친 파일은<br><b>새 이름으로 저장</b>"),
    ("목록 먼저", "'고치기 전에<br><b>목록으로 먼저</b> 보여 줘'")], TEAL, "실습이 바뀌면 새 에이전트 · 한글 파일은 하나만 열기 · 엑셀은 MS 엑셀"),
    "승인 모드는 '모든 편집 허용'으로 두고, 대신 이 세 가지로 지켜요. 실습이 바뀔 때마다 왼쪽 위 '새 에이전트'로 새 대화를 여는 것도 꼭 지켜 주세요.", 60)
add(S2, "프롬프트는 세 줄", steps("프롬프트는 세 줄이면 돼요", [("할 일", "무엇을 할지<br>한 문장으로"), ("조건", "어떻게, 무엇을 지킬지<br>모르면 '내게 물어봐'"),
    ("끝나면", "어디에 저장하고<br>무엇을 알려 줄지")], TEAL, "오늘 모든 실습 프롬프트가 이 형식이에요"),
    "오늘 프롬프트는 전부 '할 일 · 조건 · 끝나면' 세 줄이에요. 특히 조건에 '모르는 건 내게 물어봐'를 넣으면 AI가 지어내지 않고 먼저 물어봐요. 끝나면에는 저장 이름과 확인할 것을 적어요.", 75)

# ================================================================== 3 실습 01~09
ACC = [PINK, RED, TEAL, PINK, RED, TEAL, PINK, RED, TEAL]
CHECK = {
    ("01", 1): "사진 폴더가 생겼는지, 0바이트 '흉내' 파일은 빠졌는지 확인해요.",
    ("01", 2): "AI가 사진을 직접 보고 꿀벌만 골랐는지 — 고른 파일 이름을 같이 봐요.",
    ("01", 3): "지우기 전에 목록을 먼저 받는 습관. '좋아, 진행해'라고 답하면 실행돼요.",
    ("02", 1): "머리 표가 그대로인지, 날짜 요일(6. 15.(월)~6. 19.(금), 6. 22.(월))이 맞는지 봐요.",
    ("02", 2): "AI가 신청 마감일 같은 걸 먼저 물어요. 묻는 말에 답하는 경험이 핵심이에요.",
    ("02", 3): "2027. 1. 15.~1. 25.는 11일간. 일수를 다시 계산했는지 확인해요.",
    ("02", 4): "다른 학교 양식으로 옮겨도 내용은 그대로. 오현초 흔적이 남았는지 마지막 보고를 봐요.",
    ("03", 1): "표 모양 안 2가지를 비교해 고르는 게 포인트. AI와 의논하는 연습이에요.",
    ("03", 2): "4반은 26명이에요. 한 줄 8명이면 4줄이 나와야 해요.",
    ("03", 3): "이름표 26장 — 장 수와 학생 수가 같은지 AI가 스스로 확인해요.",
    ("03", 4): "우유급식 미신청은 9명이에요.",
    ("04", 1): "2026. 11. 11.은 수요일. 바꾼 곳 목록으로 빠진 곳을 점검해요.",
    ("04", 2): "열린 양식의 개조식 말투를 따라 했는지 봐요.",
    ("04", 3): "두 계획서를 같이 읽고 쓰는 실습. 어떤 내용을 어디서 가져왔는지 보고를 봐요.",
    ("05", 1): "견적서 합계와 업로드 양식 합계가 맞는지 — AI가 스스로 대조해요.",
    ("06", 1): "결과물이 두 개(계획서·협조 공문). 공문은 00_업무지침의 작성 규칙을 따랐는지 봐요.",
    ("06", 2): "이미지 추출 → 웹 검색 → 배정 → 예산까지 여러 단계를 혼자 해요.",
    ("07", 1): "시작 전에 묻는 질문에 답해요. 숫자는 엑셀에 있는 것만 썼는지 봐요.",
    ("08", 1): "학교 양식 그대로 PPT가 나와요.",
    ("08", 2): "같은 내용, 다른 옷. 디자인 가이드를 주면 스타일이 바뀌어요.",
    ("09", 1): "정답 번호가 1~4번에 고르게 나뉘었는지, 템플릿 3행부터 채웠는지 봐요.",
}
for k, (no, folder, title, nav, lead, stps) in enumerate(P):
    acc = ACC[k]
    sec = f"{k + 3} {nav}"
    ps = prompts(folder)
    add(sec, strip_tags(title.replace("<br />", " ")), section(no, title.replace("<br />", "<br>"), lead + f"<br><span class='kf'>inlineAI_실습 / {E(folder)}</span>", acc),
        f"실습 {no}. {strip_tags(lead)} 새 에이전트로 시작하세요.", 20, acc, True)
    for j, ((gt, gd, keys), pr) in enumerate(zip(stps, ps), 1):
        add(sec, f"{no}-{j} {gt}", practice(no, j, gt, gd, keys, pr, acc),
            f"{strip_tags(gd)} 사이트 실습 {no} 페이지에서 프롬프트를 [복사]해 붙여 넣어요. 확인: {CHECK.get((no, j), '')}",
            240 if no in ("02", "04", "06") else 180, acc)

# ================================================================== 4 클로드
S4 = "12 클로드"
add(S4, "클로드 코워크로 한 걸음 더", section("C", "클로드 코워크로<br>한 걸음 더", "오늘 익힌 습관이 그대로 통해요. 스킬·예약까지 더한 상위 호환이에요.", PINK),
    "마지막으로 같은 일을 클로드 코워크로 하는 법을 짧게 보여 드릴게요.", 20, PINK, True)
add(S4, "같은 습관, 더 많은 기능", cards("같은 습관, 더 많은 기능", [("프로젝트", "학교 일 묶음별로<br><b>자료·지침을 고정</b>"), ("스킬", "00_업무지침을<br><b>스킬로 올려</b> 늘 적용"),
    ("예약", "'매주 월요일 아침'처럼<br><b>정해진 때 알아서</b>")], PINK, "일단 던지기 · 내 컴퓨터에 초대 · 양식 주기는 똑같아요"),
    "클로드 데스크톱 앱의 코워크도 내 폴더를 맡기는 방식은 같아요. 여기에 프로젝트, 스킬, 예약이 더해져요.", 90)
add(S4, "폴더 맡기기", shot("코워크도 폴더를 맡겨요", "assets/shot/claude/11_folder_pick_1280.png", PINK),
    "코워크에서 작업 폴더를 고르는 화면이에요. inline AI의 '접근 가능한 폴더'와 같은 개념이에요.", 45)
add(S4, "업무 지침을 스킬로", shot("업무 지침을 스킬로 올리기", "assets/shot/claude/24_skill_add_1280.png", PINK, "사이트의 스킬 zip 그대로"),
    "사이트 클로드 페이지에서 스킬 zip을 받아 '스킬 추가'로 올리면, 공문서 규칙이 모든 대화에 자동으로 적용돼요.", 60)
add(S4, "예약", shot("예약 — 정해진 때 알아서", "assets/shot/claude/22_scheduled_1280.png", PINK),
    "'매주 월요일 아침 다운로드 폴더 정리'처럼 예약해 두면 정해진 때 알아서 해요. 예시 카드는 누르면 바로 만들어지니 구경만 하세요.", 60)
add(S4, "교사를 위한 클로드", video("HmBVZ_679Ko", "교사를 위한 클로드", "전정선 선생님 강의 다시보기<br>코워크 소개는 <b>약 37:40</b>부터", PINK, short=False),
    "더 보고 싶은 분은 이 영상을 추천해요. 사이트 클로드 페이지에 링크가 있어요.", 30)

# ================================================================== 정리
S5 = "13 정리"
add(S5, "정리", section("✓", "정리 ·<br>내일부터 이렇게", "아침에 시켜 두고, 수업 다녀와서 확인해요.", INK),
    "정리하겠습니다.", 15, INK, True)
add(S5, "확인하고 다듬는 사람", sentence(["내가 다 쓰는 게 아니라", "확인하고 다듬는 사람"], "AI가 초안을 쓰고, 나는 결재하듯 봐요", PINK),
    "오늘 해 보신 것처럼, 이제 초안은 AI가 쓰고 선생님은 확인하고 다듬는 역할이에요.", 45)
add(S5, "내일부터 아침 루틴", steps("내일부터 아침 루틴", [("출근 10분", "오늘 할 문서를<br>에이전트에 맡기기"), ("수업", "AI는 일하고<br>나는 수업"),
    ("쉬는 시간", "결과 확인·다듬기<br>새 이름 파일만 보면 돼요")], PINK),
    "아침에 맡기고, 수업 다녀와서 확인하세요. 기다리는 시간이 없어져요.", 45)
add(S5, "여러 AI에게 동시에", cards("여러 AI에게 동시에", [("에이전트 1", "가정통신문"), ("에이전트 2", "기안문"), ("에이전트 3", "품의"), ("에이전트 4", "수업 퀴즈")], PINK,
    "주의: 한글 문서는 에이전트마다 다른 파일로 · 크레딧은 맡긴 만큼 쓰여요"),
    "새 에이전트를 여러 개 열어 동시에 맡겨도 돼요. 단, 같은 한글 파일을 두 에이전트가 동시에 고치면 엉켜요.", 45)
add(S5, "다시 보기", qr_slide("오늘 가져가는 것", ["실습 자료 · 프롬프트 · 업무 지침", "<b>내일 아침 하나만 맡겨 보세요</b>"], PINK),
    "사이트는 계속 열려 있어요. 내일 아침 딱 하나만 맡겨 보세요. 감사합니다.", 30)

# ------------------------------------------------------------------ 조립
CSS = open(os.path.join(LEC, "lecture.css"), encoding="utf-8").read()
JS = open(os.path.join(LEC, "lecture.js"), encoding="utf-8").read()
# 외국어 전환 빼기: 번역 블록을 '그대로 돌려주는 tr'로 바꾸고, 저장된 언어 복원도 지움
_a = JS.index("  /* 화면 언어")
_b = JS.index("  /* 목차 */")
JS = JS[:_a] + "  function tr(k){ return k; }\n\n" + JS[_b:]
JS = re.sub(r"\n\s*var saved = qs\.get\('lang'\);.*?\n.*?setLang\(saved\);", "", JS)
assert "setLang" not in JS and "i18n" not in JS
JS = JS.replace("' · 원고 ' + f.dataset.src.replace(/,/g, ', ') + ", "")
PDF_HREF = "download/" + quote("강의안.pdf")
GATE = open(os.path.join(LEC, "gate.html"), encoding="utf-8").read()
EXTRA = """
.cover-sub{margin-top:28px;font-size:26px;color:rgba(255,255,255,.72)}
.cover-url{margin-top:18px;font-size:30px;font-weight:800;color:#fff;letter-spacing:.01em}
.kurl{font-size:34px!important}
.kf{display:inline-block;margin-top:14px;font-size:20px;color:rgba(255,255,255,.55)}
.kx{flex-direction:row;align-items:center;gap:36px;padding:52px 60px 66px}
.kx .kl-col{flex:1 1 0;min-width:0;display:flex;flex-direction:column}
.kx .tag{align-self:flex-start;color:#fff;font-weight:800;font-size:17px;border-radius:999px;padding:5px 16px}
.kt{font-family:var(--fd);font-weight:400;font-size:44px;line-height:1.15;margin:14px 0 8px}
.kg{font-size:20px;color:#39393b;line-height:1.5;margin:0 0 16px}.kg.big{font-size:26px;margin-top:10px}
.kp{background:#ececec;border-radius:18px;padding:20px 24px;line-height:1.55;font-weight:600;color:#111;max-height:470px;overflow:hidden;word-break:keep-all}
.kl{color:#0A7281;font-weight:800}
.km{margin-top:12px;background:#fff;border-radius:12px;padding:12px 16px;font-weight:500;line-height:1.5;color:#39393b}
.ui .home{color:#fff;font-weight:700;font-size:14px;padding:0 12px;text-decoration:none;opacity:.85}.ui .home:hover{opacity:1}
.kr{flex:0 0 440px;display:flex;flex-direction:column;gap:12px;height:580px;align-self:center}
.kr .panel{flex:1 1 0;min-height:0;align-items:flex-start;padding:10px}.kr .panel img{width:100%;height:auto;max-height:none}
.kx.one .kl-col{max-width:1120px}
.kv{flex-direction:row;align-items:center;justify-content:space-between;gap:48px}
.kv .kl-col{flex:1 1 0}
.kurl{margin-top:24px;font-size:24px;font-weight:800;color:#111;letter-spacing:.01em}
.kq{background:#fff;border-radius:20px;padding:16px;box-shadow:0 0 0 1px #e5e5e5}
.vid{background-size:cover;background-position:center;border-radius:20px;position:relative;flex:0 0 auto}
"""
frames = []
for i, (sec, title, acc, dark, body, notes, secs) in enumerate(SL, 1):
    frames.append(f'<div class="frame" data-i="{i}" data-sec="{E(sec)}" data-title="{E(title)}" data-src="{i:02d}" data-secs="{secs}">'
                  f'<section class="slide{" dark" if dark else ""}" id="p{i}" style="--ac:{acc}" aria-label="{i}. {E(title)}">{body}'
                  f'<div class="pnum"><span>{E(sec)}</span><b>{i:02d}</b></div></section>'
                  f'<template class="notes"><p>{E(notes)}</p></template></div>')
doc = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<title>내 첫 에이전트 AI · 강의안</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="내 업무 파일, AI에게 맡겨 보기 — 학교 현장 에이전트 AI 교원 연수 강의안">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
<style>{CSS}{EXTRA}</style></head>
<body>
{GATE}
<div class="deckwrap">
{chr(10).join(frames)}
</div>
<div class="progress" aria-hidden="true"><i id="prog"></i></div>
<div class="ui" id="ui">
  <a class="home" href="index.html" title="사이트 홈">홈</a>
  <button id="prev" aria-label="이전 장">‹</button><span class="cnt" id="cnt"></span><button id="next" aria-label="다음 장">›</button>
  <button id="btnToc" title="목차 (T)">목차</button><button id="btnNotes" title="발표자 노트 (N)">노트</button><button id="mode" title="목록/발표 (F)">목록 보기</button><button id="btnFs" title="전체화면 (Z)">전체화면</button>
  <a class="home pdf" href="{PDF_HREF}" download title="강의안 PDF 내려받기 (열기 암호는 연수 번호)">PDF ↓</a>
</div>
<aside class="notes-panel" id="notes" aria-label="발표자 노트"><div class="np-hd"><b>발표자 노트</b><span id="npMeta"></span><button id="npX" aria-label="노트 닫기">✕</button></div><div class="np-body" id="npBody"></div></aside>
<div class="toc" id="toc" role="dialog" aria-label="목차"><div class="toc-box"><div class="toc-hd"><b>목차</b><span>누르면 그 장으로 가요 · T 또는 Esc로 닫기</span></div><div class="toc-list" id="tocList"></div></div></div>
<div class="keys" id="keys">← → 넘기기 · Z 전체화면 · N 노트 · T 목차 · F 목록/발표 · P 인쇄 보기</div>
<script>{JS}</script>
<script>
(function(){{
  var b = document.getElementById('btnFs'), de = document.documentElement;
  function on(){{ return document.fullscreenElement || document.webkitFullscreenElement; }}
  function toggle(){{
    if (on()) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    else (de.requestFullscreen || de.webkitRequestFullscreen).call(de);
  }}
  function sync(){{ b.textContent = on() ? '전체화면 끄기' : '전체화면'; }}
  b.onclick = toggle;
  document.addEventListener('fullscreenchange', sync); document.addEventListener('webkitfullscreenchange', sync);
  addEventListener('keydown', function(e){{
    if (window.__deckLocked || e.target.tagName === 'INPUT') return;
    if (e.key === 'z' || e.key === 'Z' || e.key === 'ㅋ') toggle();
  }});
}})();
</script>
</body></html>'''
open(os.path.join(OUT, "lecture.html"), "w", encoding="utf-8").write(doc)
tot = sum(s[6] for s in SL)
print(f"강의안 {len(SL)}장 · 예상 {tot // 60}분")
for i, s in enumerate(SL, 1):
    for m in re.findall(r'src="(assets/[^"]+)"', s[4]):
        if not os.path.exists(os.path.join(OUT, m)):
            print("없는 그림:", i, m)

# ------------------------------------------------------------------ PDF (인쇄 모드 그대로, 열기 암호 = 연수 번호 1111)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
raw = os.path.join(HERE, "lecture_raw.pdf")
url = pathlib.Path(os.path.abspath(os.path.join(OUT, "lecture.html"))).as_uri() + "?print=1&code=1111"
subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--user-data-dir=" + os.path.join(HERE, "edgeprof_pdf"),
                "--no-pdf-header-footer", "--virtual-time-budget=30000", "--print-to-pdf=" + raw, url], capture_output=True, timeout=300)
r = PdfReader(raw)
w = PdfWriter()
for pg in r.pages:
    w.add_page(pg)
w.add_metadata({"/Title": "내 첫 에이전트 AI · 강의안"})
w.encrypt(user_password="1111", owner_password="1111", algorithm="AES-256")
os.makedirs(os.path.join(OUT, "download"), exist_ok=True)
with open(os.path.join(OUT, "download", "강의안.pdf"), "wb") as f:
    w.write(f)
print(f"PDF {len(r.pages)}쪽 · {os.path.getsize(os.path.join(OUT, 'download', '강의안.pdf')) // 1024}KB (암호 1111)")
