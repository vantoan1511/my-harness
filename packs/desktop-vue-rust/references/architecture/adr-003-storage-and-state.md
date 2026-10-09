# ADR-003: Storage Tiers & State Management

## Context

Desktop web applications have access to both browser storage APIs (`localStorage`, `IndexedDB`) and desktop filesystem storage via IPC.

## Decision: Three-Tier Storage Architecture

| Tier | Technology | Purpose | Lifetime |
|---|---|---|---|
| **Tier 1: Ephemeral UI** | Vue `ref` / `reactive` | Modal open/close, active form inputs, local sort | View lifecycle |
| **Tier 2: Session Memory** | Pinia reactive stores | Active entity, search queries, in-memory cache | Application session |
| **Tier 3: Persistent Storage** | Desktop filesystem via Backend IPC | App settings, saved filters, window bounds | Permanent across restarts |

## Prohibitions
- **Prohibit browser `localStorage`**: Webview storage origins can be wiped, corrupted, or reset across runtime updates.
- **Prohibit direct filesystem access from frontend**: All disk read/write must be routed through centralized services across the IPC boundary.
