---
name: fact-extract
description: |
  Parse raw documents and text in 01_collection to extract core scientific claims and facts.
license: Apache-2.0
metadata:
  version: v1.0
  publisher: google
---

# Fact Extract Skill (A03)

This skill processes raw text/PDF files in the collection area to extract explicit facts, mechanisms of action, and supporting bibliographic details.

## Input
- Raw files or folders in `01_collection/`.

## Output
- Draft fact JSON objects matching the `fact.json` schema layout (saved in `02_processing/`).

## Procedure
1. Scan raw documents for clinical statements, mechanism descriptions, and outcomes.
2. For each identified statement, record:
   - The verbatim/paraphrased statement.
   - Associated entity identifier (e.g. `retinol`).
   - Source reference ID (from sources register).
   - Indicated confidence score (0.0 to 1.0).
3. Save output files in the `02_processing/` directory for verification.
