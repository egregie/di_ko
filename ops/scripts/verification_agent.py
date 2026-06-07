"""
AGENT 2: VERIFICATION AGENT
Production verifier for Passport v2.1 data.
Version: 2.3 (2026-06-04) — P8.0 CHECK 10 routing mismatch fix

Changes in v2.3:
  - Fixed CHECK 10: now detects scene_archetype routing mismatch instead
    of penalizing packaging_geometry=BOX on vertical products (false negative).
    BOX is valid for secondary carton rendering of vertical containers.

Changes in v2.2:
  - Added CHECK 9:  SKU.csv package_type ↔ unit_count label consistency
  - Added CHECK 10: Vertical container → T_BOTTLE_BOX routing validation
  - Added CHECK 11: accent_hex contrast ratio vs white minimum
  - Added CHECK 12: SKU.csv ↔ JSON record existence check
  - Extended VerificationResult with sku_registry_match, template_validated, checks_passed/total
  - Raised production confidence threshold: 0.70 → 0.75
  - Added SKU_REGISTRY (SKU.csv) cross-check alongside master.json
"""

import re
import csv
import math
from typing import TypedDict
from pathlib import Path
import json

# =============================================
# SSOT DATA LOADERS (for cross-validation)
# =============================================

_SSOT_MASTER_PATH = Path("SSOT/master.json")
_SKU_CSV_PATH = Path("SSOT/SKU.csv")
_ssot_cache: dict | None = None
_sku_csv_cache: dict | None = None


def _load_ssot() -> dict:
    global _ssot_cache
    if _ssot_cache is not None:
        return _ssot_cache
    if _SSOT_MASTER_PATH.exists():
        with open(_SSOT_MASTER_PATH, "r", encoding="utf-8") as f:
            _ssot_cache = json.load(f)
    else:
        _ssot_cache = {}
    return _ssot_cache


