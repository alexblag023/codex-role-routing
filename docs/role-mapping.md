# Role mapping provenance

Profile models and effort values come from the `role_delegation` entries in the GPT delegation matrix dated 2026-11-09. Each profile uses that role's GPT route, whether the matrix marked it primary or backup. The profile comment preserves this distinction.

A live verification run on 2026-11-09 confirmed model selection for `architecture`, `audit`, and `expert_review`. The verifier checks child role, model, effort, and completion marker.

Refresh profiles by comparing every role against the current approved matrix, preserve Codex `agent_type` names, and verify representative roles through actual child session journals.
