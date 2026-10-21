# 01 · Blender를 MCP에 연결하고 BIM 도구 설치하기

수업은 **Blender를 이미 내려받은 상태**에서 시작합니다. 연결 → 읽기 전용 확인 → Bonsai 설치 → IfcOpenShell 확인 순서로 진행합니다. 설치 확인일은 2026-10-21이며, 수업 당일에는 아래 공식 링크의 안정판과 호환 버전을 다시 확인합니다.

`{WORKSHOP_ROOT}`는 수강생이 이 자료를 풀어 둔 폴더입니다. 예제 문장의 토큰은 실제 경로로 바꿔 입력합니다. 공개 예제 주소는 강의 페이지의 다운로드 링크를 사용하고, 내려받은 압축본은 로컬에서 사용할 수 있습니다.

## 도구가 맡는 일

| 구성 | 수업에서 하는 일 | 결과로 확인할 것 |
|---|---|---|
| GPT가 실행되는 도구 연결형 앱 | 자연어를 작업 순서와 Python 호출로 바꿈 | 수행한 도구·코드와 확인 결과 |
| MCP | 앱이 Blender의 기능을 부를 수 있게 연결 | 실제로 응답한 Blender의 버전·장면 |
| Blender | 형상을 표시하고 편집 | 3D 화면·객체·좌표 |
| Bonsai | Blender 안에서 IFC 프로젝트를 열고 BIM을 작성 | IFC 클래스·층 소속·속성·Save IFC |
| IfcOpenShell | IFC 데이터를 읽고 쓰고 형상을 계산 | IFC 파일·GUID·형상 검사 |
| Skill | 검증한 작업 요령을 다시 사용할 지침으로 보관 | `SKILL.md`와 실제 재적용 결과 |

MCP 연결에 Bonsai가 먼저 필요한 것은 아닙니다. 먼저 일반 Blender 연결을 확인하면 이후의 오류가 연결 문제인지 BIM 설치 문제인지 구분할 수 있습니다. 일반 채팅 화면에 프롬프트를 붙였다는 사실만으로 로컬 Blender 연결이 만들어지지는 않습니다.

## 0. 표지 다음 페이지에서 Codex에 설치 맡기기

표지 다음인 강의 2페이지의 **요청 복사**를 누르고 실습 폴더를 연 Codex에 붙여넣습니다. 이 요청은 설치 안내에서 멈추지 않고, 실행 가능한 설치와 검증까지 맡기는 용도입니다. 다운로드가 시작되면 다음 페이지로 넘어가 개념 설명을 들으세요. MCP가 아직 연결되지 않았어도 사용 가능한 로컬 터미널 작업부터 진행하도록 요청합니다. 실제 권한·클릭·재시작이 필요한 단계는 Codex가 알려주는 대로 진행합니다.

설치 대상은 Blender의 Bonsai와 그에 포함된 IfcOpenShell, 그리고 마지막 면적산출 실습에 사용할 별도 Python 가상환경의 `ifcopenshell`입니다. 공식 안정 배포처와 Blender 내부 Python 호환을 확인합니다. Blender의 포함 모듈을 외부 pip로 덮어쓰지 않습니다. 기존 환경이 정상이면 재사용하고, 가상환경 생성 전 같은 이름의 기존 환경과 Python 실행 파일을 확인합니다. 별도 환경 설치는 해당 환경의 Python으로 `-m pip install ifcopenshell`을 실행합니다.

