# Security

Secrets, staged-file risk, and a sensitive-content sweep across the four target directories, done because this project has one documented prior incident of exactly this leaking into git history.

- [Secrets and .env files](secrets-and-env.md)
- [Staged raw session exports in the backup repo](staged-inbox-risk.md) — the one live, current risk found.
- [Personal/health content sweep result](personal-content-sweep.md) — clean, false-positive rate documented.
- [Findings outside the four target directories](outside-scope.md) — noticed en route, not acted on.
