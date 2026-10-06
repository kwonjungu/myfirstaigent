# 새 실습 파일 미리보기 PNG (기존 tools/render_previews.py 함수 재사용)
import os, sys
OLD, MAT, OUT = sys.argv[1:4]
sys.path.insert(0, os.path.join(OLD, "tools"))
import render_previews as R
R.OUT = OUT; os.makedirs(OUT, exist_ok=True)
R.APP["xls"] = "EXCEL.EXE"
J = lambda *p: os.path.join(MAT, *p)
JOBS = [
 ("01_folder", J("01_다운로드정리","다운로드_흉내"), "folder"),
 ("01_photos", J("01_다운로드정리","다운로드_흉내"), "photos"),
 ("02_memo", J("02_가정통신문_양식맞추기","보낼내용_메모.hwpx"), 1),
 ("02_p1", J("02_가정통신문_양식맞추기","실습 1. 기존 가정통신문 활용하기.hwpx"), 1),
 ("02_p2", J("02_가정통신문_양식맞추기","실습 2. 디지털 시민교육 가정 통신문 만들기.hwpx"), 1),
 ("02_p3", J("02_가정통신문_양식맞추기","실습 3. 공무외국외여행 양식.hwpx"), 1),
 ("02_p4", J("02_가정통신문_양식맞추기","실습 4. 새로운 학교에 확장해보기 백암초 안내장 양식.hwp"), 1),
 ("03_p1", J("03_한글표만들기","실습 1 편집하며 자료 표로 추가하기.hwpx"), 1),
 ("03_p2", J("03_한글표만들기","실습 2 명렬표 파일로 학기 초 세팅하기.pptx"), 1),
 ("03_p3", J("03_한글표만들기","실습 3. 명렬표 파일 .xlsx"), 1),
 ("04_p1", J("04_작년도문서_업데이트","실습 1 2025 오현 한마음 체육대회 계획.hwp"), 1),
 ("04_p2", J("04_작년도문서_업데이트","실습 2디지털 학생 맞춤 선도학교 회의록(양식과 톤용).hwpx"), 1),
 ("04_p3a", J("04_작년도문서_업데이트","실습 3 2026학년도 백암초등학교 기초학력 보장 계획.hwpx"), 1),
 ("04_p3b", J("04_작년도문서_업데이트","실습 32026학년도 백암초등학교 두드림학교 운영 계획.hwpx"), 1),
 ("05_quote", J("05_행정처리_도움받기","지마켓 견적서.xls"), 1),
 ("05_form", J("05_행정처리_도움받기","품의 업로드 양식.xlsx"), 1),
 ("06_p1", J("06_계획서로_기안문쓰기","실습 1)2025학년도 합동소방훈련 계획(앞부분).hwpx"), 1),
 ("06_p2", J("06_계획서로_기안문쓰기","실습2)2025학년도 오현 AI 과학의 날 운영계획.hwpx"), 1),
 ("06_p2b", J("06_계획서로_기안문쓰기","실습 2-1) 백암초 제안서.pdf"), 1),
 ("07_form", J("07_계획서로_보고서쓰기","결과보고서_양식.hwpx"), 1),
 ("07_plan", J("07_계획서로_보고서쓰기","디지털동아리_운영계획.hwpx"), 1),
 ("07_stats", J("07_계획서로_보고서쓰기","참여현황_만족도.xlsx"), 1),
 ("08_tpl", J("08_계획서_문서로_PPT만들기","우리학교_PPT_양식.pptx"), 1),
 ("08_style", J("08_계획서_문서로_PPT만들기","스타일참고_강의안_말로만드는수업자료(발췌14장).pdf"), 1),
 ("09_book", J("09. 퀴즈 자동화","science_5-2-4.pdf"), 1),
 ("09_tpl", J("09. 퀴즈 자동화","블루킷 템플릿.xlsx"), 1),
]
only = set(sys.argv[4:])
for key, src, n in JOBS:
    if only and key not in only: continue
    try:
        if n == "folder": outs = R.folder_list(src, key)
        elif n == "photos": outs = R.photos_grid(src, key)
        else:
            ext = os.path.splitext(src)[1].lower().strip(".")
            if ext == "pdf": outs = R.pdf_pages(src, key, n)
            else:
                pdf = R.to_pdf(ext, src)
                outs = R.pdf_pages(pdf, key, n, crop=ext in ("xlsx", "xls")) if pdf else []
    except Exception as e:
        outs = []; print("  오류", e)
    print(key, "OK" if outs else "실패", flush=True)
