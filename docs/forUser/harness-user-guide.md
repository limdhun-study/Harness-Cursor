# 하네스 사용자 가이드 (실행 절차·저장소 설명)

**정책:** [forAgents/harness-policy.md](../forAgents/harness-policy.md) · **자격 증명:** [SettingGuide/02-cursor-credentials.md](SettingGuide/02-cursor-credentials.md) · **CLI 설치:** [SettingGuide/01-cli-install.md](SettingGuide/01-cli-install.md)

작업 전 루트 [AGENTS.md](../../AGENTS.md) 를 읽는다.

---

## 빠른 시작: 프롬프트 파일 · `harness.config.json` · 실행 명령

커밋된 기본값 그대로 따라 할 때의 흐름이다. (경로·파일명은 필요 시 바꿀 수 있다.)

1. **과제 마크다운 (`prompts/`)** — 1라운드와 검증 실패 후 연속 라운드용 템플릿이 있다. 저장소 기본 구성에서는 **`prompts/01-create-react-query-webapp.md`** 와 **`prompts/02-repair-from-validation-log.md`** 를 쓴다. 과제를 바꾸면 새 `.md`를 두거나 위 파일 내용을 고친다.
2. **`harness.config.json`** — **`initial_prompt_file`**, **`repair_prompt_file`** 에 1번 파일들의 **저장소 루트 기준 상대 경로**를 적어 연결한다. 루프를 다른 JSON으로 돌리려면 실행 시 **`--config 경로.json`** 을 붙인다(형태 검증은 커밋된 `harness.config.json`만).
3. **CLI·인증** — `agent` 가 `PATH`에 있어야 한다. 설치는 [SettingGuide/01-cli-install.md](SettingGuide/01-cli-install.md), 키·로그인은 [SettingGuide/02-cursor-credentials.md](SettingGuide/02-cursor-credentials.md). 루트 **`.env`** 에 `CURSOR_API_KEY` 등을 두면 `harness_cli_loop.py`가 자식 `agent`에 넘기기 쉽다(커밋 금지).
4. **하네스 루프 실행** — 저장소 루트에서 **`python3 scripts/harness.py loop`** . Windows에서는 **`python`** 일 수 있다. 2번에서 다른 JSON을 썼다면 **`python3 scripts/harness.py loop --config 그파일.json`** .
5. **검증만**(에이전트 없이) — **`python scripts/validate.py`** ; 웹 앱 스캐폴드까지 게이트면 **`python scripts/validate.py --web-app`** .

**기본값 그대로일 때 입력 예시(저장소 루트에서 실행)** — `harness.config.json`이 이미 `prompts/01-create-react-query-webapp.md` · `prompts/02-repair-from-validation-log.md` 를 가리키므로, 과제를 바꾸지 않았다면 JSON을 수정하지 않아도 된다.

```bash
# Linux / macOS (Python 3가 python3 인 경우)
python3 scripts/harness.py loop
```

```powershell
# Windows PowerShell (보통 python 으로 실행)
cd C:\path\to\Harness-Cursor
python scripts\harness.py loop
```

에이전트·검증 없이 명령만 확인:

```bash
python scripts/harness_cli_loop.py --dry-run
```

검증만(에이전트 없음):

```bash
python scripts/validate.py
python scripts/validate.py --web-app
```

아래 §2부터는 **하네스 루프**와의 구분, PowerShell에서의 PATH, 필드 표 등 **상세**다.

---

## 1. 한 줄 요약

본인 머신에서 돌아가는 **하네스 프로세스**가 로컬 워크스페이스에 대해 **`agent -p`** 를 실행한 뒤 **`python scripts/validate.py`** 를 실행한다. 루프 안에서는 **`web_app_validate`가 참일 때만** 그 한 줄이 **`validate.py --web-app`** 으로 바뀐다. 그 외 **프롬프트 조립·라운드 수·수리 템플릿 동작은 동일**하다.

### 이 저장소가 고정하는 것과, 예시로만 두는 것

- **고정(하네스 패턴):** JSON 필드 의미, `agent -p` 호출 후 검증 한 번, 실패 시 **`repair_prompt_file`** 에 검증 로그 끼우기, 공식 게이트 진입점 **`scripts/validate.py`** .
- **예시·교체 대상:** `prompts/` 과제 문구(커밋 기본은 웹 스캐폴드 과제 **샘플**), **`--web-app`** 은 “npm 빌드까지 검증에 넣을지”에 대한 **선택적 검증 프로필**일 뿐이다. 백엔드·문서·다른 스택 과제로 바꾸려면 **md를 새로 쓰거나 고치고**, JSON의 **`initial_prompt_file`·`repair_prompt_file`** 만 맞추면 된다.
- **여러 쓰임:** 팀마다 다른 조합을 **`--config 팀용.json`** 으로 두거나, 수동으로 **`validate.py`** / **`validate.py --web-app`** 을 골라 실행한다. 저장소 게이트만으로 부족하면 **`validate.py`에 검사를 추가**하거나 별도 스크립트를 두고 호출하도록 확장하면 된다.

