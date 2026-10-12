# 바탕화면 inlineAI_실습을 레포 zip 상태로 되돌린다 (폴더 경로는 유지: inline AI에 등록된 경로라서)
import os, shutil, sys, zipfile
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIP = os.path.join(REPO, "download", "inlineAI_실습.zip")
TARGET = os.path.join(os.path.expanduser("~"), "Desktop", "inlineAI_실습")
BACKUP = TARGET + "_구판_1005"


def reset(only=None):
    """only: 폴더 이름(예 '01_다운로드정리')을 주면 그 폴더만 되돌린다."""
    assert os.path.isdir(BACKUP), "첫 실행 전 백업이 없어요: " + BACKUP
    os.makedirs(TARGET, exist_ok=True)
    for name in os.listdir(TARGET):
        if only and name != only:
            continue
        p = os.path.join(TARGET, name)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    z = zipfile.ZipFile(ZIP)
    for i in z.infolist():
        rel = i.filename.split("/", 1)[1] if "/" in i.filename else i.filename
        if not rel or i.filename.endswith("/") or (only and not rel.startswith(only + "/")):
            continue
        p = os.path.join(TARGET, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(z.read(i))


if __name__ == "__main__":
    reset(sys.argv[1] if len(sys.argv) > 1 else None)
    print("reset", sys.argv[1:] or "전체", "->", TARGET)
