"""하네스 루프: Cursor Agent CLI 헤드리스 호출 후 validate.py 실행.

`PATH`에 `agent` 실행 파일이 있어야 한다(docs/forUser/SettingGuide/01-cli-install.md).
라운드 수·프롬프트 조립은 이 스크립트가 담당한다(에이전트 내부 무한 루프 아님).

저장소 루트 `.env` 가 있으면 KEY=VALUE 를 읽어 환경 변수에 넣는다(이미 설정된 키는 덮어쓰지 않음).
자식 `agent` 프로세스는 동일 환경을 상속하므로 `CURSOR_API_KEY` 등을 `.env` 로 둘 수 있다.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DEFAULT_CONFIG = ROOT / "harness.config.json"
LOG_PLACEHOLDER = "<<<HARNESS_VALIDATION_LOG>>>"


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _fail(msg: str) -> None:
    print(f"harness_cli_loop: {msg}", file=sys.stderr)
    sys.exit(2)


def _load_config(path: Path) -> dict:
    if not path.is_file():
        _fail(f"설정 파일 없음: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        _fail(f"{path} JSON 오류: {exc}")


def _resolve_config_path(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_absolute():
            p = ROOT / p
        return p
    return DEFAULT_CONFIG


def _read_text(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        _fail(f"프롬프트 파일 없음: {rel}")
    return path.read_text(encoding="utf-8-sig")


def _write_round_artifact(out_dir: Path, round_idx: int, name: str, body: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"round_{round_idx:02d}_{name}.md"
    path.write_text(body, encoding="utf-8")
    return path


def _build_repair_prompt(template: str, log_text: str) -> str:
    if LOG_PLACEHOLDER in template:
        return template.replace(LOG_PLACEHOLDER, log_text.strip() or "(검증 출력 없음)")
    return (
        template
        + "\n\n## 첨부 검증 출력\n\n```text\n"
        + log_text
        + "\n```\n"
    )


def _find_agent_stem_in_dirs(stem: str, dirs: list[Path]) -> str | None:
    for dir_path in dirs:
        if not dir_path or not str(dir_path).strip():
            continue
        try:
            if not dir_path.is_dir():
                continue
        except OSError:
            continue
        for ext in (".exe", ".cmd", ".bat", ".ps1"):
            cand = dir_path / f"{stem}{ext}"
            if cand.is_file():
                return str(cand)
    return None


def _windows_extra_agent_dirs() -> list[Path]:
    """통합 터미널 등에서 사용자 PATH가 빠져도 네이티브 설치 기본 위치를 본다."""
    la = os.environ.get("LOCALAPPDATA", "").strip()
    if not la:
        return []
    return [Path(la) / "cursor-agent"]


def _resolve_agent_path(agent_bin: str) -> str | None:
    """Windows에서 `agent`는 보통 `agent.ps1`/`agent.cmd`인데, shutil.which는 PATHEXT에 .PS1이 없으면 못 찾는다."""
    p = Path(agent_bin)
    if p.is_absolute() and p.is_file():
        return str(p)
    if ("/" in agent_bin or "\\" in agent_bin) and not p.is_absolute():
        cand = (ROOT / agent_bin).resolve()
        if cand.is_file():
            return str(cand)
    w = shutil.which(agent_bin)
    if w:
        return w
    stem = p.stem if p.suffix else agent_bin
    path_dirs = [Path(d.strip()) for d in os.environ.get("PATH", "").split(os.pathsep) if d.strip()]
    found = _find_agent_stem_in_dirs(stem, path_dirs)
    if found:
        return found
    if os.name == "nt":
        return _find_agent_stem_in_dirs(stem, _windows_extra_agent_dirs())
    return None


def _agent_spawn_argv(agent_path: str, agent_args: list[str]) -> list[str]:
    """`.ps1`는 CreateProcess로 직접 실행되지 않으므로 PowerShell로 넘긴다."""
    if agent_path.lower().endswith(".ps1"):
        return [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            agent_path,
            *agent_args,
        ]
    return [agent_path, *agent_args]


def _run_validate(web_app: bool) -> tuple[int, str]:
    cmd = [sys.executable, str(SCRIPTS / "validate.py")]
    if web_app:
        cmd.append("--web-app")
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
    return proc.returncode, out


def _run_agent(prompt: str, cfg: dict, dry_run: bool) -> int:
    agent_bin = cfg.get("agent_command") or "agent"
    agent_path = _resolve_agent_path(agent_bin)
    if not dry_run and agent_path is None:
        _fail(
            f"`PATH`에서 실행 파일을 찾을 수 없음: {agent_bin!r}. "
            "Cursor CLI를 설치하고 `agent`를 사용 가능하게 하라."
            " (Windows: `%LOCALAPPDATA%\\cursor-agent` 등 기본 설치 경로도 탐색한다.)"
        )
    ws = (ROOT / (cfg.get("workspace_relative") or ".")).resolve()
    agent_args: list[str] = ["-p", "--force"]
    if cfg.get("trust_workspace", True) is not False:
        agent_args.extend(["--trust"])
    agent_args.extend(["--workspace", str(ws)])
    model = (cfg.get("headless_model") or "").strip()
    if model:
        agent_args.extend(["--model", model])
    for arg in cfg.get("headless_extra_args", []):
        agent_args.append(str(arg))
    agent_args.append(prompt)
    cmd = _agent_spawn_argv(agent_path or agent_bin, agent_args) if agent_path else [agent_bin, *agent_args]
    if dry_run:
        print("[드라이런] 실행 예정:\n  " + " ".join(cmd[:-1]) + " '<프롬프트 …>'")
        return 0
    print("+ " + " ".join(cmd[:-1]) + " '<프롬프트 …>'", flush=True)
    proc = subprocess.run(cmd, cwd=ROOT)
    return proc.returncode


def main() -> None:
    _load_dotenv(ROOT / ".env")

    parser = argparse.ArgumentParser(description="Cursor CLI 헤드리스 하네스 루프.")
    parser.add_argument(
        "--config",
        default=None,
        help="하네스 JSON(기본: 루트 harness.config.json).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="에이전트·검증은 실행하지 않고, 실행 예정 명령과 프롬프트만 기록한다.",
    )
    args = parser.parse_args()

    cfg_path = _resolve_config_path(args.config)
    cfg = _load_config(cfg_path)
    out_rel = cfg.get("prompt_out_dir") or ".harness/out"
    out_dir = (ROOT / out_rel).resolve()
    max_rounds = int(cfg.get("max_rounds") or 3)
    if max_rounds < 1 or max_rounds > 50:
        _fail("max_rounds는 1 이상 50 이하여야 한다.")
    web_app = bool(cfg.get("web_app_validate"))

    initial_rel = cfg.get("initial_prompt_file") or "prompts/01-create-react-query-webapp.md"
    repair_rel = cfg.get("repair_prompt_file") or "prompts/02-repair-from-validation-log.md"

    last_log = ""
    for round_idx in range(1, max_rounds + 1):
        if round_idx == 1:
            prompt = _read_text(initial_rel)
        else:
            repair_tpl = _read_text(repair_rel)
            prompt = _build_repair_prompt(repair_tpl, last_log)

        _write_round_artifact(out_dir, round_idx, "prompt", prompt)
        agent_rc = _run_agent(prompt, cfg, args.dry_run)
        if agent_rc != 0 and not args.dry_run:
            print(f"경고: agent 종료 코드 {agent_rc}", file=sys.stderr)

        if args.dry_run:
            print(
                f"[드라이런] 라운드 {round_idx}: validate.py{' --web-app' if web_app else ''} 실행 예정"
            )
            continue

        val_rc, val_out = _run_validate(web_app)
        _write_round_artifact(out_dir, round_idx, "validate", val_out)
        print(val_out, end="" if val_out.endswith("\n") else "\n", flush=True)

        if val_rc == 0:
            print(f"harness_cli_loop: 라운드 {round_idx}에서 검증 통과.")
            sys.exit(0)

        last_log = val_out

    if args.dry_run:
        print(
            f"harness_cli_loop: 드라이런 완료({max_rounds}라운드); "
            f"프롬프트 산출물 경로: {out_rel!s}."
        )
        sys.exit(0)

    print(
        f"harness_cli_loop: {max_rounds}라운드 후에도 검증 실패. "
        f"산출물: {out_rel!s}.",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
