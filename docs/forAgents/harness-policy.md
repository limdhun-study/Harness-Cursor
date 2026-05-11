# 하네스 정책(규범 본문)

**독자:** 에이전트와 운영자가 **같은 원칙**을 읽도록 한 문서다. **실행 절차**(CLI 설치, 환경 변수, 명령)는 [forUser/harness-user-guide.md](../forUser/harness-user-guide.md)에 있다.

## 이 파일의 역할

1. 루트 **`README.md`** 에 프로젝트 한 줄 설명과 **용도별 문서 1차 인덱스**가 있다. 실행·설정은 **`docs/forUser/`** 를 따른다.
2. **라운드·재시도·중단·검증 순서를 누가 통제하는지**를 밝힌다. 바깥 **하네스**가 담당하며, 에이전트 내부의 무제한 자체 반복은 금지한다.
3. **`scripts/*.py` 는 이 마크다운을 파싱하지 않는다.** JSON 설정과 셸·Python이 동작을 이끈다. 이 파일은 사람과 에이전트의 **인지 정렬**용이다.

## 오케스트레이션 모델(Cursor CLI)

외부 하네스(또는 사람이 루프 스크립트를 실행)가 다음을 수행한다.

1. 라운드마다 **하나의** 구현 또는 수정 과제를 에이전트에 준다(프롬프트 파일 + 선택적 검증 로그).
2. 저장소 워크스페이스에 대해 **Cursor Agent CLI**를 헤드리스로 실행한다([forUser/harness-user-guide.md](../forUser/harness-user-guide.md)).
3. **`python scripts/validate.py`** 를 실행한다(웹 앱 과제면 **`--web-app`**).
4. 실패 시 **실패 출력**을 다음 라운드 프롬프트(수정 템플릿)에 넣는다.
5. 사용 중인 하네스 설정 JSON(기본 `harness.config.json` 또는 `--config`로 지정한 파일)의 **`max_rounds`** 까지 반복한다(기본 **3**).
6. 최대 실패 후 중단하고 보고한다: diff 요약, 실패 원인, 다음 수동 조치.

### 스크립트 역할(요약)

- **`scripts/harness_cli_loop.py`** — 라운드별 프롬프트 작성, `agent -p …` 실행, `validate.py` 실행, `.harness/out`(또는 `prompt_out_dir`)에 산출물 기록.
- **`scripts/harness.py`** — `validate` → `validate.py`, `loop` → `harness_cli_loop.py` 로 위임하는 얇은 진입점.
- **`scripts/validate.py`** — 저장소 게이트. **`--web-app`** 이면 `validate_web_app.py` 로 위임.

## 원칙

- 상한 없이 “될 때까지” 재시도하라고 에이전트에게만 맡기지 않는다. 루프 스크립트가 **`max_rounds`** 를 강제한다.
- 각 에이전트 과제는 올바른 검증 명령을 실행하고 결과를 보고해야 한다.
- 제품 기능 세부는 **작업 프롬프트**(예: `prompts/`)에 두고, 이 정책 파일에 두지 않는다.
- 실패 로그는 **다음** 라운드 수정 프롬프트의 핵심 입력이다.
