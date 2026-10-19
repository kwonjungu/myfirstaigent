# -*- coding: utf-8 -*-
"""하루 한 팁 캡처 — 가상 화면을 HTML로 그려 헤드리스 Edge로 찍는다 (1280×800)
   실제 학생·학교 정보 없이 가상 이름·데이터만 쓴다. 잠금 화면·TV처럼 캡처가 안 되는 장면도 그림으로 만든다.
   결과: assets/tips/shot/NN_slug_a.png … (tips.py의 파일 이름 그대로) → 이어서 build_tips.py를 돌리면 페이지에 들어간다
   사용: python tools/tip_scenes.py [파일 이름 일부 …]   (아무것도 안 주면 전부)"""
import os, sys, subprocess, tempfile
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "tips", "shot")
EDGE = next(p for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe") if os.path.exists(p))
W, H = 1280, 800

CSS = """
*{box-sizing:border-box}
body{margin:0;width:1280px;height:800px;overflow:hidden;font-family:Pretendard,'Malgun Gothic',sans-serif;color:#111;position:relative;
     background:linear-gradient(135deg,#8fb8e6 0%,#b9c8f2 45%,#d7c4f0 100%)}
.desk{position:absolute;inset:0 0 48px 0}
.taskbar{position:absolute;left:0;right:0;bottom:0;height:48px;background:rgba(243,243,247,.92);display:flex;align-items:center;justify-content:center;gap:10px;border-top:1px solid #ddd}
.taskbar i{width:28px;height:28px;border-radius:7px;display:block}
.taskbar .clock{position:absolute;right:16px;font-size:12px;text-align:right;line-height:1.3;color:#222}
.win{position:absolute;background:#fff;border-radius:8px;box-shadow:0 12px 36px rgba(0,0,0,.28);overflow:hidden;border:1px solid #c9c9c9;display:flex;flex-direction:column}
.win.dim{filter:saturate(.6) brightness(.97)}
.tb{height:34px;flex:0 0 34px;background:#f3f3f3;display:flex;align-items:center;padding:0 0 0 12px;font-size:13px;gap:8px;border-bottom:1px solid #e3e3e3}
.tb b{width:16px;height:16px;border-radius:4px;display:inline-block}
.tb .ctl{margin-left:auto;display:flex}.tb .ctl span{width:44px;text-align:center;color:#444;font-size:13px}
.body{flex:1;position:relative;overflow:hidden}
.tag{position:absolute;left:24px;top:22px;background:#111;color:#fff;font-weight:800;font-size:20px;padding:10px 18px;border-radius:12px;z-index:50;box-shadow:0 6px 18px rgba(0,0,0,.25)}
.tag small{display:block;font-size:13px;font-weight:600;color:#ffb0dd;margin-bottom:2px}
.key{position:absolute;right:24px;top:22px;background:#ed1aa0;color:#fff;font-weight:800;font-size:22px;padding:10px 20px;border-radius:999px;z-index:50;box-shadow:0 6px 18px rgba(0,0,0,.25)}
.ring{position:absolute;border:4px solid #ed1aa0;border-radius:12px;z-index:40}
.hwpbar{height:62px;background:#f7f7f9;border-bottom:1px solid #ddd;display:flex;gap:8px;align-items:center;padding:0 12px}
.hwpbar span{width:34px;height:34px;border-radius:6px;background:#e4e8f0}
.paper-bg{position:absolute;inset:62px 0 0 0;background:#9a9a9a;overflow:hidden}
.paper{position:absolute;background:#fff;left:50%;transform:translateX(-50%);box-shadow:0 2px 8px rgba(0,0,0,.3);padding:46px 56px;font-size:14px;line-height:1.75}
.paper h1{font-size:22px;text-align:center;margin:0 0 18px}
.ribbon{height:58px;background:#f3f6f3;border-bottom:1px solid #d6d6d6;display:flex;align-items:center;gap:8px;padding:0 12px}
.ribbon span{width:30px;height:30px;border-radius:5px;background:#dfe9df}
.fx{height:30px;border-bottom:1px solid #d6d6d6;display:flex;align-items:center;font-size:13px;gap:10px;padding:0 10px;background:#fff}
.fx .nm{width:70px;border-right:1px solid #ddd;color:#555}
table.grid{border-collapse:collapse;font-size:14px}
table.grid td,table.grid th{border:1px solid #d9d9d9;height:30px;padding:0 10px;min-width:70px}
table.grid th{background:#f2f2f2;font-weight:500;color:#555;text-align:center}
.tabs{height:40px;background:#e8eaed;display:flex;align-items:flex-end;padding:0 8px;gap:2px}
.tabs div{height:32px;min-width:170px;max-width:220px;padding:0 12px;display:flex;align-items:center;font-size:12.5px;border-radius:8px 8px 0 0;color:#333;white-space:nowrap;overflow:hidden}
.tabs .on{background:#fff}
.addr{height:40px;background:#fff;display:flex;align-items:center;padding:0 12px;gap:10px;border-bottom:1px solid #e3e3e3}
.addr div{flex:1;height:28px;border-radius:999px;background:#f1f3f4;font-size:13px;display:flex;align-items:center;padding:0 14px;color:#444}
.slide{background:#fff;position:absolute;overflow:hidden}
.tv{position:absolute;background:#141414;border-radius:16px;padding:16px;box-shadow:0 20px 50px rgba(0,0,0,.35)}
.tv .scr{position:relative;width:100%;height:100%;overflow:hidden;border-radius:4px;background:#000}
.tv .brand{position:absolute;bottom:3px;left:0;right:0;text-align:center;font-size:9px;color:#666;letter-spacing:.2em}
.stand{position:absolute;background:#2a2a2a}
.room{position:absolute;inset:0;background:linear-gradient(#efe9dc 0 78%,#c9b48f 78% 100%)}
.cap{position:absolute;font-size:16px;font-weight:800;color:#333;text-align:center}
.mini{position:absolute;inset:0;background:linear-gradient(135deg,#8fb8e6,#d7c4f0)}
"""


def page(body, bg=None):
    style = f"<style>{CSS}{('body{background:' + bg + '}') if bg else ''}</style>"
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
            f'{style}</head><body>{body}</body></html>')


