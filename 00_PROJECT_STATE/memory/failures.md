# Failure Log

- **Cargo/Rust Toolchain Installation**: Initial check confirmed Cargo and rustc are not available in the sandbox. Rather than building from source, we opted to download the prebuilt binary from GitHub releases.
- **Seeding sources.json without optional fields**: Attempting to run validation with a seeded sources list that omitted `pmid` and `doi` failed type validation. Resolved by seeding empty strings `""` for these fields.
