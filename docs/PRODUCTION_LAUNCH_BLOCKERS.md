# PRODUCTION LAUNCH BLOCKERS

1. Blocker: Committed .env file (secrets exposure)

   - Evidence: A `.env` file was found committed to the repository root on the `main` branch prior to this release branch.
   - Affected component: Repository secrets / configuration
   - Severity: CRITICAL
   - Immediate remediation performed in this commit: documented the exposure and ensured `.env` and generated artifacts are listed in `.gitignore` on the release branch.
   - Required follow-up actions (team MUST perform before any production launch):
     1. Rotate all secrets that may have been present in the committed `.env` (SECRET_KEY, API keys, DB credentials, third-party keys).
     2. Revoke and reissue credentials for Stripe, OpenAI, database users, and any other provider that may have been exposed.
     3. Do NOT put any secret values into `.env.example` or any committed file.
     4. Consider enabling GitHub secret scanning and run a repository-wide secret audit.
     5. If required, coordinate a history rewrite (BFG/git filter-repo) as a second-phase operation after team agreement (NOT performed here).

2. Blocker: Committed frontend build artifacts and dependencies (frontend/node_modules, frontend/dist)

   - Evidence: `frontend/node_modules` and `frontend/dist` directories were present in the repository prior to this release branch.
   - Affected component: Repository size, supply-chain scanning, CI performance
   - Severity: HIGH
   - Immediate remediation performed in this commit: added `node_modules/` and `dist/` to `.gitignore` and documented the issue.
   - Required follow-up actions:
     1. Remove tracked `frontend/node_modules` and `frontend/dist` from the repository in a separate commit (git rm --cached ...) or via PR. This action must be coordinated with the team.
     2. After removal, verify CI builds the frontend from source (using package.json and pnpm-lock.yaml) and that no committed built assets are required for deployment.

Notes
- This commit does NOT rewrite Git history or remove secrets from existing commits. It only documents the blockers and ensures future commits ignore the sensitive/generated files.
- The removal of tracked files from the repository root will be performed after explicit confirmation and using safe coordinated steps.