def taskbar(time="오전 9:12"):
    ic = "".join(f'<i style="background:{c}"></i>' for c in ("#2563eb", "#f59e0b", "#0ea5e9", "#16a34a", "#dc2626", "#7c3aed"))
    return f'<div class="taskbar">{ic}<div class="clock">{time}<br>2026-10-20</div></div>'


def win(x, y, w, h, title, body, color="#2563eb", cls=""):
    return (f'<div class="win {cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="tb"><b style="background:{color}"></b>{title}<div class="ctl"><span>─</span><span>☐</span><span>✕</span></div></div>'
            f'<div class="body">{body}</div></div>')


def tag(t, small="이런 때"):
    return f'<div class="tag"><small>{small}</small>{t}</div>'


def key(t):
    return f'<div class="key">{t}</div>'


def desktop(inner, time="오전 9:12"):
    return f'<div class="desk">{inner}</div>{taskbar(time)}'


# ------------------------------------------------------------------ 자주 쓰는 화면 조각
STUDENTS = ["김하늘", "이도윤", "박서아", "최지호", "정예린", "강민준", "윤채원", "임시우", "한소율", "오지안"]


def grades_win(x=140, y=70, w=1000, h=600):
    rows = "".join(f"<tr><td>{i+1}</td><td>{n}</td><td>{80+(i*7)%19}</td><td>{75+(i*5)%23}</td><td>{'상담 예정' if i in (2, 6) else ''}</td></tr>"
                   for i, n in enumerate(STUDENTS))
    body = (f'<div style="background:#1f3b73;color:#fff;padding:12px 18px;font-weight:700">교무 업무 시스템 (가상) · 성적 · 상담 기록</div>'
            f'<div style="padding:18px"><table class="grid" style="width:100%"><tr><th>번호</th><th>이름</th><th>국어</th><th>수학</th><th>상담</th></tr>{rows}</table></div>')
    return win(x, y, w, h, "교무 업무 시스템 (가상) - Microsoft Edge", body, "#1f3b73")


def messenger_win(x, y, w=380, h=430):
    msgs = [("교무부", "오늘 협의회 15:00 → 3층 회의실로 변경"), ("학부모(가상)", "선생님, 지호 상담 일정 문의드립니다"),
            ("교감", "생활기록부 점검 금요일까지 부탁드려요"), ("3학년 협의", "현장체험학습 동의서 회수 현황 공유")]
    li = "".join(f'<div style="padding:10px 14px;border-bottom:1px solid #eee"><b style="font-size:13px">{a}</b><div style="font-size:13px;color:#555">{b}</div></div>' for a, b in msgs)
    return win(x, y, w, h, "업무 메신저 (가상)", f'<div style="background:#fef3c7;padding:8px 14px;font-size:12px;font-weight:700">새 쪽지 4</div>{li}', "#f59e0b")


def lesson_slide(title="식물의 한살이", sub="씨가 싹 트는 데 필요한 조건은?", n=None):
    plant = ('<svg width="210" height="154" viewBox="0 0 300 220" style="flex:0 0 auto"><rect x="20" y="170" width="260" height="40" rx="6" fill="#a16207"/>'
             '<path d="M150 170 C150 120 150 100 150 70" stroke="#15803d" stroke-width="8" fill="none"/>'
             '<ellipse cx="118" cy="92" rx="34" ry="16" fill="#22c55e" transform="rotate(-25 118 92)"/>'
             '<ellipse cx="182" cy="80" rx="34" ry="16" fill="#22c55e" transform="rotate(25 182 80)"/><circle cx="150" cy="185" r="12" fill="#78350f"/></svg>')
    num = f'<div style="position:absolute;right:28px;bottom:18px;font-size:20px;color:#888">{n}</div>' if n else ""
    return (f'<div style="position:absolute;inset:0;background:#fff;display:flex;align-items:center;gap:24px;padding:0 50px">'
            f'<div style="flex:1"><div style="font-size:22px;color:#16a34a;font-weight:800">과학 4학년 (가상 수업)</div>'
            f'<div style="font-size:44px;font-weight:900;margin:8px 0 14px;white-space:nowrap">{title}</div><div style="font-size:22px;color:#444">{sub}</div></div>{plant}{num}</div>')


def classroom_tv(screen_html, caption=""):
    cap = f'<div class="cap" style="left:0;right:0;top:700px">{caption}</div>' if caption else ""
    return (f'<div class="room"></div><div class="stand" style="left:620px;top:600px;width:40px;height:70px"></div>'
            f'<div class="stand" style="left:540px;top:665px;width:200px;height:14px;border-radius:7px"></div>'
            f'<div class="tv" style="left:250px;top:90px;width:780px;height:470px"><div class="scr">{screen_html}</div><div class="brand">CLASSROOM TV</div></div>{cap}')


