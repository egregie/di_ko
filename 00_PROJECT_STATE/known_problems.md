# Known Problems & Blockers

- **RTK Hook Support**: Native Windows shell command intercept hooking has limited support compared to WSL. RTK remains fully functional for manual execution wrap (`rtk <cmd>`).
- **Graph Index Generation**: The flat graph index `03_knowledge_graph/graph_index.json` is currently empty. Retriever will safely return `[]` without error until graph is populated.
