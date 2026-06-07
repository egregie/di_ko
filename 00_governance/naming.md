# YM PROSKIN — Naming Conventions

This document defines the naming conventions for all entities, facts, relationships, sources, and slides within the Presentation Intelligence Platform.

## 1. Identifiers

### 1.1 Source ID (`source_id`)
- **Format**: `SRC-` followed by a 4-digit zero-padded integer.
- **Example**: `SRC-0001`, `SRC-0042`

### 1.2 Entity ID (`entity_id`)
- **Format**: Lowercase snake_case matching the canonical name of the entity.
- **Rules**:
  - No spaces or capital letters.
  - Singular form preferred.
  - Aliases should be specified in the entity structure, not as separate entity files.
- **Example**: `retinol`, `vitamin_c`, `epidermis`, `anti_aging`

### 1.3 Fact ID (`fact_id`)
- **Format**: `fact_` followed by a 4-digit zero-padded integer.
- **Example**: `fact_0001`, `fact_0123`

### 1.4 Relationship ID (`rel_id`)
- **Format**: `rel_` followed by a 4-digit zero-padded integer.
- **Example**: `rel_0001`, `rel_0099`

### 1.5 Slide Spec ID (`id` or `slide_id`)
- **Format**: `<deck_name>-s<slide_number>` where slide_number is a 2-digit zero-padded integer.
- **Example**: `deck01-s03`, `acne_course-s12`

## 2. File Naming and Organization

### 2.1 Knowledge Graph Files
- **Entities**: `03_knowledge_graph/entities/<entity_id>.json` (e.g., `03_knowledge_graph/entities/retinol.json`)
- **Facts**: `03_knowledge_graph/facts/<fact_id>.json` (e.g., `03_knowledge_graph/facts/fact_0001.json`)
- **Relationships**: `03_knowledge_graph/relationships/<rel_id>.json` (e.g., `03_knowledge_graph/relationships/rel_0001.json`)
