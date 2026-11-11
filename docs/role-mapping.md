# Role mapping provenance

Profile models and effort values come from the current `role_delegation` entries in `minimax-code-customizations/router/llm-routing.yaml`. Resolution is deterministic: use the GPT primary when it is `openai-codex/...`; otherwise use the GPT backup when it is `openai-codex/...`. The profile comment preserves whether the selected route was primary or backup. For `session_model` primaries, this is a Codex-specific pin to the accepted GPT backup, not a dynamic fallback implementation.

A live smoke run on 2026-11-09 verified `architecture → gpt-6.1-sol/high`, `audit → gpt-6.1-terra/medium`, and `expert_review → gpt-6-luna/medium`. The successful call supplied each profile name through structured `agent_type` and left model/effort unset. Calls that provide only `task_name` create generic children (`agent_role: null`) and inherit the parent route; task names and `agent_path` are not evidence of profile selection.

Run `scripts/check_role_profiles.py` to compare every profile against the current matrix, preserve Codex `agent_type` names, and verify representative roles through actual child session journals with `scripts/itest_codex_delegation.py`.

The six additional profiles (`summarize`, `extract`, `locate`, `rewrite`, `triage`, `code_review`) follow the current matrix assignments. These are configuration choices, not independent proof of benchmark acceptance: the matrix reports 3.5/4 for `summarize` and `triage`, while a separate assessment in this session recorded 4/4. The judgments need reconciliation. The six-role candidate runs did not establish filesystem isolation from the gold, and the Terra `code_review` attempt continued after an interrupted turn. Do not treat them as conclusive blind benchmark results.

MiniMax's delegation hook can resolve roles from a textual marker, agent name, rules and classifier and supports provider routes. Codex profiles require explicit structured `agent_type`; they do not implement that router. In particular, the MiniMax `code_review` agent currently describes a brainstorming author, whereas the Codex profile performs ordinary code review. Do not assume their behavioral contracts are interchangeable.
