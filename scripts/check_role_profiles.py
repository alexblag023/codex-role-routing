"""Validate generated Codex role profiles against the approved routing matrix."""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / ".codex" / "agents"
DEFAULT_MATRIX = ROOT.parent / "minimax-code-customizations" / "router" / "llm-routing.yaml"


def _gpt_route(entry: dict) -> tuple[str, str] | None:
    for route_name in ("primary", "backup"):
        route = entry.get(route_name)
        if isinstance(route, str) and route.startswith("openai-codex/"):
            effort = entry.get(f"{route_name}_effort")
            if not isinstance(effort, str):
                raise ValueError(f"GPT route {route!r} has no string {route_name}_effort")
            return route.removeprefix("openai-codex/"), effort
    return None


def validate(matrix_path: Path, profile_dir: Path = PROFILE_DIR) -> list[str]:
    matrix_doc = yaml.safe_load(matrix_path.read_text(encoding="utf-8")) or {}
    matrix = matrix_doc.get("role_delegation")
    if not isinstance(matrix, dict) or not matrix:
        raise ValueError(f"Missing non-empty role_delegation in {matrix_path}")

    profiles: dict[str, dict] = {}
    errors: list[str] = []
    for path in sorted(profile_dir.glob("*.toml")):
        profile = tomllib.loads(path.read_text(encoding="utf-8"))
        role = profile.get("name")
        if not isinstance(role, str) or not role:
            errors.append(f"{path.name}: missing profile name")
            continue
        if path.stem != role:
            errors.append(f"{path.name}: filename does not match profile name {role!r}")
        if role in profiles:
            errors.append(f"{path.name}: duplicate profile name {role!r}")
            continue
        profiles[role] = profile

    for role in sorted(set(profiles) - set(matrix)):
        errors.append(f"{role}: profile has no role_delegation entry")
    for role in sorted(set(matrix) - set(profiles)):
        errors.append(f"{role}: matrix role has no Codex profile")

    for role in sorted(set(profiles) & set(matrix)):
        profile = profiles[role]
        expected = _gpt_route(matrix[role])
        if expected is None:
            errors.append(f"{role}: matrix has no GPT primary or backup route")
            continue
        observed = (profile.get("model"), profile.get("model_reasoning_effort"))
        if observed != expected:
            errors.append(f"{role}: expected model/effort {expected}, found {observed}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--profiles", type=Path, default=PROFILE_DIR)
    args = parser.parse_args()
    try:
        errors = validate(args.matrix, args.profiles)
    except (OSError, ValueError, yaml.YAMLError, tomllib.TOMLDecodeError) as exc:
        parser.error(str(exc))
    if errors:
        print("Role profile validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated {len(list(args.profiles.glob('*.toml')))} role profiles against {args.matrix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