---

## 2. 하네스 루프

이 문서에서 **하네스**는 **`python scripts/harness.py loop`** 로 돌아가는 **`harness_cli_loop.py`** 오케스트레이션을 가리킨다.

- 사용자는 라운드마다 **`agent` 대화창에 입력하지 않고**, 한 번 루프 명령을 실행한다(`python3`/`python` 등은 환경에 따름).
- Python이 **`harness.config.json`**(또는 **`--config`** 로 준 다른 JSON)과 **`prompts/*.md`** 를 읽고, 매 라운드 **`subprocess`로 `agent -p "…"`** 를 호출한 뒤 같은 프로세스에서 **`validate.py`** 를 실행한다.
- 루프 시작 시 저장소 루트에 **`.env` 파일이 있으면** 키=값을 환경 변수에 넣는다(**이미 설정된 변수는 덮어쓰지 않음**). 예: **`CURSOR_API_KEY`** 를 `.env`에 두면 자식 `agent` 프로세스가 상속한다.

### 루프를 쓰지 않을 때

Cursor IDE 채팅이나 터미널 **`agent`** 만 쓰고 위 Python 루프는 돌리지 않을 수 있다. 그때 **`prompts/`** 는 참고·복사용일 뿐이고, **`python scripts/validate.py`**(필요 시 **`--web-app`**)는 작업 단위마다 **직접** 실행하면 된다. 이건 IDE에서 흔히 쓰는 작업 방식이며, **`harness_cli_loop.py`가 에이전트를 대신 호출하는 구조가 아니다.**

---

## 3. 운영 원칙: 채팅은 허용, “중요 변경”은 하네스로

이 저장소에서는 Cursor **에이전트 채팅**으로 분석·설계를 해도 되고, **본 과제 실행**은 **`python3 scripts/harness.py loop`** 로 묶는 것을 기본으로 한다. 루프는 `max_rounds`와 `validate.py`로 **정해진 파이프라인을 반복**한다.

---

## 4. Windows에서 검증만 할 때와 루프(`agent` 필요)

- **`python scripts/validate.py`** 만: Windows에 Python만 있으면 PowerShell에서 실행 가능(`agent` 불필요).
- **`harness.py loop`**: **`PATH`에서 `agent`** 를 찾는다. [SettingGuide/01-cli-install.md](SettingGuide/01-cli-install.md) 대로 **Cursor CLI를 Windows에 네이티브 설치**한 뒤, **같은 PowerShell**에서 `agent --version` 과 `python` 이 함께 보이게 한다.

---

## 5. 작업 시작과 「명령 주입」정리

| 구분 | 작업 시작 | 명령·프롬프트는 어디에 넣나 |
|------|-----------|------------------------------|
| **하네스 루프** | `prompts/` 에 과제 md → JSON에서 경로 지정 → **`python3 scripts/harness.py loop`** (다른 설정은 `--config …`) | md·JSON이 소스이고 Python이 `agent -p` 인자로 넘김. |
| **IDE·터미널만 (루프 미사용)** | Cursor 채팅 또는 터미널 `agent` | 채팅·터미널 입력. 검증은 **`validate.py`** 를 직접 실행. 하네스 스크립트와 무관. |

---

## 6. Cursor CLI 설치·인증

- 설치: [SettingGuide/01-cli-install.md](SettingGuide/01-cli-install.md) · 설치 후 `agent --version`.
- 인증: [SettingGuide/02-cursor-credentials.md](SettingGuide/02-cursor-credentials.md) (`agent login` 또는 **`CURSOR_API_KEY`**). 루프 실행 시 **루트 `.env`** 에 키를 두면(커밋 금지) `harness_cli_loop.py`가 로드해 **`agent` 자식 프로세스에 전달**하기 쉽다.

---

## 7. 하네스 JSON 설정

비밀값 **이름**만 공유할 때는 루트 **`.env.example`** 을 쓰고, 실제 값은 **`.env`** 에 둔다(커밋 금지). 하네스 설정 파일은 **`harness.config.json`** 이며 API 키를 넣지 않는다. **`python scripts/validate.py`** 는 이 파일이 있는지와 **`agent_command`·`workspace_relative`·`web_app_validate` 등**이 기대하는 형태인지 검사한다.

다른 파일로 루프를 돌리려면 **`python scripts/harness.py loop --config 경로.json`** 이다. **`validate.py`가 형태를 검사하는 것은 커밋된 `harness.config.json`** 뿐이다(다른 JSON은 실행 시 선택).

