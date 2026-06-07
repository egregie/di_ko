# Lessons Learned

- **Strict Schema Conformity**: Graph validation requires explicit declarations for optional fields (like `pmid` or `doi` in source records) since template-based assertion evaluates key existence.
- **RTK Exclusions**: Always configure `exclude_commands` in RTK to ensure validation outputs remain uncompressed, avoiding truncation of critical structure errors.
- **Terse Walkthrough Audit**: Formatting walkthrough files strictly to a standard layout allows consistent external parsing by client agents.
- **RTK Hook Support**: While native Windows shell PreToolUse-hook is restricted in sandbox IDE environments, running commands with explicit manual wrap (`rtk <cmd>`) is fully functional and achieves up to ~73% token efficiency.
- **Abstract-Grounding Limits**: Auditing facts strictly against raw abstract text can lead to false negatives for facts that are medically true but not detailed in the paper's summary abstract (e.g., exact conversion pathway steps or adaptation side effects). Future phases should target review papers or full texts for such foundational claims.
