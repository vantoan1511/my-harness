# ADR-002: Centralized Backend-Owned Configuration System

## Context

Desktop applications require user customization (timeouts, feature toggles, paths, themes, notifications).

## Decision: Backend as Single Source of Truth

Rather than having the frontend persist settings to browser `localStorage` or arbitrary JSON files:
1. **The Backend Owns Configuration Metadata**:
   The Rust backend defines configuration schemas (`key`, `name`, `datatype`, `defaultValue`, `cardinality`, `isConfidential`).
2. **Lean Disk Overrides**:
   The disk file (`~/.<app_name>/config.json`) strictly stores user customized key-value pairs (`{"key": value}`).
3. **Decoupled Frontend Presentation**:
   Frontend views receive a `Vec<Configuration>` across IPC and render form controls dynamically with PrimeVue (`ToggleSwitch`, `InputNumber`, `InputText`).

## Consequences

### Positive
- Cross-platform path management handled reliably by Rust standard library.
- Secrets/confidential keys are handled securely by backend rather than stored in cleartext web storage.
- Adding a new configuration requires zero frontend UI code changes (rendered dynamically from schema).
- Background workers and services can access configuration directly without IPC round-trips.
