# 3d_face_builder

Deterministic, local-first Python pipeline that turns **one RGB photo** into printable **non-planar 3D
accessories** (mask → glasses → jewelry → helmet) by deforming a parametric head, not generating a mesh
from scratch. Optimized for **RTX 2060 8GB + Cloud Code Desktop**.

> Single source of truth for the spec: [`00_governance/MASTER_TZ.md`](00_governance/MASTER_TZ.md).
> Single source of truth for config: [`00_governance/pipeline_config.json`](00_governance/pipeline_config.json).

## Architecture (10 agents)
`photo quality → preprocess → landmarks → scale → reconstruction → accessory → thickness →
boolean → repair → QA/confidence → export`. See [`00_governance/AGENTS.md`](00_governance/AGENTS.md).

Stack: MediaPipe (landmarks) + FLAME/MediaPipe-TPS (reconstruction) + Depth Anything V2 (optional Z) +
trimesh/PyMeshLab (mesh) + Blender Headless (boolean). Output: **3MF** (priority), STL, OBJ, GLB.

## Quick start
```bash
pip install -r requirements.txt          # core deps already present; mediapipe/pymeshlab/pytest optional
python ops/tests/run_all.py              # or: python -m pytest ops/tests/
python ops/run_pipeline.py 01_input_raster/<photo>.jpg --accessory mask
```

## Status
Bootstrap + runnable harness complete (7/10 agents runnable, 3 scaffolded). See
[`00_PROJECT_STATE/`](00_PROJECT_STATE) for live state, known problems, and the next steps.
