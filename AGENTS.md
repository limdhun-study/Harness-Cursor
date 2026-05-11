# 에이전트 규칙

## 역할

이 저장소는 **Harness Engineering** 예이다. 바깥의 **Python 루프**가 **Cursor Agent CLI**를 헤드리스 모드(`agent -p`)로 호출한 뒤 **`python scripts/validate.py`** 를 실행한다. 라운드·중단·재시도용 프롬프트 조립은 **하네스 스크립트**가 담당하며, 모델에게 무한 반복을 지시하지 않는다.

규범 본문: [docs/forAgents/harness-policy.md](docs/forAgents/harness-policy.md). 실행·설정: [docs/forUser/harness-user-guide.md](docs/forUser/harness-user-guide.md). 문서 목차: [README.md](README.md).

## 목표

- 공식 게이트는 **`scripts/validate.py`** 를 유지한다.
- **CLI 오케스트레이션**은 **`scripts/harness_cli_loop.py`** (프롬프트 → `agent` → 검증 → 실패 시 수정 프롬프트)가 담당한다.
- 선택적으로 **`python scripts/harness.py`** 로 `validate` | `loop` 를 호출한다.
- 커밋된 **예시 프롬프트**가 웹 스캐폴드를 요구할 때만 TypeScript/React 등을 구현하고, 그 경우 **`python scripts/validate.py --web-app`** 으로 검증한다. 과제가 다르면 **`prompts/`·검증 게이트**를 그에 맞게 둔다.

## 제약

- 코드와 설정 파일은 **이 저장소 안**에만 둔다.
- 비밀값은 커밋하지 않는다. 로컬 **`.env`**(gitignore)는 [`.env.example`](.env.example) 을 참고한다.
- 웹 앱 런타임에서 외부 CDN에 의존하지 않는다.
- 필수 검증 명령을 실행하지 않고 완료라고 말하지 않는다.
- 무제한 재시도를 에이전트에게 맡기지 않는다. **`max_rounds`** 는 하네스가 통제한다.

## 검증

실질적인 변경 후:

```bash
python scripts/validate.py
```

웹 앱 스캐폴드를 다루는 작업이면:

```bash
python scripts/validate.py --web-app
```

## 완료 보고

1. 변경한 파일
2. 실행한 검증 명령
3. PASS 또는 FAIL
4. FAIL이면 원인과 다음 라운드에 넣을 구체적 수정안