def hwp_win(x, y, w, h, title, paper_html, pw=560, ph=760, top=24, cls=""):
    body = (f'<div class="hwpbar">{"<span></span>" * 14}</div><div class="paper-bg">'
            f'<div class="paper" style="width:{pw}px;height:{ph}px;top:{top}px">{paper_html}</div></div>')
    return win(x, y, w, h, title, body, "#0b6bcb", cls)


NOTICE = ('<h1>현장체험학습 안내</h1><p>학부모님, 안녕하십니까? 가을을 맞아 3학년 학생들이 아래와 같이 현장체험학습을 다녀오고자 합니다.</p>'
          '<p>1. 일시: 2026. 10. 28.(수) 09:00~15:00<br>2. 장소: 가상 자연생태공원<br>3. 준비물: 도시락, 물, 돗자리, 필기도구<br>'
          '4. 복장: 활동하기 편한 옷과 운동화</p><p>안전한 체험을 위해 출발 전 안전교육을 실시하며, 인솔 교사가 학생들과 함께합니다. '
          '참가 동의서는 10. 23.(금)까지 담임 선생님께 제출해 주시기 바랍니다.</p>')


def excel_win(x, y, w, h, rows, sel=None, fx="", title="3학년 2반 점수표.xlsx - Excel"):
    head = "<tr><th></th>" + "".join(f"<th>{c}</th>" for c in "ABCDEF") + "</tr>"
    tr = ""
    for r, row in enumerate(rows, 1):
        tds = ""
        for c, v in enumerate(row):
            st = ' style="outline:3px solid #107c41;outline-offset:-2px;background:#e8f5e9"' if sel == (r, c) else ""
            al = ' style="text-align:right"' if isinstance(v, (int, float)) and not st else st
            tds += f"<td{al}>{v}</td>"
        tr += f"<tr><th>{r}</th>{tds}</tr>"
    body = (f'<div class="ribbon">{"<span></span>" * 16}</div><div class="fx"><span class="nm">{"ABCDEF"[sel[1]] + str(sel[0]) if sel else ""}</span>{fx}</div>'
            f'<div style="padding:0"><table class="grid">{head}{tr}</table></div>')
    return win(x, y, w, h, title, body, "#107c41")


def browser(x, y, w, h, tabs, url, content, on=0, dark=False, extra_tab="", ring=None):
    rs = ' style="outline:3px solid #ed1aa0;outline-offset:-3px"'
    t = "".join(f'<div class="{"on" if i == on else ""}"{rs if i == ring else ""}>{n}</div>' for i, n in enumerate(tabs)) + extra_tab
    style = ' style="background:#202124"' if dark else ""
    addr = f'<div class="addr"{style}><span style="color:#888">← → ⟳</span><div{" style=background:#3c4043;color:#ddd" if dark else ""}>{url}</div></div>'
    tabsh = f'<div class="tabs"{" style=background:#35363a" if dark else ""}>{t}</div>'
    return win(x, y, w, h, tabs[on] if tabs else "", tabsh + addr + f'<div style="position:absolute;inset:80px 0 0 0;overflow:hidden">{content}</div>', "#0ea5e9")


def article(scale=1.0):
    f = 15 * scale
    return (f'<div style="padding:{28*scale}px {60*scale}px;font-size:{f}px;line-height:1.7;width:{1150}px">'
            f'<div style="font-size:{f*1.9}px;font-weight:800;margin-bottom:{10*scale}px">우리 고장의 옛 이야기 (가상 자료)</div>'
            '<p>옛날 이 마을 앞에는 큰 느티나무가 있었습니다. 마을 사람들은 해마다 나무 아래 모여 한 해 농사를 이야기했고, '
            '아이들은 그늘에서 공기놀이를 하며 놀았습니다.</p><p>나무는 마을의 이정표가 되었고, 먼 길을 떠났던 사람도 나무를 보면 집에 다 왔다는 것을 알았습니다. '
            '지금도 그 자리에는 작은 비석이 남아 있습니다.</p><p>여러분 고장에도 이런 이야기가 있나요? 어른들께 여쭈어 보고 모둠에서 나누어 봅시다.</p></div>')


def ppt_editor(sel=12, total=20):
    th = "".join(f'<div style="display:flex;gap:6px;align-items:flex-start;margin:8px 0"><span style="font-size:11px;width:16px;color:#555">{i}</span>'
                 f'<div style="width:150px;height:84px;background:#fff;border:{"3px solid #c43e1c" if i == sel else "1px solid #ccc"};font-size:9px;padding:6px">'
                 f'<b>{"식물의 한살이" if i == 1 else f"{i}. 활동"}</b></div></div>' for i in range(max(1, sel - 3), min(total, sel + 2) + 1))
    body = (f'<div class="ribbon" style="background:#fbeee9">{"<span style=background:#f4d3c6></span>" * 16}</div>'
            f'<div style="position:absolute;top:58px;left:0;bottom:0;width:200px;background:#f0f0f0;padding:6px 10px;overflow:hidden">{th}</div>'
            f'<div style="position:absolute;top:58px;left:200px;right:0;bottom:0;background:#e6e6e6">'
            f'<div class="slide" style="left:60px;top:40px;width:720px;height:405px;box-shadow:0 2px 8px rgba(0,0,0,.2)">'
            f'{lesson_slide("12. 싹이 트는 조건", "물 · 온도 · 공기 중 무엇이 필요할까?")}</div></div>')
    return body


