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

### 1.6 Placeholder ID (`placeholder_id`) — composite, Phase 8+
- **Format**: `id_<type>_s<NN>_<slug>` where `type` ∈ `img | graph | illustration | logo`,
  `NN` is the 2-digit slide number, `slug` is a short lowercase snake_case content hint.
- **Rules**: unique within a deck; immutable after contract emission (Stage 2 performs binary
  replacement by this ID); registered in `05_content/contracts/<deck_id>_contract.json`.
- **Example**: `id_illustration_s04_moa`, `id_img_s13_before_after`, `id_logo_s01_brand`

### 1.7 Layout ID (`layout_id`) — Layout Library v2, Phase 8+
- **Format**: `layout_<descriptive_snake_case>`; mirrored split variants use `_left` / `_right` suffix.
- **Rules**: prefix `layout_` is mandatory (`tpl_` rejected); v1 names are kept as `alias` for
  backward compatibility with the current renderer.
- **Example**: `layout_clinical_50_50_left`, `layout_hero_asymmetric`

## 2. File Naming and Organization

### 2.1 Knowledge Graph Files
- **Entities**: `03_knowledge_graph/entities/<entity_id>.json` (e.g., `03_knowledge_graph/entities/retinol.json`)
- **Facts**: `03_knowledge_graph/facts/<fact_id>.json` (e.g., `03_knowledge_graph/facts/fact_0001.json`)
- **Relationships**: `03_knowledge_graph/relationships/<rel_id>.json` (e.g., `03_knowledge_graph/relationships/rel_0001.json`)
