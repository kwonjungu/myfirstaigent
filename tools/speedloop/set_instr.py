# inline AI 설정 > 지시사항을 파일 내용으로 바꾸고 저장 확인 (500자 제한)
import sys
from playwright.sync_api import sync_playwright
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import click

def set_instr(pg, text):
    assert len(text) <= 500, len(text)
    click(pg, pg.evaluate("()=>[...document.querySelectorAll('button')].map(e=>e.innerText.trim().split(String.fromCharCode(10))[0]).find(t=>t.startsWith('kdhdhdbdbr'))"))
    click(pg, "설정", wait=1200)
    sel = 'textarea[placeholder^="예: 우리 회사"]'
    pg.locator(sel).click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete")
    pg.keyboard.insert_text(text); pg.wait_for_timeout(500)
    click(pg, "변경 사항 저장", wait=1500)
    click(pg, "계정 설정", "button,a,div"); click(pg, "일반 설정", "button,a,div")
    ok = pg.locator(sel).input_value() == text
    pg.go_back(); pg.go_back(); pg.go_back(); pg.wait_for_timeout(800)
    return ok

if __name__ == "__main__":
    text = open(sys.argv[1], encoding="utf-8-sig").read().replace("\r\n", "\n").strip()
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        pg = [x for c in b.contexts for x in c.pages if "wlm=main" in x.url][0]
        print("saved", set_instr(pg, text), len(text))
