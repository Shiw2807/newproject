-- Adds audit table and resource-level policies
CREATE TABLE IF NOT EXISTS audit_events (
  ts TEXT NOT NULL,
  kind TEXT NOT NULL,
  payload TEXT NOT NULL
);

-- resource policies (naive)
CREATE TABLE IF NOT EXISTS resource_policies (
  resource_id TEXT NOT NULL,
  action TEXT NOT NULL,
  required_role TEXT NOT NULL,
  PRIMARY KEY (resource_id, action)
);
