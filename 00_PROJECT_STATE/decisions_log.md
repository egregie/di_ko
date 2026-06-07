# Decisions Log

- **DEC-001**: Foundation-First Approach. Prioritize ontology, graph database schemas, and agent constraints before visual rendering templates.
- **DEC-002**: Local Git-Tracked Graph. Store knowledge entities, facts, and relationships in raw JSON files with a flat index to prevent cloud dependencies.
- **DEC-003**: Token Saving CLI Proxy. Introduce RTK globally to compress shell commands and mitigate token overflow.
- **DEC-004**: Cognitive Density Mode. Configure Caveman modes (verbose full for research/extraction, terse ultra for integration/validation) by role.
- **DEC-005**: Walkthrough Format Standard. Establish a standard machine-readable markdown template for external review auditing (Claude).
- **DEC-006**: Automatic Graph Index Builder. Implement build_index.py to automate graph index compilation and prevent copy-paste synchronization errors.
- **DEC-007**: Confidence Policy. Set the confidence score of facts marked as WEAK to 0.80 to reflect partial or indirect abstract evidence.
- **DEC-008**: Collection Hardening. Identify source collection and fact verification (A02/A05) as the primary quality bottleneck, planning automated PMID validation before scaling to other topics.
- **DEC-009**: Automated Verification Gate. Mandate that all clinical facts must pass the verify-at-write gate (source existence, abstract support, and evidence level alignment check) to be eligible for knowledge graph ingestion. Any unverified or mismatching facts are automatically rejected.
- **DEC-010**: Ingestion Quality Baseline. Record that Batch 1 live audit revealed a 27.3% fact rejection rate (specifically 33.3% for Vitamin C and Niacinamide, and 100.0% for cross-topic interactions). This is due to previous collection pipelines pulling unsupported claims. We will address the root-cause in Phase 4 by transitioning to Exa-grounded web search collection.
- **DEC-011**: Verification Gate Hardening. Require that all facts undergo dynamic validation (fetching live PubMed abstracts and running keyword overlap checks) without hardcoded mock lists in production code, recording verification metadata (`verified_via`, `verified_at`, `source_title`) directly on the fact node.
- **DEC-012**: Exa-Grounded Search Deferred. Exa integration is deferred because the API key is not configured and the pilot was simulated. Retaining Exa MCP server config in disabled mode; live A/B-pathway pilot comparison remains pending user configuration of EXA_API_KEY.



