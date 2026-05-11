---
name: harness-engineering
description: Cursor CLI 헤드리스 하네스 루프를 계획·실행·복구하고 로컬 검증 게이트를 통과시킬 때 사용한다.
---

# Harness Engineering 스킬

이 저장소에서 **Cursor CLI 헤드리스** 흐름을 다룰 때 쓴다. **`scripts/harness_cli_loop.py`** 가 **`agent -p`** 를 호출한 뒤 **`scripts/validate.py`** 를 실행한다. 정책은 **`docs/forAgents/harness-policy.md`**, 명령·절차·파일맵은 **`docs/forUser/harness-user-guide.md`** 에 있다.

## 쓰는 경우

- `prompts/` 아래 **라운드 프롬프트** 작성·조정
- **`harness.config.json`** — 커밋된 기본 설정. `validate.py` 검증 대상. 덮어쓰기는 **`--config 다른파일.json`**.
- 실패 후 **`.harness/out`** 라운드 산출물 해석
- **CLI 하네스**와 Cursor 다른 진입점(에디터 등)의 차이 설명

## 표준 절차

1. **`AGENTS.md`**, **`docs/forAgents/harness-policy.md`** 를 읽는다.
2. **`agent`** 설치([`docs/forUser/SettingGuide/01-cli-install.md`](../../../docs/forUser/SettingGuide/01-cli-install.md)) 및 인증([`02-cursor-credentials.md`](../../../docs/forUser/SettingGuide/02-cursor-credentials.md))을 확인한다.
3. 저장소 변경 후 **`python scripts/validate.py`** 를 실행한다. React 스캐폴드를 건드리면 **`--web-app`** 을 쓴다.
4. 자동 라운드는 **`python scripts/harness.py loop`**. **`--config`** 로 다른 JSON을 지정할 수 있다.
5. 실패 시 **`round_XX_validate.md`** 내용이 다음 수정 프롬프트 입력이 된다(루프 스크립트가 자동 처리).

## 재시도 정책

- **바깥 스크립트**가 `max_rounds` 로 상한을 둔다. 모델이 “끝없이 계속” 하도록 덮어쓰지 않는다.
- 라운드당 **한 덩어리의 수정**을 선호하고, 실패한 **검증기 출력**을 다음 반복에 붙인다.

## 완료 보고

**`AGENTS.md`** 와 같이: 변경 파일, 실행한 명령, PASS/FAIL, FAIL이면 짧은 다음 수정안.
