---
name: source-verify
description: |
  Verify facts and assign evidence levels (A-D) based on source rules.
license: Apache-2.0
metadata:
  version: v1.0
  publisher: google
---

# Source Verify Skill (A05)

This skill validates clinical facts against EBM validation criteria. It assigns evidence levels and flags anomalies.

## Input
- Deduplicated facts from `02_processing/`.

## Output
- Verified facts with assigned `evidence_level` (A, B, C, or D).

## Protocol
- Rule: Fact must have ≥2 independent Tier A/B sources OR 1 peer-reviewed journal source.
- Assign level:
  - **A**: Systematic review / meta-analysis / RCT
  - **B**: Cohort / clinical guideline
  - **C**: Expert consensus / case series
  - **D**: Anecdotal / blog (Must be rejected/discarded for clinical slides)
- Discard/delete any fact where confidence is low or sources cannot be verified.
- Follow system instructions in `00_governance/prompts/A05_verifier.txt`.

## Execution & Script Reference
Use the validation rules and contrast criteria logic from:
- Script: `ops/scripts/verify_gate.py` (Fact validation write gate)
- Script: `ops/scripts/verification_agent.py` (Passport verification agent)


## Caveman Mode
`full`


