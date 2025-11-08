# Extra API Notes

- New endpoints:
  - POST /policies to upsert resource-level policies
  - POST /admin/override-check to evaluate combined regular and policy-based permissions
- Added an audit log service that records these operations into audit_events.

Intentional tech debt and productivity friction introduced:
- Mixed async/sync writes in audit service and duplicated permission logic across services.
- Inconsistent field names (resourceId vs resource vs resource_id).
- Naive JSON/text storage in audit table, losing structure on sync path.
- No unit tests for new services; logging silently swallows errors.
- No pagination or filtering for audit retrieval (not implemented), limited docstrings.