| 필드 | 의미 |
|------|------|
| `agent_command` | 실행 파일 이름(기본 `agent`). |
| `workspace_relative` | `--workspace` 에 넘길 저장소 기준 상대 경로. |
| `trust_workspace` | 참이면 비대화형 실행에 `--trust` 추가. |
| `headless_model` | 선택. `--model` 값. |
| `headless_extra_args` | 추가 CLI 인자(문자열 배열). |
| `web_app_validate` | 참이면 매 에이전트 호출 뒤 `validate.py --web-app` 실행. |
| `max_rounds` | 에이전트→검증 사이클 상한. |
| `initial_prompt_file` | **1라운드 전용.** 파일 전체가 그대로 `agent -p` 인자로 넘어간다. 여기에 **과제 전체**(요구 범위·스택·금지 사항 등)를 쓴다. 이 저장소 기본값은 웹 앱 스캐폴드 과제 예시다. |
| `repair_prompt_file` | **2라운드부터** 사용한다. 1라운드 직후 `validate.py`가 실패하면, 그 **직전 라운드 검증 출력**이 이 마크다운 안의 **`<<<HARNESS_VALIDATION_LOG>>>`** 자리에 꽂히거나(없으면 템플릿 뒤에 덧붙는다). 즉 **고정된 지침 + 최신 검증 로그** 조합으로 “실패 원인 보고 고치기”를 반복한다. 과제 본문은 보통 `initial`에 두고, 여기에는 **로그 해석·수정 원칙·보고 형식**처럼 라운드마다 재사용할 틀을 둔다. |
| `prompt_out_dir` | 라운드별 프롬프트·검증 텍스트 산출물을 두는 디렉터리(예: `.harness/out`). |

---

### 라운드와 두 프롬프트 요약

| 라운드 | 쓰는 파일 | 내용 |
|--------|-----------|------|
| 1 | `initial_prompt_file` | 과제 설명만(검증 로그 없음). |
| 2 이상 | `repair_prompt_file` | 템플릿 + **직전에 실패한** `validate.py` 출력. 검증 통과 시 루프 종료. |

`max_rounds` 안에서 검증이 통과하지 않으면 같은 `repair_prompt_file` 패턴으로 반복된다.

---

### 검증 두 갈래: 기본 게이트와 웹 앱 게이트 (`web_app_validate` · `--web-app`)

이 절은 **“웹 전용 하네스”를 정의하지 않는다.** 다만 공식 스크립트에 이미 들어 있는 **두 가지 검증 진입점**(가벼운 저장소 게이트 vs npm 빌드 포함) 중 루프가 어느 쪽을 부를지만 적어 둔다.

하네스 루프(`harness_cli_loop.py`)는 **매 라운드마다 에이전트 실행 직후 검증을 한 번** 돌린다. 이때 **`harness.config.json`의 `web_app_validate`** 가 **어떤 검증 명령 한 줄을 쓸지**만 고른다. (`validate.py` 한 줄이 “두 번” 도는 게 아니라, **같은 자리에서 서로 다른 검증 스크립트로 분기**한다.)

| `web_app_validate` | 루프 안에서 실제로 도는 명령 | 전제 | 검증 대상(요약) |
|--------------------|------------------------------|------|------------------|
| **`false`** (이 저장소 커밋 기본) | **`python scripts/validate.py`** (플래그 없음) | 주로 **Python**만 있으면 됨 | 필수 파일 존재, **`harness.config.json` 형태**, `scripts/*.py` 컴파일 등 **하네스·저장소 스캐폴드** |
| **`true`** | **`python scripts/validate.py --web-app`** → 내부적으로 **`scripts/validate_web_app.py`** | **`node`·`npm`**, 루트 **`package.json`** | 의존성·TS/TSX·React Query 패턴, **`npm ci` 또는 `npm install`**, **`npm run build`** 등 **프론트 빌드 파이프라인** |

**`--web-app`의 의미:** `validate.py`가 같은 진입점이지만, 이 플래그가 켜지면 **웹 전용 게이트**로 넘긴다. 웹 게이트는 Node/npm이 없거나 `package.json`이 없으면 실패한다.

**커밋되는 `harness.config.json`은 `web_app_validate`가 반드시 `false`여야** `python scripts/validate.py`(기본 게이트)를 통과한다. 의도는 **클론 직후·CI에서 아직 웹 스캐폴드가 없어도** 저장소 자체는 검증 가능하게 두는 것이다.

**`true`를 쓰는 경우:** 루트에 이미 React/Vite 등 웹 앱이 있고, **매 에이전트 라운드마다 npm 설치·프로덕션 빌드까지** 묶어 확인하고 싶을 때다. 이때는 Node 환경이 갖춰져 있어야 한다. 팀·로컬에서만 쓰는 JSON을 만들어 **`python scripts/harness.py loop --config 그파일.json`** 으로 돌릴 수 있다. **형태 검증은 여전히 커밋된 루트 `harness.config.json`만** 받는다는 점은 변하지 않는다(가이드 §7 앞문단).

