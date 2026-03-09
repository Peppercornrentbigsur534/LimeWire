# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainer directly (or use GitHub's private vulnerability reporting)
3. Include steps to reproduce and potential impact
4. Allow reasonable time for a fix before public disclosure

## Scope

LimeWire is a local desktop application. Security concerns include:
- Command injection via user-supplied URLs or filenames
- Path traversal in file operations
- Unsafe deserialization of JSON config files
- Dependencies with known CVEs

## Mitigations in Place

- URL scheme validation (`_BLOCKED_SCHEMES` allowlist)
- Windows reserved filename filtering (`_WIN_RESERVED`)
- Atomic JSON writes via temp file + `os.replace()`
- No network listeners — all connections are outbound only
- No auto-execution of downloaded content