# ------------------------------------------------------------------ 장면 36개
S = {}

S["01_lock_a"] = page(desktop(grades_win() + tag("성적·상담 기록을 띄워 둔 채 자리를 비울 때")))
S["01_lock_b"] = page(
    '<div style="position:absolute;inset:0;background:linear-gradient(160deg,#1e3a5f,#4b6cb7 60%,#c3a6e8)"></div>'
    '<div style="position:absolute;left:0;right:0;top:170px;text-align:center;color:#fff">'
    '<div style="font-size:120px;font-weight:300;line-height:1">9:12</div><div style="font-size:26px;margin-top:10px">10월 20일 화요일</div></div>'
    '<div style="position:absolute;left:0;right:0;bottom:70px;text-align:center;color:#fff;font-size:15px">🔒 잠김 · 비밀번호를 넣어야 열려요</div>'
    + key("Win + L"))
S["02_desktop_a"] = page(classroom_tv(
    f'<div class="mini">{lesson_slide()}</div>'
    f'<div style="position:absolute;left:420px;top:40px;transform:scale(.8);transform-origin:0 0">{messenger_win(0, 0)}</div>',
    "교실 TV") + tag("수업 화면 위에 업무 메신저가 그대로 보일 때"))
S["02_desktop_b"] = page(classroom_tv(
    '<div class="mini"></div><div style="position:absolute;left:20px;top:20px;display:grid;gap:18px">'
    + "".join(f'<div style="width:46px;height:40px;border-radius:6px;background:{c}"></div>' for c in ("#fbbf24", "#60a5fa", "#a78bfa")) + '</div>',
    "교실 TV") + key("Win + D") + tag("창이 모두 내려가고 바탕화면만", "누른 뒤"))
S["03_tvblack_a"] = page(classroom_tv(
    '<div style="position:absolute;inset:0;background:#000"></div>', "수업 시작했는데 화면이 까맣게")
    + tag("TV가 검은 화면이거나 멈췄을 때"))
S["03_tvblack_b"] = page(classroom_tv(lesson_slide(), "삑 · 한 번 깜빡이고 다시 나와요") + key("Win + Ctrl + Shift + B")
                         + tag("그래픽만 다시 시작 · 파일은 그대로", "누른 뒤"))

hang = hwp_win(150, 60, 980, 640, "가정통신문.hwp - 한글 (응답 없음)", NOTICE, cls="dim")
S["04_taskmgr_a"] = page(desktop(
    hang + '<div style="position:absolute;left:150px;top:94px;width:980px;height:606px;background:rgba(255,255,255,.55)"></div>'
    + win(400, 280, 480, 190, "한글", '<div style="padding:22px 24px;font-size:15px">한글이(가) 응답하지 않습니다.<br><span style="color:#666;font-size:13px">프로그램이 응답할 때까지 기다리거나 닫을 수 있어요.</span>'
          '<div style="display:flex;gap:10px;justify-content:flex-end;margin-top:22px"><span style="border:1px solid #ccc;padding:6px 14px;border-radius:4px;font-size:13px">기다리기</span></div></div>', "#0b6bcb")
    + tag("한글이 '응답 없음'으로 멈췄을 때")))
procs = [("한글 (응답 없음)", "0%", "1,204 MB", True), ("Microsoft Edge (12)", "3.1%", "980 MB", False), ("업무 메신저", "0.4%", "210 MB", False),
         ("PowerPoint", "1.2%", "350 MB", False), ("Windows 탐색기", "0.8%", "120 MB", False)]
rows = "".join(f'<tr style="background:{"#cce4ff" if s else "#fff"}"><td style="padding:9px 14px">{n}</td><td>{c}</td><td>{m}</td></tr>' for n, c, m, s in procs)
S["04_taskmgr_b"] = page(desktop(hang + win(260, 120, 760, 470, "작업 관리자",
    '<div style="display:flex;height:100%"><div style="width:150px;background:#f3f3f3;padding:14px;font-size:13px;line-height:2.2">프로세스<br>성능<br>앱 기록<br>시작 앱</div>'
    '<div style="flex:1;position:relative"><div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;font-weight:700">프로세스'
    '<span style="background:#0067c0;color:#fff;font-weight:600;font-size:13px;padding:7px 16px;border-radius:4px;outline:4px solid #ed1aa0;outline-offset:3px">작업 끝내기</span></div>'
    f'<table style="width:100%;border-collapse:collapse;font-size:13px"><tr style="color:#666;text-align:left"><th style="padding:6px 14px">이름</th><th>CPU</th><th>메모리</th></tr>{rows}</table></div></div>', "#334155")
    + key("Ctrl + Shift + Esc") + tag("멈춘 프로그램 고르고 [작업 끝내기]", "누른 뒤")))


