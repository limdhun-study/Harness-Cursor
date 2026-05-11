# 에이전트 작업: 검증 실패 후 수정(CLI 하네스 라운드)

이전 라운드에서 **`python scripts/validate.py`** 또는 **`python scripts/validate.py --web-app`** 이 실패했다. 하네스가 이 라운드 프롬프트를 만들 때 아래 자리 표시가 있으면 캡처한 출력으로 치환하고, 없으면 템플릿 뒤에 로그를 붙인다.

## 먼저 읽을 파일

- `AGENTS.md`
- `docs/forAgents/harness-policy.md`
- `.cursor/rules`

## 실패 로그(하네스가 채움)

`scripts/harness_cli_loop.py` 가 자리 표시가 있으면 아래 블록을 검증 출력으로 바꾼다. 없으면 템플릿 다음에 로그를 덧붙인다.

```text
<<<HARNESS_VALIDATION_LOG>>>
```

## 수정 기준

- 실패 로그와 **직접 연관된 최소 변경**을 우선한다.
- 이 저장소 밖 파일은 수정하지 않는다.
- 런타임에 외부 CDN을 쓰지 않는다.
- 초기 웹 앱 과제의 TypeScript·React·TanStack Query 기대를 유지한다.
- 무제한 자체 재시도를 하지 말고, **한 라운드에 한 번에** 집중해 수정한다.

## 검증

수정 후, 실패했던 것과 **동일한** 명령으로 확인한다(하네스가 자동으로 다시 돌리기 전에 수동 작업이면 보고 전에 직접 실행).

```bash
python scripts/validate.py --web-app
```

(기본 하네스 게이트만 실패했다면 `python scripts/validate.py`)

## 보고 형식

[요약]

…

[변경 파일]

- …

[검증 명령]

```bash

```

[결과] PASS 또는 FAIL

[FAIL인 경우] 다음 하네스 라운드에 넣을 구체적 다음 수정안.
