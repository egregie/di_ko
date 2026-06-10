import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import re
import socket
import hashlib
import datetime

# Happy Eyeballs / IPv6 connectivity workaround: Force IPv4 for eutils.ncbi.nlm.nih.gov
orig_getaddrinfo = socket.getaddrinfo

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host == "eutils.ncbi.nlm.nih.gov" and family == 0:
        return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    return orig_getaddrinfo(host, port, family, type, proto, flags)

socket.getaddrinfo = custom_getaddrinfo

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Process-level rate limiter: NCBI requests limit is <= 3 req/s
_last_ncbi_request_time = 0.0

def throttle_ncbi():
    global _last_ncbi_request_time
    now = time.time()
    elapsed = now - _last_ncbi_request_time
    wait_time = 0.35 - elapsed
    if wait_time > 0:
        time.sleep(wait_time)
    _last_ncbi_request_time = time.time()



# Determine paths relative to this file (ops/scripts/lib/evidence.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CACHE_DIR = os.path.join(PROJECT_ROOT, "ops", "cache", "eutils")
os.makedirs(CACHE_DIR, exist_ok=True)

def log_api_call(url: str, status: str):
    """
    Log api calls to verify_api_calls.log.
    """
    log_path = os.path.join(PROJECT_ROOT, "ops", "logs", "verify_api_calls.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | GET | {url} | {status}\n")

def clean_statement_key(text):
    # Normalize statement string
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

def check_source(identifier: str, force_live: bool = False) -> dict:
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
        
    # Check cache if not forced live
    if not force_live and os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                if cached_data.get("fetched") is True:
                    return cached_data
        except Exception:
            pass

    # Fetch from API
    result = {"exists": False, "title": "", "pubtype": [], "abstract": ""}
    fetched_url = ""
    
    if is_pmid:
        # Entrez esummary
        summary_url = f"{EUTILS}/esummary.fcgi?db=pubmed&id={identifier}&retmode=json&tool=ym_proskin&email=admin@ym-proskin.local"
        fetched_url = summary_url
        try:
            throttle_ncbi()
            req = urllib.request.Request(
                summary_url, 
                headers={'User-Agent': 'ym-proskin-collector/1.0 (mailto:admin@ym-proskin.local)'}
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                log_api_call(summary_url, "200")
                data = json.load(r)
            
            rec = data.get("result", {}).get(str(identifier))
            if rec and not rec.get("error"):
                result["exists"] = True
                result["title"] = rec.get("title", "")
                result["pubtype"] = rec.get("pubtype", [])
                
                # Fetch abstract too
                abstract_url = f"{EUTILS}/efetch.fcgi?db=pubmed&id={identifier}&rettype=abstract&retmode=text&tool=ym_proskin&email=admin@ym-proskin.local"
                throttle_ncbi()
                req_abs = urllib.request.Request(
                    abstract_url, 
                    headers={'User-Agent': 'ym-proskin-collector/1.0 (mailto:admin@ym-proskin.local)'}
                )
                try:
                    with urllib.request.urlopen(req_abs, timeout=20) as r_abs:
                        log_api_call(abstract_url, "200")
                        result["abstract"] = r_abs.read().decode('utf-8').strip()
                except urllib.error.HTTPError as e:
                    log_api_call(abstract_url, str(e.code))
                except Exception:
                    log_api_call(abstract_url, "ERROR")
            
        except urllib.error.HTTPError as e:
            log_api_call(summary_url, str(e.code))
            print(f"Error fetching PMID {identifier}: HTTP {e.code}")
            result["exists"] = False
        except Exception as e:
            log_api_call(summary_url, "ERROR")
            print(f"Error fetching PMID {identifier}: {e}")
            result["exists"] = False
            
    else:
        # Crossref DOI
        url = f"https://api.crossref.org/works/{urllib.parse.quote(identifier)}"
        fetched_url = url
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'mailto:admin@ym-proskin.local'})
            with urllib.request.urlopen(req, timeout=20) as r:
                log_api_call(url, "200")
                data = json.load(r)
            
            msg = data.get("message", {})
            title_list = msg.get("title", [])
            result["exists"] = True
            result["title"] = title_list[0] if title_list else ""
            result["pubtype"] = [msg.get("type", "")]
            # Note: Crossref works don't always contain abstracts, keep empty
            result["abstract"] = ""
            
        except urllib.error.HTTPError as e:
            log_api_call(url, str(e.code))
            print(f"Error fetching DOI {identifier}: HTTP {e.code}")
            result["exists"] = False
        except Exception as e:
            log_api_call(url, "ERROR")
            print(f"Error fetching DOI {identifier}: {e}")
            result["exists"] = False
            
    # Cache result if it exists
    if result.get("exists"):
        result["fetched"] = True
        result["fetched_at"] = datetime.datetime.utcnow().isoformat() + "Z"
        result["http_status"] = 200
        result["source_url"] = fetched_url
        
        # Calculate raw hash of the response content
        content_to_hash = f"{result.get('title','')}\n{result.get('abstract','')}\n{','.join(result.get('pubtype',[]))}"
        result["raw_hash"] = hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest()

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Cache write error: {e}")
        
    return result


def assess_claim(statement: str, abstract: str) -> str:
    """
    Assess if statement is supported by abstract.
    Returns: SUPPORTED, WEAK, UNSUPPORTED, or NEEDS_MANUAL
    """
    # If abstract is empty/missing (e.g. books or non-PubMed items), it needs manual audit
    if not abstract:
        return "NEEDS_MANUAL"

    # Normalize aliases/synonyms at keyword extraction stage
    def normalize_word(w):
        w = w.lower()
        if w in ("nicotinamide", "niacinamide", "nicotinic"):
            return "niacinamide"
        if w in ("ascorbic", "ascorbate", "ascorbyl", "ascorbyl_glucoside"):
            return "ascorbic"
        if w in ("retinol", "tretinoin", "adapalene", "tazarotene", "retinaldehyde", "palmitate", "retinoid", "retinoids"):
            return "retinoid"
        if w in ("matrixyl", "argireline", "ghk", "peptides", "peptide", "tripeptide", "pentapeptide", "hexapeptide", "tetrapeptide"):
            return "peptide"
        return w


    # Preprocess statement and abstract words for a general overlap heuristic
    def get_keywords(text):
        # keeps words of length >= 3
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Filter out common stop words
        stopwords = {
            "the", "and", "for", "with", "this", "that", "from", "are", "were", 
            "was", "been", "has", "have", "had", "not", "but", "efficacy", "safety",
            "study", "clinical", "results", "patients", "treatment", "effects"
        }
        return set(normalize_word(w) for w in words if w not in stopwords)

    s_words = get_keywords(statement)
    a_words = get_keywords(abstract)

    # Core subjects/ingredients in cosmetology
    core_subjects = {
        "vitamin", "vitamins", "retinol", "tretinoin", "adapalene", "tazarotene", 
        "retinaldehyde", "palmitate", "retinoid", "retinoids", "ascorbic", "ascorbate",
        "niacinamide", "acid", "acids", "peptide", "peptides", "caffeine", "hyaluronic",
        "salicylic", "glycolic", "lactic", "benzoyl", "peroxide", "sulfur", "clindamycin",
        "azelaic", "ghk", "matrixyl", "argireline", "tripeptide", "pentapeptide", "hexapeptide", "tetrapeptide"
    }
    # map core_subjects through normalize_word
    core_subjects = set(normalize_word(w) for w in core_subjects)
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
    else:
        return "UNSUPPORTED"

def evidence_ok(level: str, pubtype: list) -> bool:
    """
    Check if publication types support the required EBM level.
    """
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
