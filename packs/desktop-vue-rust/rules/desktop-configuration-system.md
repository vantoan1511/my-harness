# Desktop Application Configuration System

## Overview

Desktop applications with privileged backends (e.g. Rust) and web frontends (Vue 3) should use a centralized, system-defined configuration model. Settings are defined and validated by the backend engine and delivered across IPC to the frontend.

### Core Principles

1. **System-Controlled Definitions**: Application configurations are defined, typed, validated, and controlled by the backend engine.
2. **Unified Data Contract**: Backend and frontend communicate exclusively via a strongly-typed `Configuration` model.
3. **User Customization Scope**: Users can only modify the `value` of enabled configurations.
4. **Lean Local Storage**: The user's local configuration file (`~/.<app_name>/config.json`) strictly persists customized key-value pairs (`{"key": value}`).
5. **Dynamic UI Rendering**: The frontend settings views dynamically render appropriate controls (`ToggleSwitch`, `InputNumber`, `Select`, `InputText`) based on configuration metadata (`datatype`, `cardinality`, `enable`, `isConfidential`).

---

## Storage & File Hierarchy

All application runtime files and user preferences reside in the user's home directory (`~/.<app_name>`):

- Configuration file: `~/.<app_name>/config.json` (key-value overrides only)
- Logs directory: `~/.<app_name>/logs/`
  - Active log: `~/.<app_name>/logs/app.log`
  - Daily archives: `~/.<app_name>/logs/app.log.YYYY-MM-DD`

---

## Data Model Specification

```typescript
export type ConfigurationDataType = 'string' | 'number' | 'boolean'
export type ConfigurationCardinality = '0..1' | '0..*' | '1..*' | '1..1' | string

export interface Configuration<T = unknown> {
  key: string                  // Unique identification key (e.g., 'maxLogFiles')
  name: string                 // Display title shown on UI
  description: string          // Detailed description of the setting
  datatype: ConfigurationDataType // 'string' | 'number' | 'boolean'
  defaultValue?: T             // Default fallback value
  value?: T                    // Effective or user-customized value
  isConfidential: boolean      // When true, encoded in transit (Base64)
  cardinality: ConfigurationCardinality // Multiplicity ('0..1', '0..*', '1..*', '1..1')
  enable: boolean              // Applicable/active flag (false = disabled / Coming soon)
  createdAt?: string           // ISO timestamp of definition creation
  lastUpdatedAt?: string       // ISO timestamp of last update
}
```

### Cardinality / Multiplicity (`cardinality`)

| Cardinality | Meaning | UI Representation |
|---|---|---|
| `0..1` | Single optional value | Single input field (can be left blank) |
| `1..1` | Single mandatory value | Single required input control (`InputNumber`, `ToggleSwitch`, `InputText`) |
| `0..*` | Multiple optional values | Comma-separated list or item list |
| `1..*` | Multiple values (at least 1 required) | Multi-item list with validation |

---

## Architectural Layers

```
┌────────────────────────────────────────────────────────┐
│ Vue Frontend                                           │
│  - Settings UI: src/components/settings/*.vue          │
│    (Dynamic rendering with PrimeVue controls)          │
│  - Reactive Store: src/stores/settingsStore.ts         │
│  - Typed IPC Service: src/services/appSettingsService.ts│
└──────────────────────────┬─────────────────────────────┘
                           │ Desktop IPC (JSON)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Rust Engine                                            │
│  - IPC Dispatcher: src/ipc/handlers/mod.rs             │
│  - Settings Handler: src/ipc/handlers/settings.rs      │
│  - Events Definition: src/ipc/events.rs                │
│  - Config Schema & Storage: src/config.rs              │
│  - File System Storage: ~/.<app_name>/config.json      │
└────────────────────────────────────────────────────────┘
```

---

## Backend Implementation (Rust)

### 1. Unified Configuration Struct
- `Configuration`: Represents setting metadata, default values, and effective values.
- `Configuration::system_definitions()`: Canonical source of truth defining all system configurations.
- `AppConfig`: Transparent map (`HashMap<String, Value>`) mapped to `~/.<app_name>/config.json`.
  - `.load()`: Loads key-value pairs from `config.json`.
  - `.save()`: Serializes key-value pairs to `config.json`.
  - `.get_configurations()`: Combines system definitions with user values, automatically Base64-encoding confidential values.
  - `.update_from_configurations(&[Configuration])`: Updates user values, decoding Base64 if confidential.

### 2. IPC Protocol
- `getAppSettings`: Reads `AppConfig::load().get_configurations()` and sends `AppSettingsUpdated`.
- `updateAppSettings`: Accepts `Vec<Configuration>` or `HashMap<String, Value>`, updates `AppConfig`, saves to disk, and broadcasts `AppSettingsUpdated`.

---

## Frontend Implementation (Vue 3 / TypeScript)

### 1. Type Definitions (`src/types/settings.ts`)
- `Configuration<T>`: Unified configuration interface matching Rust backend.
- `ConfigurationMap`: Key-value record (`Record<string, unknown>`).

### 2. Frontend Service (`src/services/appSettingsService.ts`)
- `getAppSettings()`: Dispatches `'getAppSettings'`.
- `updateAppSettings(settings)`: Dispatches `'updateAppSettings'`.

### 3. Pinia Store (`src/stores/settingsStore.ts`)
- Reactive state: `settings` (`ref<Configuration[]>`), `isLoading`, `isSaving`.
- Helper getters:
  - `getConfig(key: string): Configuration | undefined`
  - `getConfigValue<T>(key: string, fallback?: T): T`
- Action helpers:
  - `updateConfigValue(key: string, value: unknown)`
  - `updateSettings(newSettings: Configuration[] | ConfigurationMap)`

### 4. Dynamic Settings UI
- `GeneralSettingsForm.vue`: Dynamically iterates over `settingsStore.settings`.
- Automatically renders:
  - `ToggleSwitch` for `datatype === 'boolean'`
  - `InputNumber` or preset `Select` for `datatype === 'number'`
  - `InputText` with multi-value formatting for `cardinality === '0..*' || cardinality === '1..*'`
  - Password-masked inputs for `isConfidential === true`
  - Disabled styling (`opacity-60`, `Tag` with "Coming soon") when `enable === false`
