# Recipe: Rust Backend Testing (`cargo test`)

Standard testing patterns for desktop application Rust backends.

---

## 1. In-Module Unit Tests (`#[cfg(test)]`)

```rust
// src/services/formatter.rs
pub fn format_filesize(bytes: u64) -> String {
    if bytes >= 1024 * 1024 * 1024 {
        format!("{:.2} GiB", bytes as f64 / (1024.0 * 1024.0 * 1024.0))
    } else if bytes >= 1024 * 1024 {
        format!("{:.2} MiB", bytes as f64 / (1024.0 * 1024.0))
    } else if bytes >= 1024 {
        format!("{:.2} KiB", bytes as f64 / 1024.0)
    } else {
        format!("{} B", bytes)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_bytes() {
        assert_eq!(format_filesize(500), "500 B");
    }

    #[test]
    fn test_format_kib() {
        assert_eq!(format_filesize(2048), "2.00 KiB");
    }

    #[test]
    fn test_format_mib() {
        assert_eq!(format_filesize(10485760), "10.00 MiB");
    }
}
```

---

## 2. IPC Request/Response Serialization Tests

Always write contract tests to guarantee IPC schema stability between Rust and TypeScript:

```rust
// src/ipc/models.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct ActionResponse {
    pub success: bool,
    pub message: String,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_action_response_camel_case_serialization() {
        let resp = ActionResponse {
            success: true,
            message: "Operation completed".to_string(),
        };

        let json = serde_json::to_string(&resp).expect("Failed to serialize");
        assert!(json.contains("\"success\":true"));
        assert!(json.contains("\"message\":\"Operation completed\""));

        let deserialized: ActionResponse = serde_json::from_str(&json).expect("Failed to deserialize");
        assert_eq!(resp, deserialized);
    }
}
```

---

## 3. Execution Commands

```bash
# Run all backend tests
cargo test

# Run a specific test module
cargo test -- formatter::tests

# Run with stdout output enabled
cargo test -- --nocapture
```
