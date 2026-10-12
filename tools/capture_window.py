# 창 하나를 몇 초마다 자동으로 찍는다 (앱을 조작하지 않고 그림만 저장) — ChatGPT 앱 폴더 모드 비교용
# 사용: python capture_window.py "<창 제목에 들어 있는 글자>" <저장 폴더> [간격초=4] [최대분=40]
# 멈추기: 저장 폴더에 STOP 파일을 만들거나 Ctrl+C. 같은 화면이 이어지면 저장하지 않는다.
import ctypes, os, sys, time, hashlib
import win32gui, win32ui
from PIL import Image

KEY, OUT = sys.argv[1], sys.argv[2]
EVERY = float(sys.argv[3]) if len(sys.argv) > 3 else 4
LIMIT = float(sys.argv[4]) * 60 if len(sys.argv) > 4 else 40 * 60
os.makedirs(OUT, exist_ok=True)
ctypes.windll.user32.SetProcessDPIAware()


def find():
    hits = []
    win32gui.EnumWindows(lambda h, _: hits.append(h) if win32gui.IsWindowVisible(h) and KEY in win32gui.GetWindowText(h) else None, None)
    return hits[0] if hits else None


def grab(h):
    l, t, r, b = win32gui.GetWindowRect(h)
    w, hgt = r - l, b - t
    if w < 50 or hgt < 50:
        return None
    hdc = win32gui.GetWindowDC(h)
    src = win32ui.CreateDCFromHandle(hdc)
    mem = src.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(src, w, hgt)
    mem.SelectObject(bmp)
    ctypes.windll.user32.PrintWindow(h, mem.GetSafeHdc(), 2)  # 2 = 가려진 창도 그리기
    info = bmp.GetInfo()
    img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]), bmp.GetBitmapBits(True), "raw", "BGRX", 0, 1)
    win32gui.DeleteObject(bmp.GetHandle()); mem.DeleteDC(); src.DeleteDC(); win32gui.ReleaseDC(h, hdc)
    return img


t0, last, n = time.time(), None, 0
log = open(os.path.join(OUT, "capture_log.txt"), "a", encoding="utf-8")
print(f"찍기 시작: '{KEY}' 창, {EVERY}초마다 → {OUT}", flush=True)
while time.time() - t0 < LIMIT and not os.path.exists(os.path.join(OUT, "STOP")):
    h = find()
    img = grab(h) if h else None
    if img is not None:
        d = hashlib.md5(img.resize((160, 100)).tobytes()).hexdigest()
        if d != last:
            n += 1
            stamp = time.strftime("%H%M%S")
            name = f"{n:03d}_{stamp}.png"
            img.save(os.path.join(OUT, name))
            log.write(f"{stamp}\t{name}\t{win32gui.GetWindowText(h)}\n"); log.flush()
            last = d
    time.sleep(EVERY)
print(f"끝: {n}장", flush=True)
