# inline AI 처리 시간 측정기
# 준비: inline AI를 --remote-debugging-port=9333 으로 실행해 두기
# 사용: python run.py <태그> [케이스...]   (케이스 생략 시 전부)
import json, os, re, subprocess, sys, time
from playwright.sync_api import sync_playwright
from pywinauto import Desktop

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reset import reset, TARGET

CFG = json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))
RUNS = os.path.join(HERE, "runs")
OFFICE = ("Hwp.exe", "EXCEL.EXE", "POWERPNT.EXE")

FIND = r"""([t,sel])=>[...document.querySelectorAll(sel)].find(e=>{const x=((e.innerText||'').trim()||e.getAttribute('aria-label')||'').split(/\n/)[0].trim();return x===t})"""
STATE = r"""()=>{const b=[...document.querySelectorAll('button')].map(e=>(e.getAttribute('aria-label')||e.innerText||'').trim().split(/\n/)[0]).filter(Boolean);
const m=document.querySelector('main')||document.body; const t=m.innerText;
return {busy:b.includes('중지하기'), len:t.length, tail:t.slice(-600)}}"""


def click(pg, t, sel="button,[role=menuitem]", wait=800, no_wait=False):
    h = pg.evaluate_handle(FIND, [t, sel]).as_element()
    if h is None:
        raise RuntimeError("버튼 없음: " + t)
    h.click(no_wait_after=no_wait)
    pg.wait_for_timeout(wait)


def pick_dialog(path, edit_id):
    t0 = time.time()
    while time.time() - t0 < 15:
        apps = [w for w in Desktop(backend="uia").windows() if w.window_text() == "inline AI"]
        ds = [c for a in apps for c in a.children() if c.class_name() == "#32770"]
        if ds:
            break
        time.sleep(0.3)
    d = ds[0]
    [c for c in d.descendants(control_type="Edit") if c.element_info.automation_id == edit_id][0].set_edit_text(path)
    [c for c in d.descendants(control_type="Button") if c.element_info.automation_id == "1"][0].invoke()
    time.sleep(1.5)


def attach(pg, kind, path):
    click(pg, "파일 및 폴더 첨부하기")
    click(pg, "폴더 첨부하기" if kind == "folder" else "파일 첨부하기", no_wait=True, wait=300)
    pick_dialog(path, "1152" if kind == "folder" else "1148")


def office_pids():
    out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True, encoding="cp949", errors="ignore").stdout
    return {int(r[1]) for r in (l.strip('"').split('","') for l in out.splitlines() if l) if r[0] in OFFICE}


def snapshot(folder):
    res = {}
    for root, _, files in os.walk(folder):
        for f in files:
            p = os.path.join(root, f)
            st = os.stat(p)
            res[os.path.relpath(p, folder)] = (st.st_size, int(st.st_mtime))
    return res


def prompts(folder):
    d = os.path.join(TARGET, folder)
    if os.path.exists(os.path.join(d, "프롬프트.txt")):
        txt = open(os.path.join(d, "프롬프트.txt"), encoding="utf-8-sig").read().strip()
        items = re.split(r"(?m)^\s*\d+\.\s*", txt)
        return [re.sub(r"\n{3,}", "\n\n", x).strip() for x in items if x.strip()]
    txt = open(os.path.join(d, "시작_프롬프트.txt"), encoding="utf-8-sig").read().strip()
    return [re.sub(r"^\[[^\]]*\]\s*", "", txt).strip()]


def looks_like_question(tail):
    end = tail.strip()[-300:]
    return bool(re.search(r"\?|Q\.|말씀해 주세요|알려 주시면|진행해도 되|진행할까요|선택해 주세요|확인해 주시면", end))


CARD = r"""()=>{const sk=[...document.querySelectorAll('button')].find(e=>(e.innerText||'').trim()==='건너뛰기');
if(!sk) return null;
const opts=[...document.querySelectorAll('button,[role=option],[role=radio],li')].filter(e=>/^\d+\s/.test((e.innerText||'').trim())).map(e=>(e.innerText||'').trim());
return {q:(sk.parentElement&&sk.parentElement.innerText||'').slice(0,120), opts:[...new Set(opts)]}}"""
PREFER = ["알아서", "기본", "추천", "그대로", "진행", "비워", "확인 필요"]