def _load_sku_csv() -> dict:
    """
    Load SSOT/SKU.csv keyed by picture filename.
    Returns: { "379-min.jpg": { "package_type": "bottles", ... }, ... }
    """
    global _sku_csv_cache
    if _sku_csv_cache is not None:
        return _sku_csv_cache
    _sku_csv_cache = {}
    if not _SKU_CSV_PATH.exists():
        return _sku_csv_cache
    with open(_SKU_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pic = row.get("picture", "").strip()
            if pic:
                _sku_csv_cache[pic] = {
                    "package_type":        row.get("package_type", "").strip().lower(),
                    "primary_geometry":    row.get("primary_geometry", "").strip(),
                    "unit_count_standard": row.get("unit_count_standard", "").strip(),
                    "dosage_type":         row.get("dosage_type", "").strip(),
                }
    return _sku_csv_cache


# =============================================
# COLOR UTILITIES
# =============================================

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int] | None:
    """Convert #RRGGBB or RRGGBB to (R, G, B) tuple. Returns None on failure."""
    h = hex_color.lstrip("#").upper()
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    if len(h) != 6:
        return None
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return None


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG relative luminance formula."""
    def f(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast_ratio(hex1: str, hex2: str) -> float:
    """WCAG contrast ratio between two hex colors."""
    rgb1 = _hex_to_rgb(hex1)
    rgb2 = _hex_to_rgb(hex2)
    if not rgb1 or not rgb2:
        return 1.0
    l1 = _relative_luminance(rgb1)
    l2 = _relative_luminance(rgb2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# =============================================
# PACKAGE TYPE CLASSIFICATION
# =============================================

_VERTICAL_PACKAGE_TYPES = {"bottles", "bottle", "vials", "vial", "inhalers", "inhaler", "pens", "pen"}
_HORIZONTAL_PACKAGE_TYPES = {"sachets", "sachet", "tubes", "tube"}
_SOLID_ORAL_TYPES = {"pills", "pill", "packs", "pack", "boxes", "box", "strips", "strip", "units", "unit"}

# Expected unit_count labels per package_type
_EXPECTED_LABELS = {
    **{t: "Pills" for t in _SOLID_ORAL_TYPES},
    "vials":    "Vials",
    "vial":     "Vial",
    "tubes":    "Tubes",
    "tube":     "Tube",
    "sachets":  "Sachets",
    "sachet":   "Sachet",
    "pens":     "Pens",
    "pen":      "Pen",
    "inhalers": "Inhalers",
    "inhaler":  "Inhaler",
    "bottles":  "Bottles",
    "bottle":   "Bottle",
    "blisters": "Blisters",
    "blister":  "Blister",
}


# =============================================
# VERIFICATION RESULT TYPE (v2.2)
# =============================================

class VerificationResult(TypedDict):
    data: dict
    confidence: float
    warnings: list[str]
    verified: bool
    sku_registry_match: bool  # SKU found in SKU.csv
    template_validated: bool  # Template routing is consistent with SKU.csv
    checks_passed: int
    checks_total: int


# =============================================
# AGENT 2: VERIFIER (Production v2.2)
# =============================================

# Verification confidence threshold for production clearance
PRODUCTION_CONFIDENCE_THRESHOLD = 0.75  # Raised from 0.70 in v2.1


def agent_2_verifier(data: dict) -> VerificationResult:
    """
    Deterministic heuristic verifier for passport v2.1 data.
    Returns confidence score (0.0-1.0) and list of warnings.

    Weight table (v2.2):
      CHECK 1:  active_ingredient == product_name      -> -0.15
      CHECK 2:  active_ingredient empty                -> -0.15
      CHECK 3:  primary_color == background_white       -> -0.30
      CHECK 4:  dosage no numeric value                 -> -0.20
      CHECK 5:  unit_count empty                        -> -0.10
      CHECK 6:  geometry ↔ template consistency         -> -0.20
      CHECK 7:  product_name empty                      -> -0.25
      CHECK 8:  SSOT master.json color cross-validation -> -0.10
      CHECK 9:  SKU.csv package_type↔unit_count label  -> -0.15  [NEW]
      CHECK 10: vertical container template validation  -> -0.15  [NEW]
      CHECK 11: accent_hex contrast ratio vs white      -> -0.10  [NEW]
      CHECK 12: SKU.csv ↔ JSON record existence         -> -0.10  [NEW]
    """
    warnings: list[str] = []
    confidence: float = 1.0
    checks_passed = 0
    checks_total = 12

    sku_id = data.get("sku_id", "")
    sku_csv = _load_sku_csv()
    sku_entry = sku_csv.get(sku_id, {})
    sku_registry_match = sku_id in sku_csv

    # CHECK 1: active_ingredient vs product_name (weight: -0.15)
    ai = data.get("active_ingredient") or ""
    pn = data.get("product_name") or ""
    if ai and ai.strip().lower() == pn.strip().lower():
        warnings.append("CHECK 1: active_ingredient identical to product_name — likely unfilled")
        confidence -= 0.15
    else:
        checks_passed += 1

    # CHECK 2: active_ingredient is empty (weight: -0.15)
    if not ai.strip():
        warnings.append("CHECK 2: active_ingredient is empty or null")
        confidence -= 0.15
    else:
        checks_passed += 1

    # CHECK 3: primary color == background white (weight: -0.30)
    palette = data.get("branding", {}).get("palette", {})
    primary = (palette.get("primary") or "").upper().lstrip("#")
    bg = (palette.get("background") or "").upper().lstrip("#")
    if primary in ("FFFFFF", "FFF") and bg in ("FFFFFF", "FFF"):
        warnings.append("CHECK 3: primary_color == background_white — invisible text risk")
        confidence -= 0.30
    elif bg not in ("FFFFFF", "FFF"):
        warnings.append(f"CHECK 3: background color #{bg} is not white — invalid package background")
        confidence -= 0.30
    else:
        checks_passed += 1

    # CHECK 4: dosage contains numeric value (weight: -0.20)
    dosage = data.get("label_content", {}).get("dosage_display") or ""
    if not re.search(r'\d', dosage):
        warnings.append(f"CHECK 4: dosage_display '{dosage}' contains no numeric value")
        confidence -= 0.20
    else:
        checks_passed += 1

    # CHECK 5: unit_count present (weight: -0.10)
    unit = data.get("label_content", {}).get("unit_count_display") or ""
    if not unit.strip():
        warnings.append("CHECK 5: unit_count_display is empty")
        confidence -= 0.10
    else:
        checks_passed += 1

    # CHECK 6: geometry ↔ product consistency (weight: -0.20)
    geom = str(data.get("packaging_geometry", "")).upper()
    product_name_lower = pn.lower()
    liquid_keywords = {"spray", "drops", "nasal", "inhaler", "solution", "injection", "syrup"}
    solid_geom = {"BOX", "BLISTER"}
    is_liquid_product = any(kw in product_name_lower for kw in liquid_keywords)
    
    # Exempt boxes/box/vials/vial package types from liquid BOX penalty (injections in cartons/vials are valid secondary boxes)
    is_exempt = False
    if sku_registry_match:
        pkg_type_c6 = sku_entry.get("package_type", "").lower()
        if pkg_type_c6 in {"boxes", "box", "vials", "vial"}:
            is_exempt = True
            
    if is_liquid_product and geom in solid_geom and not is_exempt:
        warnings.append(f"CHECK 6: geometry '{geom}' inconsistent with liquid product '{pn[:40]}'")
        confidence -= 0.20
    else:
        checks_passed += 1

    # CHECK 7: product_name not empty (weight: -0.25)
    if not pn.strip():
        warnings.append("CHECK 7: product_name is empty — core identity missing")
        confidence -= 0.25
    else:
        checks_passed += 1

    # CHECK 8: SSOT master.json color cross-validation (weight: -0.10)
    if sku_id and primary:
        ssot = _load_ssot()
        registry = ssot.get("sku_registry", {})
        ssot_entry = registry.get(sku_id, {})
        ssot_palette = ssot_entry.get("branding", {}).get("palette", {})
        ssot_primary = (ssot_palette.get("primary") or "").upper().lstrip("#")
        if ssot_primary and ssot_primary != primary:
            warnings.append(
                f"CHECK 8: primary_color #{primary} differs from SSOT/master.json #{ssot_primary}"
            )
            confidence -= 0.10
        else:
            checks_passed += 1
    else:
        checks_passed += 1  # No SSOT entry — not a failure, just unverifiable

    # CHECK 9: SKU.csv package_type ↔ unit_count label consistency (weight: -0.15) [NEW]
    template_validated = True
    if sku_registry_match:
        pkg_type = sku_entry.get("package_type", "").lower()
        expected_label = _EXPECTED_LABELS.get(pkg_type)
        unit_display = unit.strip()
        if expected_label and unit_display:
            # Extract label word from unit_count_display (e.g. "30 Pills" → "Pills")
            parts = unit_display.split()
            label_in_display = parts[-1] if len(parts) >= 2 else ""
            # Acceptable singular forms
            singular_map = {
                "Vials": "Vial", "Sachets": "Sachet", "Bottles": "Bottle", 
                "Tubes": "Tube", "Pens": "Pen", "Inhalers": "Inhaler", 
                "Blisters": "Blister", "Boxes": "Box", "Strips": "Strip",
                "Packs": "Pack", "Units": "Unit"
            }
            acceptable = {expected_label}
            if expected_label in singular_map:
                acceptable.add(singular_map[expected_label])
            for p_lbl, s_lbl in singular_map.items():
                if expected_label == s_lbl:
                    acceptable.add(p_lbl)
            if label_in_display and label_in_display not in acceptable:
                warnings.append(
                    f"CHECK 9: unit_count label '{label_in_display}' doesn't match "
                    f"expected '{expected_label}' for package_type '{pkg_type}'"
                )
                confidence -= 0.15
            else:
                checks_passed += 1
        else:
            checks_passed += 1  # Unverifiable — not a failure
    else:
        checks_passed += 1  # No SKU.csv entry — not a failure

    # CHECK 10: Vertical container → T_BOTTLE_BOX routing validation (weight: -0.15) [v2 P8.0]
    # FIX (P8.0): old check penalized packaging_geometry=BOX for vertical products — invalid,
    # because BOX is correct for secondary carton rendering. New check: detect genuine routing
    # mismatch by verifying scene_archetype is not a blister/pill scene for vertical products.
    if sku_registry_match:
        pkg_type_c10 = sku_entry.get("package_type", "").lower()
        primary_geom_c10 = sku_entry.get("primary_geometry", "").lower()
        geom_js_c10 = geom.upper()

        VERTICAL_PKG_TYPES_C10 = {"bottles", "bottle", "vials", "vial", "inhalers", "inhaler", "pens", "pen"}
        VERTICAL_CSV_GEOMS_C10 = {
            "bottle (hdpe)", "bottle (amber glass)", "glass type i",
            "inhaler (hfa/generic)", "vial (glass type i)"
        }
        VERTICAL_JSON_GEOMS_C10 = {"BOTTLE", "VIAL", "AMPOULE", "DROPPER", "INHALER", "SPRAY", "PEN"}

        is_vertical_c10 = (
            pkg_type_c10 in VERTICAL_PKG_TYPES_C10
            or primary_geom_c10 in VERTICAL_CSV_GEOMS_C10
            or geom_js_c10 in VERTICAL_JSON_GEOMS_C10
        )

        render_config_c10 = data.get("render_config", {})
        scene_c10 = render_config_c10.get("scene_archetype", "")
        # Blister/pill scenes are wrong for vertical (bottle/vial/inhaler) products
        BLISTER_SCENES = {"slim_blister_carton", "thick_blister_carton", "flat_strip_carton"}

        if is_vertical_c10 and scene_c10 in BLISTER_SCENES:
            warnings.append(
                f"CHECK 10: vertical container (pkg_type='{pkg_type_c10}') "
                f"has blister scene_archetype='{scene_c10}' — routing mismatch, "
                f"expected bottle/vial scene"
            )
            template_validated = False
            confidence -= 0.15
        else:
            checks_passed += 1
    else:
        checks_passed += 1  # No SKU.csv entry

    # CHECK 11: accent_hex contrast ratio vs white minimum (weight: -0.10) [NEW]
    accent = palette.get("accent") or ""
    if accent:
        ratio = contrast_ratio(accent, "#FFFFFF")
        if ratio < 1.5:
            warnings.append(
                f"CHECK 11: accent_hex {accent} has very low contrast vs white "
                f"(ratio={ratio:.2f}) — risk of invisible accent stripe"
            )
            confidence -= 0.10
        else:
            checks_passed += 1
    else:
        checks_passed += 1  # No accent — not a failure

    # CHECK 12: SKU.csv ↔ JSON record existence (weight: -0.10) [NEW]
    if not sku_registry_match and sku_id:
        warnings.append(
            f"CHECK 12: sku_id '{sku_id}' not found in SSOT/SKU.csv — "
            f"package_type and unit_count_standard cannot be validated"
        )
        confidence -= 0.10
    else:
        checks_passed += 1

    final_confidence = round(max(0.0, confidence), 2)

    return VerificationResult(
        data=data,
        confidence=final_confidence,
        warnings=warnings,
        verified=final_confidence >= PRODUCTION_CONFIDENCE_THRESHOLD,
        sku_registry_match=sku_registry_match,
        template_validated=template_validated,
        checks_passed=checks_passed,
        checks_total=checks_total,
    )
