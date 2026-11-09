"""Verify a Codex role smoke test against child journals and role profiles."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path


PROFILES = Path(__file__).resolve().parents[1] / ".codex" / "agents"


def _thread_spawn(payload: dict) -> dict:
    source = payload.get("source") or {}
    if not isinstance(source, dict):
        return {}
    subagent = source.get("subagent") or {}
    if not isinstance(subagent, dict):
        return {}
    spawn = subagent.get("thread_spawn") or {}
    return spawn if isinstance(spawn, dict) else {}


def _read_events(path: Path):
    with path.open(encoding="utf-8") as journal:
        for line_number, line in enumerate(journal, start=1):
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc


def verify(day: Path, parent: str, roles: set[str], profile_dir: Path = PROFILES) -> None:
    if not roles:
        raise ValueError("At least one role must be requested")

    observed_roles: set[str] = set()
    for path in sorted(day.glob("rollout-*.jsonl")):
        events = list(_read_events(path))
        first = events[0] if events else {}
        payload = first.get("payload", {})
        spawn = _thread_spawn(payload)
        if spawn.get("parent_thread_id") != parent:
            continue

        role = spawn.get("agent_role")
        if not isinstance(role, str) or not role:
            raise SystemExit(f"{path.name}: child has no named role metadata; delegation occurred but profile routing is unverified")
        if role not in roles:
            continue
        if role in observed_roles:
            raise SystemExit(f"Repeated child role: {role}")

        profile_path = profile_dir / f"{role}.toml"
        if not profile_path.is_file():
            raise SystemExit(f"Missing profile for child role {role}: {profile_path}")
        profile = tomllib.loads(profile_path.read_text(encoding="utf-8"))
        if profile.get("name") != role:
            raise SystemExit(f"{role}: profile name does not match its filename")
        expected = (profile.get("model"), profile.get("model_reasoning_effort"))

        child_id = payload.get("id")
        child_turn_ids = {
            event.get("payload", {}).get("turn_id")
            for event in events
            if event.get("type") == "token_usage_record"
            and event.get("payload", {}).get("thread_id") == child_id
            and event.get("payload", {}).get("turn_id")
        }
        completed_turn_ids = {
            event.get("payload", {}).get("turn_id")
            for event in events
            if event.get("type") == "event_msg"
            and event.get("payload", {}).get("type") == "task_complete"
            and event.get("payload", {}).get("turn_id") in child_turn_ids
            and event.get("payload", {}).get("last_agent_message") == f"ROUTE_SMOKE {role}"
        }
        contexts_by_turn: dict[str, set[tuple[str | None, str | None]]] = {}
        for event in events:
            event_payload = event.get("payload", {})
            turn_id = event_payload.get("turn_id")
            if event.get("type") == "turn_context" and turn_id in child_turn_ids:
                contexts_by_turn.setdefault(turn_id, set()).add(
                    (event_payload.get("model"), event_payload.get("effort"))
                )

        matching_turns = {
            turn_id
            for turn_id in completed_turn_ids
            if contexts_by_turn.get(turn_id) == {expected}
        }
        if not matching_turns:
            observed = {turn_id: contexts_by_turn.get(turn_id, set()) for turn_id in child_turn_ids}
            raise SystemExit(f"{role}: expected own turn {expected} with ROUTE_SMOKE marker; observed {observed}")
        print(f"{role}: {expected[0]} / {expected[1]} / completed ({len(matching_turns)} verified turn(s))")
        observed_roles.add(role)

    missing = roles - observed_roles
    if missing:
        raise SystemExit(f"Missing child roles: {', '.join(sorted(missing))}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("day", type=Path, help="Codex sessions YYYY/MM/DD directory")
    parser.add_argument("parent", help="Parent thread ID from the thread.started event")
    parser.add_argument("roles", nargs="+", help="Expected named profile roles in this smoke run")
    parser.add_argument("--profiles", type=Path, default=PROFILES)
    args = parser.parse_args()
    verify(args.day, args.parent, set(args.roles), args.profiles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