def two_screens(video_on_tv):
    vid = ('<div style="position:absolute;left:30px;top:30px;width:300px;height:190px;background:#111;border-radius:6px;overflow:hidden">'
           '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;font-size:42px">▶</div>'
           '<div style="position:absolute;left:0;right:0;bottom:0;background:rgba(0,0,0,.6);color:#fff;font-size:12px;padding:6px 10px">수업 영상 (가상)</div></div>')
    big = ('<div style="position:absolute;inset:0;background:#111;display:flex;align-items:center;justify-content:center;color:#fff;font-size:80px">▶</div>'
           '<div style="position:absolute;left:0;right:0;bottom:0;background:rgba(0,0,0,.6);color:#fff;font-size:18px;padding:10px 16px">수업 영상 (가상)</div>')
    mine = f'<div class="mini">{"" if video_on_tv else vid}</div>'
    tv = f'<div class="mini">{big if video_on_tv else ""}</div>'
    return (f'<div class="room"></div>'
            f'<div class="tv" style="left:70px;top:250px;width:380px;height:260px;border-radius:10px;padding:10px"><div class="scr">{mine}</div></div>'
            f'<div class="stand" style="left:245px;top:510px;width:30px;height:60px"></div><div class="cap" style="left:70px;width:380px;top:590px">내 모니터</div>'
            f'<div class="tv" style="left:540px;top:120px;width:680px;height:410px"><div class="scr">{tv}</div><div class="brand">CLASSROOM TV</div></div>'
            f'<div class="stand" style="left:865px;top:530px;width:30px;height:60px"></div><div class="cap" style="left:540px;width:680px;top:600px">교실 TV (확장 화면)</div>'
            + ('<div style="position:absolute;left:460px;top:330px;font-size:64px;color:#ed1aa0;font-weight:900">➜</div>' if video_on_tv else ""))


S["05_movetv_a"] = page(two_screens(False) + tag("영상이 내 모니터에만 열렸을 때"))
S["05_movetv_b"] = page(two_screens(True) + key("Win + Shift + →") + tag("창이 TV로 한 번에 넘어가요", "누른 뒤"))

vid_page = ('<div style="padding:24px 40px"><div style="width:760px;height:400px;background:#111;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:64px">▶</div>'
            '<div style="font-size:20px;font-weight:800;margin-top:14px">[과학] 씨앗이 싹 트는 과정 타임랩스 (가상 영상)</div></div>')
S["06_reopentab_a"] = page(desktop(browser(60, 30, 1160, 680, ["학급 알림장 (가상)", "수업 자료 모음 (가상)"], "class.example.kr/notice",
    '<div style="padding:30px 40px;font-size:18px;color:#555">알림장 화면 …</div>',
    extra_tab='<div style="border:2px dashed #ed1aa0;color:#ed1aa0;font-weight:700;background:transparent">✕ 수업 영상 탭을 실수로 닫음</div>')
    + tag("띄워 둔 수업 영상 탭을 실수로 닫았을 때")))
S["06_reopentab_b"] = page(desktop(browser(60, 30, 1160, 680, ["학급 알림장 (가상)", "수업 자료 모음 (가상)", "씨앗 타임랩스 (가상 영상)"],
    "video.example.kr/watch?v=seed", vid_page, on=2, ring=2)
    + key("Ctrl + Shift + T") + tag("닫은 탭이 그대로 돌아와요", "누른 뒤")))
acct = ('<div style="padding:30px 40px"><div style="display:flex;align-items:center;gap:14px;font-size:18px">'
        '<div style="width:52px;height:52px;border-radius:50%;background:#7c3aed;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800">권</div>'
        '<div><b>선생님 계정 (가상)</b><div style="color:#666;font-size:14px">teacher@example.kr · 로그인됨</div></div></div>'
        '<div style="margin-top:24px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px">'
        + "".join(f'<div style="height:120px;border-radius:10px;background:#f1f3f4;padding:14px;font-size:14px">{n}</div>' for n in ("받은 메일함 32", "학급 드라이브", "설문 결과", "상담 메모", "학년 협의록", "개인 사진"))
        + '</div></div>')
S["07_incognito_a"] = page(desktop(browser(60, 30, 1160, 680, ["메일 - 선생님 계정 (가상)"], "mail.example.kr/inbox", acct)
    + '<div style="position:absolute;left:880px;top:610px;background:#fff7ed;border:2px solid #f59e0b;border-radius:10px;padding:10px 14px;font-size:14px;font-weight:700">특별실 공용 PC · 다음 반도 이 PC를 써요</div>'
    + tag("공용 PC에 내 계정이 로그인된 채 남을 때")))
S["07_incognito_b"] = page(desktop(browser(60, 30, 1160, 680, ["새 InPrivate 탭"], "검색어 또는 웹 주소 입력",
    '<div style="position:absolute;inset:0;background:#202124;color:#e8eaed;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">'
    '<div style="font-size:56px">🕶️</div><div style="font-size:28px;font-weight:800">시크릿(InPrivate) 창</div>'
    '<div style="font-size:16px;color:#bdc1c6;text-align:center;line-height:1.7">이 창을 닫으면 로그인 기록·방문 기록·쿠키가 지워져요.<br>공용 PC에서는 여기서 로그인하세요.</div></div>', dark=True)
    + key("Ctrl + Shift + N") + tag("창을 닫으면 로그인 기록이 남지 않아요", "누른 뒤")))

quiz = ('<div style="position:absolute;inset:0;background:#fff;padding:120px 90px 60px"><div style="font-size:24px;color:#2563eb;font-weight:800">퀴즈 3 (가상)</div>'
        '<div style="font-size:46px;font-weight:900;margin:14px 0 30px">씨가 싹 트는 데 꼭 필요하지 않은 것은?</div>'
        '<div style="font-size:32px;line-height:1.9">① 물　② 알맞은 온도　③ 햇빛　④ 공기</div>'
        '<div style="position:absolute;right:80px;bottom:60px;background:#fee2e2;color:#b91c1c;font-size:34px;font-weight:900;padding:14px 26px;border-radius:14px">정답: ③ 햇빛</div></div>')
