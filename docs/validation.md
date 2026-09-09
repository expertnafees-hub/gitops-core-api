# Validation evidence

- PASS: six application contract tests (liveness, readiness, release identity, unknown route, unsupported method, HEAD response).
- PASS: Docker build using pinned Python base and exact runtime dependencies.
- PASS: localhost health response with a non-root, read-only, capability-restricted container.
- The 3-second Docker checker process deadline proved too short on the loaded local VM; increased to 10 seconds while preserving the 2-second HTTP request timeout.
- Local Trivy database download timed out on its default mirror; an alternate official registry attempt is in progress. No clean vulnerability result is claimed.

AWS release, ECR publication, Argo CD integration and cloud rollback have not been exercised.
