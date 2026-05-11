# Harness-Cursor

**하네스 엔지니어링**을 보여 주기 위한 예시 저장소다. **Cursor Agent CLI**(`agent -p`)를 라운드마다 호출하고, 매 회 **`python scripts/validate.py`** 로 묶는 흐름을 **`scripts/harness_cli_loop.py`** 와 루트 **`harness.config.json`** 이 고정한다. 라운드 상한·프롬프트 조립도 여기서 다룬다.

커밋된 **`prompts/`** 는 그 오케스트레이션을 설명하려고 넣은 **과제·수리 템플릿 예시**일 뿐이며(기본값이 웹 스캐폴드 과제일 뿐), 이 저장소를 “프론트엔드 전용 하네스”로 규정하지 않는다. **`--web-app` / `web_app_validate`** 는 **검증 한 줄이 기본 게이트냐 웹(npm 빌드) 게이트냐**만 갈라진다. 과제 문구·검증 규칙·추가 스크립트는 팀·상황에 맞게 **`prompts/`·`--config`·`validate.py` 확장**으로 바꾸면 된다.

## 작업 시작(사용자)

**가장 중요한 구분(하네스 루프 vs 루프 미사용, PowerShell에서 `agent` PATH, 명령 주입 위치)** 과 **프롬프트·JSON·실행 명령 한 줄 흐름**은 **[docs/forUser/harness-user-guide.md](docs/forUser/harness-user-guide.md)** 의 **빠른 시작**(복사용 명령 블록 포함)과 **§2~§5**에 정리되어 있다. 반드시 그걸 먼저 읽는다.  
특히 **“채팅은 분석/문서, 과제 실행은 하네스 루프”** 라는 점은 같은 문서 **§3**에 있다.

요약만 골라 쓰면:

- **하네스 루프** — 저장소 루트에서 PowerShell **`python scripts\harness.py loop`** · Unix/macOS **`python3 scripts/harness.py loop`** ([가이드 «빠른 시작»](docs/forUser/harness-user-guide.md)). `prompts/`·`harness.config.json`·`agent` PATH·루트 `.env` 등은 가이드 **§2·§4**.
- **검증만** — `python scripts/validate.py` vs `--web-app` 분기, 루프 안 `web_app_validate` 조건은 [가이드 §7·§9](docs/forUser/harness-user-guide.md). [AGENTS.md](AGENTS.md).
- **루프 없이 IDE·터미널만** — 채팅/`agent`만 쓰고 Python 하네스는 안 돌릴 때. **`validate.py`** 는 직접 실행. 상세는 가이드 **§2**.

## 문서 1차 인덱스(용도별)

| 용도 | 문서 |
|------|------|
| 사용자 — 실행 절차·저장소 설명(통합 가이드) | [docs/forUser/harness-user-guide.md](docs/forUser/harness-user-guide.md) |
| 사용자 — CLI 설치 | [docs/forUser/SettingGuide/01-cli-install.md](docs/forUser/SettingGuide/01-cli-install.md) |
| 사용자 — 인증(API 키·로그인) | [docs/forUser/SettingGuide/02-cursor-credentials.md](docs/forUser/SettingGuide/02-cursor-credentials.md) |
| 에이전트 — 규범(정책 본문) | [docs/forAgents/harness-policy.md](docs/forAgents/harness-policy.md) |
| 에이전트 — `forAgents` 안내 | [docs/forAgents/README.md](docs/forAgents/README.md) |
| 에이전트 — 행동 규칙(루트) | [AGENTS.md](AGENTS.md) |
