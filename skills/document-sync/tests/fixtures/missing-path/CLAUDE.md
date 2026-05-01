# Test Fixture — Missing Path

This fixture tests F3 (path/package reference validation).
The path `pkg/gone/deleted.go` is mentioned but does NOT exist in this fixture root.

## Project Structure

The main entry point is `pkg/gone/deleted.go`. Adjacent helpers live under `pkg/gone/`.

(Expected document-sync behavior: detect that `pkg/gone/deleted.go` doesn't exist, present this as an ASK candidate — never auto-remove the reference. User must confirm.)
