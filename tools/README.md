# 저장 IFC에서 면적표 만들기

4시간 수업의 마지막 실습입니다. 먼저 25B 한 세대, 다음 A32 05층 한 층을 읽습니다. 전체 동 IFC·전체 동 Blender 파일은 필요하지 않습니다.

실습 설명과 붙여넣을 프롬프트는 [면적 실습 안내](../area-lab/README.md)에 있습니다. 가장 쉬운 준비는 [면적 실습 ZIP](../area-lab.zip)을 받아 압축을 푸는 것입니다. ZIP 안에는 이 도구, 입력 IFC 2개와 실제 예제 결과가 들어 있습니다.

## 실행

Python 3.10 이상이 설치되어 있으면 `Run-AreaLab.cmd`를 더블클릭합니다. 첫 실행은 전용 `.area-venv`에 IfcOpenShell·NumPy·Shapely를 설치하므로 인터넷 연결이 필요합니다. 학교 PC 정책으로 스크립트가 차단되면 오류를 보존하고 담당자 또는 Codex에게 진단을 요청합니다. 아래 Python 직접 실행도 가능합니다.

Codex나 터미널에서 직접 실행하는 재현 예시는 다음과 같습니다. 아래 `area-results-01`이 이미 있으면 `area-results-02`처럼 새 이름을 사용합니다.

```powershell
python -m venv tools/.area-venv
tools/.area-venv/Scripts/python.exe -m pip install -r tools/requirements.txt
tools/.area-venv/Scripts/python.exe tools/area_extract.py area-lab/inputs/25B.ifc --out area-results-01
tools/.area-venv/Scripts/python.exe tools/area_extract.py area-lab/inputs/A32-05.ifc --out area-results-02
```

macOS/Linux에서는 `python3 -m venv tools/.area-venv` 후 실행 경로를 `tools/.area-venv/bin/python`으로 바꿉니다.

결과 폴더의 `review.html`을 브라우저로 엽니다. `objects.csv`에는 `inputfile, GUID, class, storey, basis, area, unit, limitations`와 추적용 이름·분류·타입 GUID·원본 SHA가 있습니다. `floors.csv`는 층별 합집합, `unit-slabs.csv`는 A32 등록 세대별 소속 슬래브 합집합입니다. 값이 없는 공간 면적은 공란입니다.

## Excel

[검증된 예제 XLSX](../area-lab/example-output/IFC-area-review.xlsx)를 먼저 열어 표의 구조를 확인합니다. 새 계산의 CSV는 Excel의 **데이터 → 텍스트/CSV에서**로 불러옵니다. 파일 원본은 UTF-8, 구분 기호는 쉼표로 선택하고 `storey`와 GUID 열은 텍스트로 가져옵니다. `area` 열은 숫자입니다. CSV를 더블클릭하면 `05`가 `5`로 바뀔 수 있으므로 가져오기를 권합니다.

예제의 `Area review`는 모델 면적 요약, `IFC objects`는75행 관측 원장, `Unit slabs`는14세대 근거, `Source dimensions`는 원본 A32 25형 도면 치수의 별도 산식입니다. `Source dimensions`의 노란 폭·높이 입력을 바꾸면 면적이 재계산됩니다. 모델 IFC가 바뀌면 CSV를 다시 추출해야 하며, 예제 XLSX가 IFC를 실시간 연결한 것은 아닙니다.

## 도구 범위와 자동검사

수직 압출된 다각형 단면을 실제 배치 좌표로 변환해 XY 합집합을 계산하며 구멍을 보존합니다. 타입 정의를 합계에 넣지 않습니다. 원본 IFC를 저장하지 않고 실행 전후 SHA256을 비교합니다. 기존 결과 폴더 덮어쓰기, 같은 입력 중복, 겹치는 입력의 GUID 중복을 거절합니다. 미지원 원호·경사 단면·메시는 이유를 표시하고 중단합니다. 알려진 A32 미세 조각의 표시 메시 오류를 피해 원래 유효 압출 단면을 사용합니다.

```powershell
tools/.area-venv/Scripts/python.exe -m unittest discover -s tools -p test_area_extract.py -v
```

실제 25B·05 입력의 층/공간/슬래브 수, 저장본 읽기 전용, IFC 공간 누락과0의 구분, 과거 독립 산출값과 합계 일치, 중복 및 미지원 형상 거절을 검사합니다. `build_area_example.mjs`는 강사용 XLSX 저작 소스이며 수강생 실행에는 필요하지 않습니다. 예제는 번들 artifact-tool로 저작·재계산·렌더 검토했고 Excel 데스크톱에서 직접 재계산한 검증은 하지 않았습니다.
