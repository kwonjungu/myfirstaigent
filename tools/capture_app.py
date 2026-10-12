# inline AI 앱 화면 캡처 (교안 '막히면' 장용) — docs/2026-10-12-capture-plan.md B
# 준비: inline AI를 --remote-debugging-port=9333 으로 실행. 측정기(speedloop)가 돌고 있지 않을 때만.
# 원칙: 한 번에 하나, 창을 앞으로, 시간 제한, 찍은 뒤 눈으로 확인.
# 사용: python capture_app.py <출력 폴더> [sidebar|hwp|accept]
import os, sys, time, subprocess
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "speedloop"))
from run import FIND, click, edit_page, office_pids, quiesce, page_state  # noqa: E402

OUT = sys.argv[1]
WHICH = set(sys.argv[2:]) or {"sidebar", "hwp", "accept"}
DOC = os.path.join(os.path.expanduser("~"), "Desktop", "inlineAI_실습", "02_가정통신문_양식맞추기", "실습 1. 기존 가정통신문 활용하기.hwpx")
os.makedirs(OUT, exist_ok=True)


def shot(page, name, clip=None):
    page.bring_to_front()
    page.wait_for_timeout(800)
    page.screenshot(path=os.path.join(OUT, name), clip=clip, timeout=5000)
    print("찍음", name, flush=True)


with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
    pg = [x for c in b.contexts for x in c.pages if "wlm=main" in x.url][0]
    quiesce(pg)
    if "sidebar" in WHICH:
        click(pg, "새 에이전트", wait=1200)
        # 왼쪽 위: 새 에이전트 · 한/글 편집하기 · Word · Excel (계정 영역은 화면 아래라 잘라 냄)
        shot(pg, "sidebar_edit_modes.png", clip={"x": 0, "y": 40, "width": 300, "height": 175})
    if {"hwp", "accept"} & WHICH:
        before = office_pids()
        os.startfile(DOC)
        time.sleep(8)
        click(pg, "한/글 편집하기", wait=2500)
        ed = edit_page(pg, "hwp")
        ed.bring_to_front()
        h = ed.evaluate_handle(FIND, ["새 에이전트", "button"]).as_element()
        h.evaluate("e=>e.click()")
        ed.wait_for_timeout(1500)
        if "hwp" in WHICH:
            shot(ed, "hwp_edit_window.png")
        if "accept" in WHICH:
            ed.locator("textarea").first.evaluate("e=>e.focus()")
            ed.keyboard.insert_text("할 일: 본문 제목만 '2026 디지털 시민교육 주간 안내'로 바꿔줘\n조건: 다른 곳은 건드리지 마\n끝나면: 새 이름으로 저장해")
            ed.keyboard.press("Enter")
            t0, calm = time.time(), 0
            while time.time() - t0 < 300:
                time.sleep(2)
                calm = 0 if page_state(ed)["busy"] else calm + 1
                if calm >= 3 and time.time() - t0 > 10:
                    break
            if ed.evaluate_handle(FIND, ["전체 수락하기", "button"]).as_element() is None:
                print("전체 수락하기 버튼이 안 보임 — 찍지 않음", flush=True)
            else:
                shot(ed, "hwp_accept_all.png")
        for pid in office_pids() - before:
            subprocess.run(["taskkill", "/f", "/pid", str(pid)], capture_output=True)