S["08_pptblack_a"] = page(quiz + tag("정답이 학생들에게 먼저 보일 때"), bg="#fff")
S["08_pptblack_b"] = page('<div style="position:absolute;inset:0;background:#000"></div>' + key("B")
                          + tag("검은 화면 · 아무 키나 누르면 돌아와요", "누른 뒤"), bg="#000")
S["09_pptfrom_a"] = page(desktop(win(40, 20, 1200, 700, "식물의 한살이 (가상).pptx - PowerPoint", ppt_editor(), "#c43e1c")
                         + tag("지난 시간에 멈춘 12번 슬라이드부터 이어갈 때")))
S["09_pptfrom_b"] = page(f'<div style="position:absolute;inset:0">{lesson_slide("12. 싹이 트는 조건", "물 · 온도 · 공기 중 무엇이 필요할까?", "12 / 20")}</div>'
                         + key("Shift + F5") + tag("보고 있던 12번부터 바로 시작", "누른 뒤"), bg="#fff")

textbook = ('<div style="position:absolute;inset:0;background:#525659"><div style="position:absolute;left:250px;top:20px;width:660px;height:900px;background:#fff;padding:40px 50px">'
            '<div style="font-size:13px;color:#888">과학 4-2 (가상 교과서) · 32쪽</div><div style="font-size:28px;font-weight:900;margin:8px 0 14px">식물의 한살이를 관찰해요</div>'
            '<div style="display:flex;gap:16px;align-items:flex-end;height:200px;padding:10px;border:1px solid #ddd;border-radius:10px">'
            + "".join(f'<div style="flex:1;text-align:center;font-size:12px"><div style="height:{h}px;background:linear-gradient(#22c55e,#15803d);border-radius:40px 40px 4px 4px;margin:0 auto;width:{w}px"></div>{t}</div>'
                      for h, w, t in ((20, 20, "씨"), (50, 14, "싹"), (100, 16, "잎"), (150, 18, "꽃"), (170, 22, "열매")))
            + '</div><p style="font-size:14px;line-height:1.8;margin-top:16px">씨를 심고 물을 주면 싹이 트고, 잎과 줄기가 자라며, 꽃이 피고 열매를 맺습니다.</p></div></div>')
S["10_capture_a"] = page(desktop(win(120, 30, 1040, 680, "과학4-2 (가상 교과서).pdf - Edge", textbook, "#dc2626")
                         + tag("교과서 그림만 학습지에 넣고 싶을 때")))
S["10_capture_b"] = page(desktop(win(120, 30, 1040, 680, "과학4-2 (가상 교과서).pdf - Edge", textbook, "#dc2626"))
    + '<div style="position:absolute;left:409px;top:174px;width:580px;height:226px;border:2px solid #fff;box-shadow:0 0 0 2000px rgba(0,0,0,.5)"></div>'
    + '<div style="position:absolute;left:500px;top:14px;background:#fff;border-radius:8px;padding:8px 14px;font-size:13px;display:flex;gap:14px;box-shadow:0 4px 14px rgba(0,0,0,.3)">▭ 사각형 &nbsp; ✎ 자유형 &nbsp; ▢ 창 &nbsp; ⛶ 전체 화면</div>'
    + key("Win + Shift + S") + tag("마우스로 원하는 부분만 끌어요", "누른 뒤"))
sheet = ('<h1>식물의 한살이 학습지</h1><p>4학년 ___반 ___번 이름 ________</p>'
         '<div style="outline:4px solid #ed1aa0;outline-offset:4px;border:1px solid #bbb;height:190px;display:flex;gap:12px;align-items:flex-end;padding:10px;margin:10px 0 16px">'
         + "".join(f'<div style="flex:1;text-align:center;font-size:11px"><div style="height:{h}px;background:linear-gradient(#22c55e,#15803d);border-radius:30px 30px 3px 3px;margin:0 auto;width:{w}px"></div>{t}</div>'
                   for h, w, t in ((18, 18, "씨"), (44, 12, "싹"), (90, 14, "잎"), (130, 16, "꽃"), (150, 20, "열매")))
         + '</div><p>1. 씨가 싹 트려면 무엇이 필요할까요?<br>______________________________</p><p>2. 위 그림에서 가장 오래 걸릴 것 같은 단계는?<br>______________________________</p>')
S["10_capture_c"] = page(desktop(hwp_win(120, 30, 1040, 680, "식물의 한살이 학습지.hwp - 한글", sheet)
    + key("Ctrl + V") + tag("학습지에 바로 붙여요", "붙인 뒤")))
S["11_zoom_a"] = page(desktop(browser(60, 30, 1160, 680, ["옛 이야기 (가상 자료)"], "story.example.kr/neutinamu", article(1.0))
                      + '<div style="position:absolute;right:60px;bottom:80px;background:#fff;border:2px solid #f59e0b;border-radius:10px;padding:10px 14px;font-weight:700">뒷자리: "글씨가 안 보여요!"</div>'
                      + tag("TV 속 글씨가 작아 뒷자리에서 안 보일 때")))
S["11_zoom_b"] = page(desktop(browser(60, 30, 1160, 680, ["옛 이야기 (가상 자료)"], "story.example.kr/neutinamu", article(1.75))
                      + '<div style="position:absolute;left:880px;top:76px;background:#fff;border:1px solid #ccc;border-radius:6px;padding:4px 10px;font-size:13px;box-shadow:0 2px 8px rgba(0,0,0,.2)">🔍 175%</div>'
                      + key("Ctrl + 마우스 휠 ↑") + tag("글씨가 커지고, Ctrl + 0이면 원래대로", "누른 뒤")))