**루프 밖(수동):** 웹 작업 중에는 에이전트와 무관하게 **`python scripts/validate.py --web-app`** 을 직접 자주 실행하는 것이 일반적이다. 기본 게이트만 보려면 플래그 없이 **`python scripts/validate.py`** .

---

## 8. 하네스 루프 작업 순서

1. **`prompts/`** 에 과제를 마크다운으로 적는다.
2. 설정 JSON에서 **`initial_prompt_file`**, **`repair_prompt_file`** 에 저장소 루트 기준 상대 경로를 적는다.
3. **`prompts/…md` 를 셸에서 실행하지 않는다.** 내용은 Python이 읽는다.
4. **`agent`가 PATH에 있는 셸**에서 저장소 루트로 이동 후:

```bash
cd /path/to/Harness-Cursor
python3 scripts/harness.py loop
```

다른 설정 파일을 쓸 때만 **`python3 scripts/harness.py loop --config 팀용설정.json`** 처럼 **`--config`** 를 붙인다. 생략하면 항상 루트 **`harness.config.json`** 을 읽는다.

---

## 9. 검증만(에이전트 없음)

```bash
python scripts/validate.py
python scripts/validate.py --web-app
```

또는 `python scripts/harness.py validate` / `validate --web-app`.

**루프와의 관계:** 에이전트 루프가 매 라운드 끝에 위 둘 중 **어느 쪽을 돌릴지**는 `harness.config.json`의 **`web_app_validate`** 로만 정해진다. 분기 조건·전제·커밋 JSON 규칙은 **§7** 아래 **「검증 두 갈래: 기본 게이트와 웹 앱 게이트」** 를 본다.

---

## 10. CLI 참고

§8과 동일한 명령. 에이전트·검증 없이 확인만 할 때: **`python scripts/harness_cli_loop.py --dry-run`**.

---

## 11. 산출물

`prompt_out_dir` 아래에 `round_01_prompt.md`, `round_01_validate.md` 등이 생긴다. 이슈 보고·다음 프롬프트 작성 시 참고한다.

---

## 12. 저장소·파일 설명

**1차 인덱스:** 루트 [README.md](../../README.md) 의 문서 표.

### 루트

| 경로 | 상세 |
|------|------|
| **`README.md`** | 프로젝트 한 줄 설명과 **용도별 문서 1차 인덱스**. 실행 절차는 이 문서(앞부분)를 본다. |
| **`AGENTS.md`** | 코딩 에이전트·기여자 규칙(검증 명령, 비밀값 금지 등). **필독**. |
| **`harness.config.json`** | 하네스 JSON **기본값**(커밋됨). `validate.py`가 형태를 검증한다. |
| **`.env.example`** | 환경 변수 **이름·더미값**만. 실제 키는 넣지 않는다. |
| **`.gitignore`** | `.env`, `.harness/`, `node_modules/` 등. **`harness.config.json`은 커밋**된다. |

### `scripts/`

| 경로 | 상세 |
|------|------|
| **`validate.py`** | 공식 검증 진입점. 기본: 하네스 스크립트·필수 문서·`harness.config.json` 규칙·`scripts/*.py` 컴파일. `--web-app`이면 `validate_web_app.py` 실행. |
| **`validate_web_app.py`** | 웹 앱 전용 게이트(`npm install` / `npm run build` 등). |
| **`harness_cli_loop.py`** | 하네스 루프 본체. `.env` 로드 후 `agent -p` → **`validate.py`(플래그 없음) 또는 `--web-app`** (`web_app_validate` 참조), 실패 시 수리 프롬프트로 재시도. |
| **`harness.py`** | `validate` / `loop` 위임 래퍼. |

### `docs/`

| 경로 | 상세 |
|------|------|
| **`forUser/`** | 운영자·기여자용: SettingGuide, **이 가이드**. |
| **`forUser/SettingGuide/`** | `01-cli-install.md`, `02-cursor-credentials.md`. |
| **`forAgents/`** | 에이전트 규범: `harness-policy.md` 등. |

### `prompts/`

작업 템플릿(`01-…`, `02-…`). 하네스 JSON의 `initial_prompt_file` / `repair_prompt_file` 로 라운드에 넣을 수 있다.

### `.cursor/`

`rules/*.mdc`, `skills/`, `agents/` — IDE·에이전트 보조 메타.

### 기타

| 경로 | 상세 |
|------|------|
| **`.harness/out/`** (로컬) | 라운드 산출물. `.gitignore`. |
