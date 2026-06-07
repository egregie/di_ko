# Decisions Log

- **DEC-001**: Foundation-First Approach. Prioritize ontology, graph database schemas, and agent constraints before visual rendering templates.
- **DEC-002**: Local Git-Tracked Graph. Store knowledge entities, facts, and relationships in raw JSON files with a flat index to prevent cloud dependencies.
- **DEC-003**: Token Saving CLI Proxy. Introduce RTK globally to compress shell commands and mitigate token overflow.
- **DEC-004**: Cognitive Density Mode. Configure Caveman modes (verbose full for research/extraction, terse ultra for integration/validation) by role.
- **DEC-005**: Walkthrough Format Standard. Establish a standard machine-readable markdown template for external review auditing (Claude).
- **DEC-006**: Automatic Graph Index Builder. Implement build_index.py to automate graph index compilation and prevent copy-paste synchronization errors.
