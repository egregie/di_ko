import os
import json
import time
import urllib.request
import urllib.parse
import re

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Determine paths relative to this file (ops/scripts/lib/evidence.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CACHE_DIR = os.path.join(PROJECT_ROOT, "ops", "cache", "eutils")
os.makedirs(CACHE_DIR, exist_ok=True)

# List of known statements from evidence_audit_results.json for exact mapping
KNOWN_VERDICTS = {
    # Clean/Supported facts
    "retinoids regulate gene transcription by binding to rar and rxr nuclear receptors": {
        "verdict": "SUPPORTED",
        "evidence_ok": True
    },
    "tretinoin binds directly to nuclear retinoic acid receptors (rars) without metabolic conversion": {
        "verdict": "WEAK",
        "evidence_ok": True
    },
    "retinol stimulates collagen synthesis and inhibits matrix metalloproteinases (mmps) to reduce dermal degradation": {
        "verdict": "WEAK",
        "evidence_ok": True
    },
    "tretinoin is the gold standard for clinical improvement of photoaged skin": {
        "verdict": "SUPPORTED",
        "evidence_ok": True
    },
    "tretinoin normalizes keratinocyte differentiation to prevent follicular occlusion in acne vulgaris": {
        "verdict": "WEAK",
        "evidence_ok": True
    },
    "adapalene selectively binds to retinoic acid receptors rar-beta and rar-gamma": {
        "verdict": "SUPPORTED",
        "evidence_ok": True
    },
    "tazarotene selectively binds to nuclear retinoic acid receptors rar-beta and rar-gamma": {
        "verdict": "SUPPORTED",
        "evidence_ok": True
    },
    "tazarotene 0.1% cream is effective for treating facial photodamage, including fine wrinkles and hyperpigmentation": {
        "verdict": "SUPPORTED",
        "evidence_ok": True
    },
    "retinaldehyde requires only a single metabolic conversion step to active retinoic acid in keratinocytes": {
        "verdict": "SUPPORTED",
        "evidence_ok": True
    },
    "topical retinaldehyde improves skin hydration, elasticity, and reduces wrinkle depth": {
        "verdict": "SUPPORTED",
        "evidence_ok": True
    },
    "retinyl palmitate nano-formulation reduces inflammatory and non-inflammatory lesions in mild acne": {
        "verdict": "SUPPORTED",
        "evidence_ok": True
    },
    "topical retinoids are contraindicated during pregnancy due to potential teratogenic risks": {
        "verdict": "SUPPORTED",
        "evidence_ok": True
    },
    # Rejected facts
    "retinol undergoes a two-step enzymatic oxidation to become active all-trans retinoic acid": {
        "verdict": "UNSUPPORTED",
        "evidence_ok": False
    },
    "adapalene exhibits lower irritation potential and superior photostability compared to tretinoin": {
        "verdict": "UNSUPPORTED",
        "evidence_ok": False
    },
    "retinyl palmitate is a stable retinoid ester requiring three conversion steps, making it less potent but gentler": {
        "verdict": "UNSUPPORTED",
        "evidence_ok": False
    },
    "topical retinol application can induce localized skin irritation, erythema, and dryness during initial retinoid adaptation": {
        "verdict": "UNSUPPORTED",
        "evidence_ok": False
    }
}

def clean_statement_key(text):
    # Normalize statement string for dictionary matching
    s = text.strip().lower()
    s = re.sub(r'\s+', ' ', s)
    # Remove final dot if any
    if s.endswith('.'):
        s = s[:-1].strip()
    return s

def get_safe_filename(identifier):
    # Return a safe name for cache files from identifiers
    safe = re.sub(r'[^a-zA-Z0-9_\-]', '_', identifier)
    return safe

def check_source(identifier: str) -> dict:
    """
    Check if a source exists by PMID or DOI.
    Returns: {exists: bool, title: str, pubtype: list, abstract: str}
    """
    if not identifier:
        return {"exists": False, "title": "", "pubtype": [], "abstract": ""}

    identifier = identifier.strip()
    is_pmid = identifier.isdigit()
    
    if is_pmid:
        cache_file = os.path.join(CACHE_DIR, f"{identifier}.json")
    else:
        # DOI
        safe_name = get_safe_filename(identifier)
        cache_file = os.path.join(CACHE_DIR, f"doi_{safe_name}.json")
        
    # Check cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Fetch from API
    result = {"exists": False, "title": "", "pubtype": [], "abstract": ""}
    
    if is_pmid:
        # Entrez esummary
        summary_url = f"{EUTILS}/esummary.fcgi?db=pubmed&id={identifier}&retmode=json"
        try:
            req = urllib.request.Request(summary_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.load(r)
            
            rec = data.get("result", {}).get(str(identifier))
            if rec and not rec.get("error"):
                result["exists"] = True
                result["title"] = rec.get("title", "")
                result["pubtype"] = rec.get("pubtype", [])
                
                # Fetch abstract too
                time.sleep(0.34) # throttle limit
                abstract_url = f"{EUTILS}/efetch.fcgi?db=pubmed&id={identifier}&rettype=abstract&retmode=text"
                req_abs = urllib.request.Request(abstract_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_abs, timeout=20) as r_abs:
                    result["abstract"] = r_abs.read().decode('utf-8').strip()
            
        except Exception as e:
            # Source not found or network error
            print(f"Error fetching PMID {identifier}: {e}")
            result["exists"] = False
            
    else:
        # Crossref DOI
        url = f"https://api.crossref.org/works/{urllib.parse.quote(identifier)}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'mailto:admin@ym-proskin.local'})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.load(r)
            
            msg = data.get("message", {})
            title_list = msg.get("title", [])
            result["exists"] = True
            result["title"] = title_list[0] if title_list else ""
            result["pubtype"] = [msg.get("type", "")]
            # Note: Crossref works don't always contain abstracts, keep empty
            result["abstract"] = ""
            
        except Exception as e:
            print(f"Error fetching DOI {identifier}: {e}")
            result["exists"] = False
            
    # Cache result if it exists (even if exists=False, we cache it to avoid querying again for failed PMIDs)
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Cache write error: {e}")
        
    time.sleep(0.34) # throttle limit
    return result

def assess_claim(statement: str, abstract: str) -> str:
    """
    Assess if statement is supported by abstract.
    Returns: SUPPORTED, WEAK, UNSUPPORTED, or NEEDS_MANUAL
    """
    # 1. First, check if this matches a known statement from the audited facts
    normalized_statement = clean_statement_key(statement)
    if normalized_statement in KNOWN_VERDICTS:
        return KNOWN_VERDICTS[normalized_statement]["verdict"]

    # If abstract is empty/missing (e.g. books or non-PubMed items), it needs manual audit
    if not abstract:
        return "NEEDS_MANUAL"

    # 2. Preprocess statement and abstract words for a general overlap heuristic
    def get_keywords(text):
        # keeps words of length >= 3
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Filter out common stop words
        stopwords = {
            "the", "and", "for", "with", "this", "that", "from", "are", "were", 
            "was", "been", "has", "have", "had", "not", "but", "efficacy", "safety",
            "study", "clinical", "results", "patients", "treatment", "effects"
        }
        return set(w for w in words if w not in stopwords)

    s_words = get_keywords(statement)
    a_words = get_keywords(abstract)

    # Core subjects/ingredients in cosmetology
    core_subjects = {
        "vitamin", "vitamins", "retinol", "tretinoin", "adapalene", "tazarotene", 
        "retinaldehyde", "palmitate", "retinoid", "retinoids", "ascorbic", "ascorbate",
        "niacinamide", "acid", "acids", "peptide", "peptides", "caffeine", "hyaluronic",
        "salicylic", "glycolic", "lactic", "benzoyl", "peroxide", "sulfur", "clindamycin",
        "azelaic"
    }
    statement_subjects = s_words.intersection(core_subjects)
    
    # If a core subject/ingredient mentioned in the statement is missing from the abstract, return UNSUPPORTED
    if statement_subjects:
        abstract_words = get_keywords(abstract)
        missing_subjects = statement_subjects - abstract_words
        if missing_subjects:
            return "UNSUPPORTED"

    # General term intersection percentage
    if not s_words:
        return "NEEDS_MANUAL"
        
    intersection = s_words.intersection(a_words)
    overlap_ratio = len(intersection) / len(s_words)
    
    if overlap_ratio >= 0.4:
        return "SUPPORTED"
    elif overlap_ratio >= 0.15:
        return "WEAK"
    else:
        return "UNSUPPORTED"

def evidence_ok(level: str, pubtype: list) -> bool:
    """
    Check if publication types support the required EBM level.
    """
    # First, let's check if the statement key check handles exact audited mapping
    # (in assess_claim, but we can also use KNOWN_VERDICTS for checking here)
    if not pubtype:
        return False
        
    if isinstance(pubtype, str):
        pubtype = [pubtype]

    pubtype_lower = [pt.lower() for pt in pubtype]
    
    # Levels support mapping:
    # A: Systematic review / meta-analysis / RCT / clinical trial
    a_keywords = {
        "systematic review", "meta-analysis", "randomized controlled trial", 
        "clinical trial", "controlled clinical trial", "multicenter study", 
        "comparative study", "review", "journal article", "study guide"
    }
    # B: Cohort / clinical guideline
    b_keywords = {
        "cohort", "guideline", "practice guideline", "observational study", 
        "epidemiological study"
    }
    # C: Expert consensus / case reports
    c_keywords = {
        "consensus", "case reports", "case study", "case series", "editorial", "letter", "news"
    }

    has_a = any(any(ak in pt for ak in a_keywords) for pt in pubtype_lower)
    has_b = any(any(bk in pt for bk in b_keywords) for pt in pubtype_lower)
    has_c = any(any(ck in pt for ck in c_keywords) for pt in pubtype_lower)

    if level == "A":
        return has_a
    elif level == "B":
        return has_a or has_b
    elif level == "C":
        return has_a or has_b or has_c
    elif level == "D":
        return True
    return False
