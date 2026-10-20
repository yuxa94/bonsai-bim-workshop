# 04 · 복사해서 쓰는 짧은 요청 모음

`{WORKSHOP_ROOT}`를 실제 수업 폴더로 바꾸고 입력 파일을 지정합니다. 이 문서의 요청은 **로컬 Blender MCP와 CAD 해석 도구가 연결된 앱**에서 실행합니다. 브라우저의 일반 ChatGPT 대화만으로 PC의 DWG와 Blender에 접근할 수 있는 것은 아닙니다. 실행하지 못한 단계는 제공 예제 검토로 구분해 기록합니다.

## 연결과 설치

```text
현재 Blender MCP 연결을 읽기 전용으로 확인하고 버전·장면·객체 수·현재 IFC 경로를 알려줘.
그다음 공식 안정판 안내로 Bonsai를 설치하고,
같은 Blender 내부에서 ifcopenshell import와 버전·모듈 경로를 확인하게 도와줘.
연결 오류와 설치 오류를 나눠 기록하고 다른 창은 유지해줘.
```

설치 상세: [01 연결·설치](01-connect-and-install.md)

## 25B 처음 만들기

```text
25B-v003.dwg로 첫 단위세대 IFC를 만들어줘.
원본을 보존하고 단위·WCS·미러·벽·문창·FL/SL을 먼저 조사해줘.
필수 미표기 높이를 확인받은 뒤 새 IFC를 작성해줘.
완성 예제 스킬부터 설치하지 말고 이번 도면으로 직접 진행해줘.
평면·입체·주요 치수·IFC 재열기로 검증하고 근거와 미확정 항목을 남겨줘.
```

## 현재 모델 고치기

```text
현재 IFC를 보존하고 WIN03 두 열 창틀·싱크 상판 개구·샤워문 방향을 원본과 대조해줘.
수정 대상을 GUID로 기록하고 해당 항목만 새 버전에서 고쳐줘.
저장 IFC의 실제 상세 치수와 대상 외 형상 보존을 확인해줘.
```

## 첫 성공을 내 스킬로

```text
$skill-creator 방금 성공한25B 작성·상세 수정·검증 과정을 my-unit-bim으로 정리해줘.
다음 도면에도 쓸 판단 규칙과25B 전용 값을 나누고,
{WORKSHOP_ROOT}/my-skills/my-unit-bim/SKILL.md에 써줘.
작성 후 제공 completed 예제와 비교하고 현재 앱의 개인 스킬 경로에 등록해줘.
```

## 54B에 적용

```text
$my-unit-bim 54B-v003.dwg로 두 번째 단위세대를 만들어줘.
25B를 유지하고 별도 작업 폴더와 세션에서 진행해줘.
54B의 치수·벽 레이어·문창·높이 근거를 다시 확인하고,
재사용 부재는54B에 맞춰 IFC 형상으로 조정해 새 GUID로 배치해줘.
```

## 실제 기준층 작성·수정

```text
$my-unit-bim A32-5-23F.dwg의 실제14세대 기준층 한 층을 IFC로 만들어줘.
세대 INSERT·미러·공용부·계단·승강기와 단면 치수 근거를 확인해줘.
먼저 한 층을 저장·대조하고 현재 파일에서 문 상부벽과 계단 상세를 수정해줘.
다른 층 적층은 기준층 검증 뒤에 진행해줘.
```

## 층별 스킬과 다른 층

```text
$skill-creator 기준층의 실제 성공 기록으로 my-floor-bim을 만들어줘.
타입·배치형·공용부·층 레벨·새 GUID·한 층 예외·층별/통합본 대응을 포함해줘.
그 스킬을 사용해 일반층 하나와 다른24층을 새 도면 근거로 구성하고 검증해줘.
```

## 면적표를 도면과 연결

```text
저장 IFC를 읽기 전용으로 분석해 모델 면적표를 만들어줘.
공간 형상·수량 유무를 먼저 확인하고 가능한 기하와 경계를 명시해줘.
층별 중복을 합집합으로 제거하고 도면·번호·치수·산식·GUID와 표를 연결해줘.
원본 산식과 모델 경계가 다르면 분리하고 미확정 법정 면적·단가를 임의 확정하지 마.
```

## 공개 예제 가져오기: 첫 작성 뒤 비교용

강의 페이지의 다운로드 링크 또는 아래 공개 MD를 사용합니다. 로컬 압축본에는 `skill-kits/`가 있으므로 인터넷 없이 비교할 수 있습니다. 공개 저장소 배포가 완료되기 전에는 로컬 압축본을 기준으로 사용합니다.

- [단위세대 완성 스킬 MD](https://raw.githubusercontent.com/yuxa94/bonsai-bim-workshop/main/skill-kits/completed/unit-bim/SKILL.md)
- [층별 완성 스킬 MD](https://raw.githubusercontent.com/yuxa94/bonsai-bim-workshop/main/skill-kits/completed/floor-bim/SKILL.md)

배포 경로의 `unit-bim`·`floor-bim`은 자료 분류명입니다. 완성 MD 안의 YAML 이름은 각각 `workshop-unit-bim`·`workshop-floor-bim`입니다. 비교는 파일 경로로 요청하고, 별도 등록 폴더와 호출 이름은 YAML 이름에 맞춥니다. 학생이 작성한 `my-unit-bim`·`my-floor-bim`과 구분해 보관합니다.

```text
내가 직접 작성한 단위세대/층별 스킬과 수업자료의
skill-kits/completed/unit-bim/SKILL.md,
skill-kits/completed/floor-bim/SKILL.md를 비교해줘.
내 성공 기록으로 확인된 규칙 중 빠진 부분만 제안하고,
확인하지 않은 기능이 완성됐다고 추가하지 마.
기존 개인 스킬 전체나 앱 설정·인증 파일을 복사하지 마.
```

개인 작성본을 비교한 뒤 공개 예제를 별도로 등록하려면 다음처럼 요청합니다.

```text
아래 공개 스킬 MD를 먼저 읽고 적용 범위와 수행할 작업을 확인해줘.
https://raw.githubusercontent.com/yuxa94/bonsai-bim-workshop/main/skill-kits/completed/unit-bim/SKILL.md
지금 앱의 개인 스킬 경로를 확인해 YAML name인 workshop-unit-bim 폴더로 등록해줘.
내가 작성한 my-unit-bim과 기존 동명 스킬은 보존해줘.
받을 수 없으면 성공으로 처리하지 말고 수업 압축본의 같은 파일을 사용해줘.
```

각 요청의 상세 절차와 제출 증거: [02 단위세대·스킬](02-first-unit-and-personal-skill.md), [03 기준층·면적표](03-floor-reuse-and-area.md)
