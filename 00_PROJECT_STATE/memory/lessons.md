# Lessons Learned

- **Strict Schema Conformity**: Graph validation requires explicit declarations for optional fields (like `pmid` or `doi` in source records) since template-based assertion evaluates key existence.
- **RTK Exclusions**: Always configure `exclude_commands` in RTK to ensure validation outputs remain uncompressed, avoiding truncation of critical structure errors.
- **Terse Walkthrough Audit**: Formatting walkthrough files strictly to a standard layout allows consistent external parsing by client agents.
