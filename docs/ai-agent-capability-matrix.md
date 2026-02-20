# AI Agent Capability Matrix

This matrix defines what the agent can do, with default risk and expected control mode.

## Control Modes
- `auto`: can run without human approval.
- `auto_nonprod`: can run automatically only in `dev` and `stage`.
- `approval_required`: requires one explicit approval.
- `dual_approval_required`: requires two explicit approvals.

## Matrix
| Domain | Task | Primary Tools | Default Risk | Control Mode | Required Evidence | Rollback Pattern |
|---|---|---|---|---|---|---|
| Kubernetes | Inspect pods, services, ingress, events | `kubectl get`, `kubectl describe` | R0 | auto | Command output + target namespace | Not required (read-only) |
| Kubernetes | Collect logs from pods/deployments | `kubectl logs` | R0 | auto | Logs with timestamps | Not required (read-only) |
| Kubernetes | Restart deployment | `kubectl rollout restart` | R1 | auto_nonprod | Before/after pod status | `kubectl rollout undo` |
| Kubernetes | Scale deployment | `kubectl scale` | R1 | auto_nonprod | Replicas before/after | Scale back to previous replicas |
| Kubernetes | Edit Service/Ingress exposure | `kubectl apply`, `kubectl patch` | R2 | approval_required | Diff + post-change health checks | Reapply previous manifest |
| Helm | Render and validate templates | `helm template`, `helm lint`, `make helm-tenant-template` | R0 | auto | Rendered manifests + lint output | Not required (read-only) |
| Helm | Dry-run upgrade | `helm upgrade --dry-run`, `make helm-tenant-dry-run` | R0 | auto | Dry-run output | Not required (read-only) |
| Helm | Upgrade release in `dev/stage` | `helm upgrade` | R1 | auto_nonprod | Revision diff + health checks | `helm rollback <release> <rev>` |
| Helm | Upgrade release in `prod` | `helm upgrade` | R2 | approval_required | Change set + smoke checks | `helm rollback <release> <rev>` |
| Helm | Uninstall release | `helm uninstall` | R3 | dual_approval_required | Dependency impact + backup evidence | Reinstall from known good values |
| Linux/VM | Read system state and services | `ssh`, `journalctl`, `systemctl status` | R0 | auto | Host + service status | Not required (read-only) |
| Linux/VM | Restart service | `systemctl restart` | R1 | auto_nonprod | Service status before/after | Restart previous stable instance/config |
| Networking | DNS/TLS/HTTP checks | `dig`, `nslookup`, `curl`, `openssl` | R0 | auto | Raw command outputs | Not required (read-only) |
| Networking | Firewall/LB policy changes | Cloud CLI + IaC apply | R2 | approval_required | Planned diff + connectivity tests | Apply previous policy version |
| Git | Inspect code state | `git status`, `git diff`, `git log`, `rg` | R0 | auto | Referenced files and diffs | Not required (read-only) |
| Coding | Create patch in repo | file edits + `git add` | R1 | auto_nonprod | Exact file diff + rationale | Revert commit |
| Coding | Run unit/integration tests | test commands (`make`, `npm`, `pytest`, etc.) | R0 | auto | Test output + exit code | Not required (read-only) |
| Coding | Dependency update in app | package manager + tests | R1 | auto_nonprod | Lockfile diff + test pass | Revert dependency commit |
| Database | Schema migration | migration tool (`alembic`, `liquibase`, etc.) | R2 | approval_required | Migration plan + backup check | Down migration or restore snapshot |
| Data | Destructive cleanup/wipe | SQL/CLI delete operations | R3 | dual_approval_required | Scope proof + backup snapshot | Restore from backup/snapshot |

## Notes
- Risk can be escalated by policy based on environment (`prod`) and blast radius.
- Every `R1+` action must include a rollback plan before execution.