gongmun = ('<div style="padding:30px 40px;font-size:14px;line-height:1.9"><div style="text-align:center;font-size:22px;font-weight:900">가 상 교 육 지 원 청</div>'
           '<p>수신: 관내 초등학교장<br>제목: 2026 가을 독서 주간 운영 안내 (가상)</p><p>1. 관련: 가상교육지원청-1234(2026.10.10.)<br>'
           '2. 학교별 독서 주간을 아래와 같이 운영하고 결과를 제출하여 주시기 바랍니다.<br>　가. 기간: 2026. 11. 2.~11. 6.<br>　나. 제출: 2026. 11. 13.까지</p></div>')
gian = '<h1 style="font-size:18px">2026 가을 독서 주간 운영 계획</h1><p>1. 관련: 가상교육지원청-1234<br>2. 위 호와 관련하여 본교의 독서 주간을 아래와 같이 운영하고자 합니다.<br>　가. 기간: </p>'
S["12_snap_a"] = page(desktop(win(120, 40, 820, 600, "공문_독서주간 (가상).pdf", gongmun, "#dc2626")
                      + hwp_win(330, 140, 820, 560, "독서주간 계획 기안.hwp - 한글", gian, pw=520, ph=600)
                      + tag("공문을 보면서 기안문을 써야 할 때")))
S["12_snap_b"] = page(desktop(win(0, 0, 640, 752, "공문_독서주간 (가상).pdf", gongmun, "#dc2626")
                      + hwp_win(640, 0, 640, 752, "독서주간 계획 기안.hwp - 한글", gian, pw=480, ph=640)
                      + key("Win + ←") + tag("왼쪽·오른쪽 반반으로 나뉘어요", "누른 뒤")))


def notice_pages(tight):
    tail = '<p style="text-align:center;margin:14px 0 0">2026. 10. 20.</p><p style="text-align:center;font-size:17px;font-weight:900;margin:4px 0 0">가상초등학교장</p>'
    pg = 'position:absolute;left:50%;transform:translateX(-50%);width:500px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.3);padding:34px 48px;font-size:12.5px;line-height:1.75;'
    if tight:
        pages = f'<div style="{pg}top:16px;height:520px;letter-spacing:-0.05em;line-height:1.62">{NOTICE}{tail}</div>'
    else:
        pages = (f'<div style="{pg}top:16px;height:520px">{NOTICE}</div>'
                 f'<div style="{pg}top:552px;height:300px;padding-top:24px">{tail}</div>')
    body = f'<div class="hwpbar">{"<span></span>" * 14}</div><div class="paper-bg">{pages}</div>'
    return win(200, 20, 880, 700, "현장체험학습 가정통신문.hwp - 한글 · " + ("1쪽" if tight else "2쪽"), body, "#0b6bcb")


S["13_hwpspace_a"] = page(desktop(notice_pages(False) + '<div style="position:absolute;left:840px;top:630px;background:#fee2e2;color:#b91c1c;font-weight:800;padding:8px 14px;border-radius:8px">← 두 줄이 2쪽으로 넘침</div>'
                          + tag("가정통신문이 딱 두 줄 넘쳐 2쪽이 될 때")))
S["13_hwpspace_b"] = page(desktop(notice_pages(True) + key("Alt + Shift + N") + tag("자간을 줄이니 1쪽에 쏙", "누른 뒤")))
sc = [["번호", "이름", "국어", "수학", "사회", "합계"]] + [[i + 1, n, 80 + (i * 7) % 19, 75 + (i * 5) % 23, 82 + (i * 3) % 15, ""] for i, n in enumerate(STUDENTS[:8])]
S["14_autosum_a"] = page(desktop(excel_win(100, 30, 1080, 680, sc, sel=(2, 5)) + tag("과목 점수를 더한 합계 칸을 채울 때")))
sc2 = [r[:] for r in sc]
for r in sc2[1:]:
    r[5] = r[2] + r[3] + r[4]
S["14_autosum_b"] = page(desktop(excel_win(100, 30, 1080, 680, sc2, sel=(2, 5), fx="=SUM(C2:E2)") + key("Alt + =") + tag("합계가 바로 · 아래로 채우기만", "누른 뒤")))
hd = lambda s: ('<h1>학부모 공개수업 안내</h1>'
                f'<p style="font-size:20px;font-weight:800">대상: <span style="outline:3px solid {"#dc2626" if s == "1.2" else "#ed1aa0"};outline-offset:3px;border-radius:3px">{s}학년</span> 학부모님</p><p>{s}학년 학부모님께서는 11월 5일(목) 2교시에 각 교실로 오시기 바랍니다.</p>')
S["15_middot_a"] = page(desktop(hwp_win(200, 30, 880, 680, "공개수업 안내.hwp - 한글", hd("1.2"))
                        + tag("'1.2학년'처럼 온점으로 잘못 쓸 때")))
S["15_middot_b"] = page(desktop(hwp_win(200, 30, 880, 680, "공개수업 안내.hwp - 한글", hd("1·2"))
                        + key("Alt 누른 채 0183") + tag("가운데점(·)으로 바르게", "누른 뒤")))
