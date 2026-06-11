---
name: slide-plan
description: |
  Deterministically plan a deck: detect slide intents, select layouts from the
  approved pool, fill slots, and emit slide-specs plus a placeholder contract.
license: Apache-2.0
metadata:
  version: v1.0
  publisher: ym_proskin
---

# Slide Planning Engine Skill (A09, Stage 1)

This skill turns verified graph content into designer-ready slide specifications.
It is the only sanctioned path from content to composition (P022): no layout is
ever invented by an LLM.

## Input
- Narrative outline + active graph facts (non-quarantined only).
- `04_design_system/layouts.json` (approved Layout Library; geometry required from v2).
- `03_slide_taxonomy/slide_intents.json` (trimmed taxonomy, Phase 8.3+).

## Output
- `05_content/specs/<deck_id>/<deck_id>-sNN.json` slide specs (13–20 per deck, P023).
- `05_content/contracts/<deck_id>_contract.json` placeholder contract
  (schema: `00_governance/schemas/placeholder_contract.json`).

## Operation Protocol
1. Detect intent per slide — rule-based (keywords + structural metrics:
   text_nodes, lists_count, list_elements, has_visual, visual_type, visual_count).
2. Select `layout_id` deterministically: primary → secondary →
   `layout_text_dense_fallback`. LLM choice is forbidden (P022).
3. Apply attention dynamics: mirror split layouts on consecutive identical
   split intents (history depth = 1; split layouts only).
4. Fill slots; validate `max_chars` per slot — violation is a hard error
   before render (fail fast).
5. Emit composite placeholder IDs `id_{type}_s{NN}_{slug}` (naming.md §1.6)
   and write the contract with routing per P021
   (logo→registry SVG, illustration/graph→diagram engine, img→generation/stock).
6. Reset planner history between decks (`clear_session`).

## Execution & Validation
Planned executor: `ops/scripts/slide_planner.py` (Phase 8.4, per P010 registered
here once created). Until then this skill governs manual spec authoring: the same
rules apply, validated by `ops/scripts/qa_deck.py` gates.
Hard gates: deck scope 13–20 slides (P023); placeholder without contract entry =
FAIL; `route` ↔ `type` mismatch = FAIL; bounds/relative_bounds parity ±1px.

## Caveman Mode
`ultra`