def answer_card(x):
    card = x.evaluate(CARD)
    if not card or not card["opts"]:
        return None
    opts = card["opts"]
    pick = next((o for p in PREFER for o in opts if p in o), None) or next((o for o in opts if "직접" not in o), opts[0])
    h = x.evaluate_handle(r"""t=>[...document.querySelectorAll('button,[role=option],[role=radio],li')].find(e=>(e.innerText||'').trim()===t)""", pick).as_element()
    h.click()
    x.wait_for_timeout(1500)
    return pick


def pages(pg):
    return [x for x in pg.context.pages if "index.html" in x.url and "splash" not in x.url]


def edit_page(pg, mode, timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        ps = [x for x in pages(pg) if f"/edit{mode}" in x.url]
        if ps:
            return ps[0]
        time.sleep(0.5)
    raise RuntimeError("편집 창 없음: " + mode)


def page_state(x):
    try:
        return x.evaluate(STATE)
    except Exception:
        return {"busy": False, "len": 0, "tail": ""}


def send_and_wait(pg, cur, text, out, tag, limit=900):
    """cur = 입력할 창. 모든 창을 보면서 '중지하기'가 사라진 뒤 6초 조용하면 끝. 넘겨받기 카드는 한 번 누른다."""
    cur.bring_to_front()
    cur.locator("textarea").first.evaluate("e=>e.focus()")
    cur.keyboard.insert_text(text)
    cur.wait_for_timeout(400)
    t0 = time.time()
    cur.keyboard.press("Enter")
    timeline, last_busy, quiet, nshot, handoff, active, cards = [], 0.0, 0, 0, None, cur, []
    while time.time() - t0 < limit:
        time.sleep(2)
        el = round(time.time() - t0, 1)
        watch = [cur] if cur is not pg else pages(pg)
        states = [(x, page_state(x)) for x in watch]
        busy = [x for x, s in states if s["busy"]]
        if busy:
            last_busy, quiet, active = el, 0, busy[0]
        else:
            quiet += 1
        if el // 15 > nshot:
            nshot = el // 15
            timeline.append({"t": el, "text": page_state(active)["tail"]})
        if not busy and quiet >= 2:
            picked = answer_card(cur if cur is not pg else active)
            if picked:
                cards.append(picked)
                quiet = 0
                continue
        if not busy and quiet >= 3 and el > 8:
            if handoff is None and cur is pg:
                h = pg.evaluate_handle(FIND, ["이어서 작업하기", "button"]).as_element()
                if h is not None:
                    handoff = el
                    h.click()
                    time.sleep(3)
                    quiet = 0
                    continue
            break
    timed_out = time.time() - t0 >= limit
    if timed_out:
        for x in pages(pg):
            h = x.evaluate_handle(FIND, ["중지하기", "button"]).as_element()
            if h is not None:
                h.click()
    if handoff is None:
        active = cur
    return {"sec": last_busy or round(time.time() - t0, 1), "timeout": timed_out, "handoff": handoff,
            "tail": page_state(active)["tail"], "active": active, "timeline": timeline, "cards": cards}


def quiesce(pg, timeout=60):
    """모든 창의 진행 중 작업을 멈추고 6초 동안 조용해질 때까지 기다린다 (이전 실행의 잔여 작업 제거)"""
    t0, calm = time.time(), 0
    while time.time() - t0 < timeout:
        busy = False
        for x in pages(pg):
            if page_state(x)["busy"]:
                busy = True
                h = x.evaluate_handle(FIND, ["중지하기", "button"]).as_element()
                if h is not None:
                    h.evaluate("e=>e.click()")
        calm = 0 if busy else calm + 1
        if calm >= 3:
            return
        time.sleep(2)


def run_case(pg, cid, label):
    c = CFG["cases"][cid]
    folder = os.path.join(TARGET, c["folder"])
    out = os.path.join(RUNS, label, cid)
    os.makedirs(out, exist_ok=True)
    quiesce(pg)
    reset(c["folder"])
    before_pids, before = office_pids(), snapshot(folder)
    ps = prompts(c["folder"])
    mode = c.get("start", "agent")
    click(pg, "새 에이전트", wait=1200)
    cur = pg
    rec = {"case": cid, "label": label, "start": mode, "steps": []}
    for i, st in enumerate(c["steps"]):
        if st.get("open"):
            os.startfile(os.path.join(folder, st["open"]))
            time.sleep(8)
            if mode != "agent" and i == 0:
                click(pg, {"hwp": "한/글 편집하기", "excel": "Excel 편집하기"}[mode], wait=2500)
                cur = edit_page(pg, mode)
                cur.bring_to_front()
                h = cur.evaluate_handle(FIND, ["새 에이전트", "button"]).as_element()
                h.evaluate("e=>e.click()")
                cur.wait_for_timeout(1500)
        if st.get("attach_folder"):
            attach(cur, "folder", os.path.normpath(os.path.join(folder, st["attach_folder"])))
        if st.get("attach_file"):
            attach(cur, "file", os.path.join(folder, st["attach_file"]))
        r = send_and_wait(pg, cur, st.get("text") or ps[st["p"] - 1], out, f"s{i + 1}")
        total, asked = r["sec"], len(r["cards"])
        cards = list(r["cards"])
        answers = list(st.get("answers", []))
        while looks_like_question(r["tail"]) and asked < 2:
            ans = answers.pop(0) if answers else CFG["default_answer"]
            asked += 1
            r = send_and_wait(pg, r["active"], ans, out, f"s{i + 1}a{asked}")
            total += r["sec"]
            cards += r["cards"]
        cur = r["active"]
        accepted = False
        h = cur.evaluate_handle(FIND, ["전체 수락하기", "button"]).as_element()
        if h is not None:
            h.click()
            cur.wait_for_timeout(2500)
            accepted = True
            if "수락" in r["tail"][-300:]:
                r = send_and_wait(pg, cur, "전체 수락했어. 이어서 마무리해 줘.", out, f"s{i + 1}acc")
                total += r["sec"]
                h = cur.evaluate_handle(FIND, ["전체 수락하기", "button"]).as_element()
                if h is not None:
                    h.click()
                    cur.wait_for_timeout(2000)
        rec["steps"].append({"p": st["p"], "sec": round(total, 1), "asked": asked, "accepted": accepted, "cards": cards, "handoff": r["handoff"], "timeout": r["timeout"], "tail": r["tail"][-400:]})
        json.dump(r["timeline"], open(f"{out}/s{i + 1}_timeline.json", "w", encoding="utf-8"), ensure_ascii=False)
    for k, x in enumerate(pages(pg)):
        try:
            x.screenshot(path=f"{out}/final_{k}.png", timeout=5000)
            open(f"{out}/chat_{k}.txt", "w", encoding="utf-8").write(x.inner_text("body"))
        except Exception:
            pass
    time.sleep(3)
    after = snapshot(folder)
    rec["new_files"] = sorted(k for k in after if k not in before)
    rec["changed_files"] = sorted(k for k in after if k in before and after[k] != before[k])
    for pid in office_pids() - before_pids:
        subprocess.run(["taskkill", "/f", "/pid", str(pid)], capture_output=True)
    rec["total_sec"] = round(sum(s["sec"] for s in rec["steps"]), 1)
    with open(os.path.join(RUNS, "results.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(cid, rec["total_sec"], "s", [s["sec"] for s in rec["steps"]], "asked", [s["asked"] for s in rec["steps"]], "new", len(rec["new_files"]), flush=True)
    return rec


def main():
    label = sys.argv[1]
    ids = sys.argv[2:] or list(CFG["cases"])
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        pg = [x for c in b.contexts for x in c.pages if "wlm=main" in x.url][0]
        for cid in ids:
            before_pids = office_pids()
            try:
                run_case(pg, cid, label)
            except Exception as e:
                for pid in office_pids() - before_pids:
                    subprocess.run(["taskkill", "/f", "/pid", str(pid)], capture_output=True)
                print(cid, "오류", repr(e)[:300], flush=True)
                try:
                    pg.screenshot(path=os.path.join(RUNS, label, cid, "error.png"), timeout=5000)
                except Exception:
                    pass


if __name__ == "__main__":
    main()