프롬프트는 [설치 요청 페이지](https://yuxa94.github.io/bonsai-bim-workshop/#2) 또는 [요청문 모음](../prompts.txt)의 첫 항목에서 복사할 수 있습니다. 실제 설치 결과·버전·모듈 경로와 남은 단계는 `work/setup-check.md`에 기록합니다. 이어지는 MCP 연결 실습은 수업용 Blender에서 진행합니다.

## 1. 일반 Blender MCP 연결

Blender ZIP을 내려받았다면 압축을 풀고 실행 파일로 한 번 엽니다. 설치 프로그램을 내려받았다면 설치를 마치고 엽니다. 수업 중 기존 모델이 있는 창은 그대로 두고 수업용 창을 준비합니다.

이 과정은 외부 모델 생성 서비스 없이 로컬 Blender와 연결합니다. 공개 저장소 [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)는 현재 `mcp-for-blender`로 이동했으며, 신규 설치 패키지도 그 이름을 사용합니다. 기존 `uvx blender-mcp` 설정은 호환되므로 이미 정상 동작하는 설정은 수업 도중 바꿀 필요가 없습니다.

Windows PowerShell에서 다음을 한 줄씩 실행합니다. `uv`가 이미 있으면 첫 줄은 생략합니다.

```powershell
winget install --id=astral-sh.uv -e
```

새 PowerShell 창을 열어 실행합니다.

```powershell
uvx --version
uvx mcp-for-blender install-addon
```

설치기가 표시한 Blender 버전과 애드온 설치 위치를 확인합니다. Blender를 열고 **Edit → Preferences → Add-ons**에서 `MCP for Blender`를 검색해 켭니다. 자동 탐지가 실패하면 공식 저장소의 `addon.py`를 내려받아 Add-ons의 **Install… / Install from Disk**로 설치합니다. Blender 버전에 따라 메뉴 표현이 다를 수 있습니다.

도구 연결형 앱의 MCP 설정에 서버 하나를 추가합니다.

| 설정 | 값 |
|---|---|
| 이름 | `blender` |
| 방식 | `STDIO` |
| 실행 파일 | `uvx` |
| 인수 | `mcp-for-blender` |

Codex CLI가 이미 있는 환경에서는 아래 명령으로 같은 서버를 등록할 수 있습니다. UI와 CLI 중 한 방법을 선택합니다.

```powershell
codex mcp add blender -- uvx mcp-for-blender
codex mcp list
```

앱을 완전히 종료한 뒤 다시 엽니다. Blender 3D Viewport에서 `N`을 눌러 **MCP for Blender** 탭을 확인합니다. 서버가 멈춰 있으면 **Start MCP Server**를 누릅니다. 처음에는 수업용 Blender 한 창으로 확인합니다. 여러 창을 쓰는 단계에서는 대상 포트를 각각 기록합니다. 설정 원리는 [공식 MCP 문서](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)와 [연결 도구 README](https://github.com/ahujasid/mcp-for-blender#quickstart)를 참고합니다.

**연결 확인 프롬프트**

```text
Blender MCP로 현재 연결된 Blender를 읽기 전용으로 확인해줘.
Blender 버전, 열린 blend 경로, 장면 이름, 객체 수를 알려줘.
아직 모델을 만들지 말고 화면 캡처도 보여줘.
도구가 연결되지 않았다면 성공으로 추정하지 말고 실패 단계와 원문 오류를 알려줘.
```

기대 결과는 실제 도구 응답과 현재 창이 일치하는 것입니다. 빈 `blend` 경로는 아직 저장하지 않은 새 장면일 수 있습니다. 등록 목록에 서버가 있다는 것만으로 Blender까지 연결되었다고 판단하지 않습니다.

## 2. Bonsai 안정판 설치

Blender에서 **Edit → Preferences → Get Extensions → Allow Online Access → Bonsai 검색 → Install**을 실행합니다. 설치 뒤 Add-ons에서 Bonsai가 활성화되어 있는지, File 메뉴에 **Open IFC Project**가 있는지 확인합니다. [Bonsai 안정판 설치 안내](https://docs.bonsaibim.org/studio/quickstart/installation.html)

확인 시점 공식 안정판 문서는 `0.9.0post1`입니다. 과거 실습의 Blender 4.4.0 / Bonsai py311 조합은 그때의 검증 환경입니다. 내려받은 Blender가 다른 버전이면 해당 버전이 지원되는지 확인한 뒤 설치합니다. 오프라인 ZIP이 필요하면 공식 배포 파일 중 OS·CPU·Blender 내 Python 버전에 맞는 **안정판**을 선택합니다. `latest`라는 주소나 더 큰 버전 번호만 보고 alpha/daily 빌드를 선택하지 않습니다.

**설치 도우미 프롬프트**

```text
연결된 수업용 Blender에 Bonsai 안정판을 설치하려고 해.
먼저 Blender 버전과 Blender 내부 Python 버전을 읽어줘.
공식 Bonsai 안정판 설치 안내와 호환되는 설치 경로를 확인해 실제 설치·활성화까지 진행해줘.
이미 설치되어 있으면 재설치 전에 버전·모듈 경로·활성 상태부터 확인해줘.
다른 Blender 창이나 기존 모델은 유지해줘.
```

## 3. IfcOpenShell은 Blender 안에서 확인

Bonsai에는 IfcOpenShell과 Python 사용 환경이 포함됩니다. 이 수업의 Blender 안 모델링에는 별도 시스템 Python 설치가 선행 조건이 아닙니다. Blender **Python Console** 또는 MCP의 Blender Python 실행으로 아래를 확인합니다. [IfcOpenShell의 Bonsai 사용 안내](https://docs.ifcopenshell.org/ifcopenshell-python/installation.html#using-bonsai)

```python
import bpy
import sys
import ifcopenshell
print("Blender:", bpy.app.version_string)
print("Python:", sys.version)
print("IfcOpenShell:", ifcopenshell.version)
print("Module:", ifcopenshell.__file__)
```

**확인 프롬프트**

```text
현재 MCP가 연결된 Blender 내부에서 bpy, bonsai, ifcopenshell을 import해줘.
Blender·Bonsai·IfcOpenShell 버전, Python 버전, 각 모듈 경로를 기록해줘.
IFC 열기와 Save IFC 기능을 사용할 수 있는지도 읽기 전용으로 확인해줘.
결과를 수업 폴더의 work/setup-check.md에 기록해줘.
```

`ModuleNotFoundError`가 나면 **어느 Python에서 발생했는지**부터 확인합니다. Windows의 `python`이나 MCP 서버용 `uvx` 환경에 설치한 패키지가 Blender에 자동으로 설치되는 것은 아닙니다. 우선 Bonsai 설치·활성 상태와 Blender 재시작 여부를 확인합니다.

수업 후 별도 터미널에서 IFC 일괄 분석을 할 때만 프로젝트용 가상환경을 따로 만들 수 있습니다. 그 환경의 Python 경로를 확인하고 그 실행 파일로 `-m pip install ifcopenshell`을 실행합니다. Blender의 임의 경로에 pip를 강제로 실행하거나, 시스템 Python 패키지를 Blender 폴더에 복사하는 방식은 이 수업의 기본 절차가 아닙니다. [IfcOpenShell 설치 방식](https://docs.ifcopenshell.org/ifcopenshell-python/installation.html)

## 연결 오류를 좁히는 순서

| 관측된 문제 | 먼저 확인할 항목 |
|---|---|
| `uvx`를 못 찾음 | 새 터미널에서 `Get-Command uvx`; 앱 실행 파일 설정에 확인된 절대 경로 사용 |
| MCP 등록은 있지만 응답이 없음 | Blender 애드온 활성·서버 실행·포트 일치·앱 재시작 |
| 다른 모델이 응답함 | 실제 Blender PID·포트·IFC 경로; 화면 제목만으로 판단하지 않음 |
| Bonsai 검색/다운로드 실패 | 온라인 접근·공식 저장소 접근·Blender 지원 버전 |
| IFC가 열리지만 이전 형상처럼 보임 | 현재 IFC 경로·저장 버전·blend 스냅샷 여부 |

완료 증거는 `work/setup-check.md`와 현재 화면입니다. 다음 단계는 [첫 단위세대와 개인 스킬](02-first-unit-and-personal-skill.md)입니다.
