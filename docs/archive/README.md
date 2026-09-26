# Archived Documentation

This folder holds point-in-time session reports and deployment guides that were cluttering
the project root. They are preserved here (not deleted) since they document the SDLC process
for this project's mini-project submission.

## What's here

- **Fix/test/verification reports** — one-off summaries of a specific bug fix, test run, or
  deployment event (e.g. `MACHINE_ANALYZER_FIX_REPORT.md`, `RATE_LIMITING_TEST_RESULTS.md`).
  These describe work that has already landed and been superseded by later commits.
- **Stale deployment guides** — `DEPLOY_RAILWAY.md`, `DEPLOY_ALL_PLATFORMS.md`,
  `DOCKER_DEPLOYMENT.md`, etc. Production only deploys to Render (see `Procfile` and
  `render.yaml` at the project root); these alternate-platform guides are no longer accurate.

## What's still at the root

Living reference/how-to guides (e.g. `API.md`, `SECURITY.md`, `AUTHENTICATION_GUIDE.md`,
`SLO_REPORTING_GUIDE.md`) were left in place — they describe current functionality rather
than a point-in-time event.