cell = ('<div style="position:absolute;inset:0;background:#fff;padding:40px 60px"><div style="font-size:30px;font-weight:900">세포를 관찰해요 (가상 자료)</div>'
        '<svg style="position:absolute;left:540px;top:290px" width="180" height="120" viewBox="0 0 180 120"><ellipse cx="90" cy="60" rx="85" ry="55" fill="#dcfce7" stroke="#15803d" stroke-width="3"/>'
        '<circle cx="70" cy="55" r="16" fill="#7c3aed"/><circle cx="120" cy="40" r="6" fill="#16a34a"/><circle cx="125" cy="75" r="6" fill="#16a34a"/><circle cx="45" cy="85" r="5" fill="#16a34a"/></svg>'
        '<div style="position:absolute;left:560px;top:415px;font-size:12px;color:#666">현미경 사진 (작게 실림)</div></div>')
S["16_zoomit_a"] = page(classroom_tv(cell, "그림이 너무 작아 설명하기 어려움") + tag("TV 속 작은 그림을 짚어 설명할 때"))
cellbig = ('<div style="position:absolute;inset:0;background:#fff"><svg style="position:absolute;left:40px;top:10px" width="700" height="430" viewBox="0 0 180 120">'
           '<ellipse cx="90" cy="60" rx="85" ry="55" fill="#dcfce7" stroke="#15803d" stroke-width="2"/><circle cx="70" cy="55" r="16" fill="#7c3aed"/>'
           '<circle cx="120" cy="40" r="6" fill="#16a34a"/><circle cx="125" cy="75" r="6" fill="#16a34a"/><circle cx="45" cy="85" r="5" fill="#16a34a"/>'
           '<ellipse cx="70" cy="55" rx="24" ry="22" fill="none" stroke="#dc2626" stroke-width="1.6"/><path d="M95 50 Q120 20 150 18" stroke="#dc2626" stroke-width="1.6" fill="none"/>'
           '<text x="118" y="14" font-size="9" fill="#dc2626" font-weight="700">핵</text></svg></div>')
S["16_zoomit_b"] = page(classroom_tv(cellbig, "확대한 채 그 위에 빨간 펜으로") + key("Ctrl + 1 → Ctrl + 2") + tag("크게 보여 주고 바로 판서", "누른 뒤"))
S["16_zoomit_c"] = page(classroom_tv('<div style="position:absolute;inset:0;background:#fff;display:flex;align-items:center;justify-content:center;font-size:190px;font-weight:300;color:#111">4:59</div>',
                                     "모둠 활동 5분 · 남은 시간이 크게") + key("Ctrl + 3") + tag("쉬는 시간·활동 시간 타이머", "누른 뒤"))
S["17_ditto_a"] = page(desktop(
    win(60, 40, 560, 600, "학교 기본 정보 메모.txt - 메모장", '<div style="padding:18px;font-size:15px;line-height:2">학교 주소: 가상시 가상로 123<br>대표 전화: 000-123-4567<br>행정실: 000-123-4568<br>'
        '<span style="background:#bfdbfe">담임 인사말: 안녕하세요, 3학년 2반 담임입니다.</span><br>현장체험 링크: example.kr/trip</div>', "#64748b")
    + hwp_win(660, 40, 560, 600, "가정통신문.hwp - 한글", '<h1 style="font-size:16px">가정통신문</h1><p>주소: <span style="background:#fde68a">가상시 가상로 123</span><br>전화: ?<br>인사말: ?</p>', pw=440, ph=520)
    + '<div style="position:absolute;left:470px;top:660px;background:#fff;border:2px solid #f59e0b;border-radius:10px;padding:10px 16px;font-weight:700">복사할 때마다 앞에 복사한 게 사라져서 왔다 갔다…</div>'
    + tag("여러 개를 번갈아 복사·붙여넣기 할 때")))
items = ["담임 인사말: 안녕하세요, 3학년 2반 담임입니다.", "행정실: 000-123-4568", "대표 전화: 000-123-4567", "학교 주소: 가상시 가상로 123", "현장체험 링크: example.kr/trip",
         "붙임 1부. 끝.", "준비물: 도시락, 물, 돗자리"]
dl = "".join(f'<div style="padding:9px 12px;font-size:13.5px;border-bottom:1px solid #eee;background:{"#cce4ff" if i in (0, 1, 2) else "#fff"}">{i}  {t}</div>' for i, t in enumerate(items))
S["17_ditto_b"] = page(desktop(
    hwp_win(330, 40, 860, 640, "가정통신문.hwp - 한글", '<h1 style="font-size:16px">가정통신문</h1><p>주소: 가상시 가상로 123<br>전화: 000-123-4567 / 행정실 000-123-4568<br>인사말: 안녕하세요, 3학년 2반 담임입니다.</p>', pw=520, ph=520)
    + win(60, 140, 430, 380, "Ditto", f'<div style="padding:8px;border-bottom:1px solid #ddd;font-size:13px;color:#888">🔍 검색</div>{dl}', "#1d4ed8")
    + key("Ctrl + `") + tag("여러 개 골라 Enter → 한꺼번에", "누른 뒤")))


# ------------------------------------------------------------------ 찍기
def main():
    want = sys.argv[1:]
    names = [n for n in S if not want or any(w in n for w in want)]
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="tipscenes_")
    prof = os.path.join(tmp, "profile")
    for n in names:
        src = os.path.join(tmp, n + ".html")
        open(src, "w", encoding="utf-8").write(S[n])
        dst = os.path.join(OUT, n + ".png")
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={prof}",
                        "--force-device-scale-factor=1", f"--window-size={W},{H}", "--virtual-time-budget=4000",
                        f"--screenshot={dst}", "file:///" + src.replace(os.sep, "/")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        print(("✓ " if os.path.exists(dst) else "✗ ") + n)


if __name__ == "__main__":
    main()
