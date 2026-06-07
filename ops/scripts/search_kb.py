import csv
import os
import re
import numpy as np
from schemas.analysis_passport import AnalysisPassport

def load_kb(csv_path):
    """
    Загружает базу знаний из CSV.
    Ключ - picture-id (имя файла).
    """
    data = {}
    if not os.path.exists(csv_path):
        return data
        
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get("picture-id")
            if not key:
                continue
            
            data[key] = {
                "name": row.get("name"),
                "group_type": row.get("group_type"),
                "package_type": row.get("package_type"),
                "dosage_type": row.get("dosage_type"),
                "package_id": row.get("package_id")
            }
    return data

def kb_lookup(passport, kb_data):
    """
    Поиск в KB в режиме реконструкции.
    Возвращает эталонные данные для планирования дизайна.
    """
    filename = passport["meta"]["source_file"]
    record = kb_data.get(filename)

    if not record:
        passport["kb"] = {
            "verified_name": None,
            "design_guideline": "generic_reconstruction"
        }
        if "validation" not in passport:
            passport["validation"] = {"status": "pending", "errors": []}
            
        passport["validation"]["status"] = "review_needed"
        passport["validation"]["errors"].append("KB_NOT_FOUND")
        return passport

    # Маппинг на схему 3.0
    passport["kb"] = {
        "verified_name": record.get("name"),
        "design_guideline": f"Follow style for {record.get('group_type')} packaging. ID: {record.get('package_id')}"
    }
    return passport
import math

from utils.dosage_parser import extract_dosage

def numeric_similarity(obs_val, kb_val) -> float:
    """
    Устойчивая к масштабам логарифмическая дистанция (Scale-Invariant).
    Разница 5мг vs 10мг (100%) >> Разница 500мг vs 510мг (2%).
    """
    if obs_val is None or kb_val is None:
        return 0.0
        
    obs_n = extract_dosage(obs_val)
    kb_n = extract_dosage(kb_val)
    
    if obs_n is None or kb_n is None:
        return 0.0
        
    # Нормализующий фактор (2.0 означает, что разница в e^2 раз сводит скор к 0)
    norm_factor = 2.0 
    
    # Считаем логарифмическую дистанцию
    distance = abs(math.log(obs_n + 1) - math.log(kb_n + 1))
    
    # Возвращаем score (1.0 - идеал, уходит в минус при жестком конфликте)
    return 1.0 - (distance / norm_factor)

def search_candidates(passport: AnalysisPassport, kb_data: dict):
    """
    INDUSTRIAL RETRIEVAL ENGINE V3.0 (Probabilistic Ranking).
    Retreival ≠ Search | Scoring ≠ Filtering
    """
    from schemas.kb_models import SKUCandidate
    from rapidfuzz import fuzz
    import numpy as np
    import math

    if not kb_data:
        return [], False

    # 1. DYNAMIC TOP-K CALCULATION
    top_k = min(10, max(3, int(math.log2(len(kb_data) + 1))))
    
    brand_query = passport.extracted_zones.get("brand_zone", {}).raw_text or ""
    dosage_query = passport.extracted_zones.get("dosage_zone", {}).raw_text or ""
    ocr_conf = passport.extracted_zones.get("brand_zone", {}).confidence or 0.0
    
    brand_clean = brand_query.lower().strip()
    hypotheses = []
    
    for sku_id, info in kb_data.items():
        # L0: CONFIDENCE-AWARE HARD FILTERING
        n_sim = numeric_similarity(dosage_query, info.get("dosage_type"))
        
        # Режектим только при высокой уверенности OCR и жестком конфликте (score < -0.5)
        if ocr_conf > 0.9 and n_sim < -0.5:
            continue
            
        # L1: FEATURE EXTRACTION (Stateless)
        features = {
            "numeric_score": float(n_sim),
            "lexical_score": float(fuzz.ratio(brand_clean, info.get("name", "").lower()) / 100.0),
            "semantic_score": float(fuzz.WRatio(brand_clean, info.get("name", "").lower()) / 100.0),
            "visual_score": 1.0 if passport.geometry_type.lower() in str(info.get("package_type", "")).lower() else 0.0
        }
        
        # HEURISTIC SCORING FORMULA (Option A - Temporary)
        total_score = (
            features["lexical_score"] * 0.3 +
            features["numeric_score"] * 0.4 +
            features["semantic_score"] * 0.2 +
            features["visual_score"] * 0.1
        )
        
        hypotheses.append((total_score, sku_id, info, features))

    # Сортировка
    hypotheses.sort(key=lambda x: x[0], reverse=True)
    top_hypotheses = hypotheses[:top_k]
    
    if not top_hypotheses:
        return [], False, []

    # L2: CALIBRATION LAYER (Softmax)
    scores = np.array([h[0] for h in top_hypotheses])
    exp_scores = np.exp(scores - np.max(scores)) # Stability
    probs = exp_scores / exp_scores.sum()
    
    # Check for Ambiguity
    is_ambiguous = False
    if len(probs) >= 2 and (probs[0] - probs[1]) < 0.15:
        is_ambiguous = True

    candidates = []
    telemetry_data = []
    
    for i, (total_score, sku_id, info, f_vec) in enumerate(top_hypotheses):
        candidate = SKUCandidate(
            sku_id=sku_id,
            name=info["name"],
            dosage_type=info.get("dosage_type"),
            package_type=info.get("package_type"),
            group_type=info.get("group_type")
        )
        candidates.append(candidate)
        
        telemetry_data.append({
            "candidate": candidate.model_dump(),
            "score": float(total_score),
            "feature_vector": f_vec
        })
        
    return candidates, is_ambiguous, telemetry_data
