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
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Keys known to be leaked/blocked (e.g. previously committed to source). Dropped
# from the candidate list so a stale machine-level env var can't shadow a good key.
LEAKED_GEMINI_KEYS = {"AIzaSyBgGJqlRJORAnuxjPfR6u2ljsMO_zeqNHg"}


def _read_gemini_keys_from_env_file(path: str) -> list[str]:
    found = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(("GEMINI_API_KEY=", "GEMINI_API_KEY_OLD=")):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            found.append(val)
        except Exception:
            pass
    return found


def get_gemini_api_keys() -> list[str]:
    """
    Retrieve Gemini API keys, in preference order:
      1) project-local .env (gitignored)   2) process env   3) C:/pharma_v2/.env
    Known-leaked keys are filtered out; project .env wins so a stale machine-level
    env var cannot shadow a freshly provided key. No hardcoded fallback (a committed
    key gets flagged as leaked); if none configured, caller -> NEEDS_MANUAL.
    """
    candidates = []
    # 1) project-local .env (preferred)
    candidates += _read_gemini_keys_from_env_file(os.path.join(PROJECT_ROOT, ".env"))
    # 2) process environment
    env_k = os.environ.get("GEMINI_API_KEY")
    if env_k:
        candidates.append(env_k)
    # 3) external fallback
    candidates += _read_gemini_keys_from_env_file("C:/pharma_v2/.env")

    keys, seen = [], set()
    for c in candidates:
        if c and c not in seen and c not in LEAKED_GEMINI_KEYS:
            seen.add(c)
            keys.append(c)
    return keys


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


class JudgeVerdict(BaseModel):
    verdict: str = Field(description="Must be exactly one of: 'SUPPORTED', 'WEAK', 'UNSUPPORTED'")
    quote: str = Field(description="A verbatim sentence or sentences from the provided abstract that supports the statement. MUST be an exact substring of the abstract. Leave empty if UNSUPPORTED.")
    reason: str = Field(description="A brief explanation of the verdict based on the abstract content.")

def assess_claim(statement: str, abstract: str) -> str:
    """
    Assess if statement is supported by abstract.
    Returns: SUPPORTED, WEAK, UNSUPPORTED, or NEEDS_MANUAL
    """
    if not abstract:
        return "NEEDS_MANUAL"

    # Normalize aliases/synonyms at keyword extraction stage
    def normalize_word(w):
        w = w.lower()
        if w in ("nicotinamide", "niacinamide", "nicotinic", "niacin"):
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
        "niacinamide", "peptide", "peptides", "caffeine", "hyaluronic",
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
    
    # Cheap pre-filter
    if overlap_ratio < 0.15:
        return "UNSUPPORTED"

    # Check judge cache
    cache_dir = os.path.join(PROJECT_ROOT, "ops", "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "judge_cache.json")
    
    content_to_hash = f"{statement.strip()}|||{abstract.strip()}"
    cache_key = hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest()
    
    cached_result = None
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_db = json.load(f)
            cached_result = cache_db.get(cache_key)
        except Exception:
            pass
            
    if cached_result:
        verdict = cached_result.get("verdict", "UNSUPPORTED").strip().upper()
        quote = cached_result.get("quote", "").strip()
        reason = cached_result.get("reason", "")
        print(f"[Cached Judge API] Fact statement: {statement[:60]}...")
        print(f"  Verdict: {verdict}")
        print(f"  Quote: '{quote}'")
        print(f"  Reason: {reason}")
        
        if verdict not in ("SUPPORTED", "WEAK", "UNSUPPORTED"):
            verdict = "UNSUPPORTED"
            
        if verdict in ("SUPPORTED", "WEAK"):
            if not quote:
                return "UNSUPPORTED"
            def normalize_text(t):
                return re.sub(r'\s+', ' ', t).strip().lower()
            norm_quote = normalize_text(quote)
            norm_abstract = normalize_text(abstract)
            if norm_quote not in norm_abstract:
                return "UNSUPPORTED"
        return verdict

    # Retrieve API keys
    keys = get_gemini_api_keys()
    if not keys:
        print("  Judge unavailable: no GEMINI_API_KEY configured. Returning NEEDS_MANUAL.")
        return "NEEDS_MANUAL"
    key_index = 0
    api_key = keys[key_index]

    # Run LLM-as-judge
    prompt = f"""You are a scientific verification judge for cosmetology claims.
Your job is to assess if the statement is supported by the abstract text provided.

Statement:
{statement}

Abstract:
{abstract}

Rules:
1. Verdict must be:
   - "SUPPORTED" if the statement is directly, explicitly confirmed in a primary study (clinical trial, RCT, in vitro/in vivo experiment, etc.) described in the abstract.
   - "WEAK" if the statement is supported indirectly, or mentioned as general background/discussion, or supported in a review paper/general discussion, or has minor discrepancies.
   - "UNSUPPORTED" if the abstract does not contain evidence for the statement, doesn't mention it, or contradicts it.
2. If the verdict is "SUPPORTED" or "WEAK", you MUST provide the exact verbatim quote(s) from the abstract that supports the statement.
3. The quote MUST be an exact case-sensitive and punctuation-sensitive substring of the abstract. Do NOT summarize or paraphrase.
4. Rely ONLY on the provided abstract text. Do NOT use external knowledge.
5. If the abstract does not contain a sentence that can be quoted verbatim as support, the verdict MUST be "UNSUPPORTED".
"""

    retries = 6
    delay = 1.0
    for attempt in range(retries):
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=JudgeVerdict,
                    temperature=0.0
                ),
            )
            
            # Parse output
            result = json.loads(response.text)
            verdict = result.get("verdict", "UNSUPPORTED").strip().upper()
            quote = result.get("quote", "").strip()
            reason = result.get("reason", "")
            
            print(f"[Judge API] Fact statement: {statement[:60]}...")
            print(f"  Verdict: {verdict}")
            print(f"  Quote: '{quote}'")
            print(f"  Reason: {reason}")
            
            # Save to cache
            try:
                cache_db = {}
                if os.path.exists(cache_path):
                    with open(cache_path, "r", encoding="utf-8") as f:
                        cache_db = json.load(f)
                cache_db[cache_key] = {"verdict": verdict, "quote": quote, "reason": reason}
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache_db, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
            
            if verdict not in ("SUPPORTED", "WEAK", "UNSUPPORTED"):
                verdict = "UNSUPPORTED"
                
            if verdict in ("SUPPORTED", "WEAK"):
                if not quote:
                    print("  Warning: Supported/Weak verdict returned but quote is empty. Forcing UNSUPPORTED.")
                    return "UNSUPPORTED"
                
                # Grounding check: verify that quote is a substring of the abstract
                def normalize_text(t):
                    return re.sub(r'\s+', ' ', t).strip().lower()
                
                norm_quote = normalize_text(quote)
                norm_abstract = normalize_text(abstract)
                
                if norm_quote not in norm_abstract:
                    print("  Warning: Grounding check failed. Quoted text is not a substring of the abstract. Forcing UNSUPPORTED.")
                    print(f"  Normalized Quote: '{norm_quote}'")
                    return "UNSUPPORTED"
                    
            return verdict
            
        except Exception as e:
            err_msg = str(e)
            is_quota = "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower()
            is_transient = is_quota or any(x in err_msg for x in ["503", "UNAVAILABLE", "high demand", "Service Unavailable"])

            # Rotate to an alternate key first if one is available.
            if is_quota and key_index < len(keys) - 1:
                key_index += 1
                api_key = keys[key_index]
                print(f"  Quota hit. Rotating to API key index {key_index}...")
                continue

            # Free-tier 429s report a short per-minute retryDelay even though the
            # message also lists PerDay metrics; honour that delay instead of bailing.
            sleep_time = None
            for pat in (r'retry in (\d+(?:\.\d+)?)\s*s',
                        r'retryDelay["\']?\s*[:=]\s*["\']?(\d+(?:\.\d+)?)',
                        r'seconds:\s*(\d+)'):
                m = re.search(pat, err_msg, re.IGNORECASE)
                if m:
                    sleep_time = float(m.group(1)) + 2.0
                    break
            if sleep_time is None and is_quota:
                sleep_time = 30.0

            BACKOFF_CAP = 65.0
            if is_transient and attempt < retries - 1 and sleep_time is not None and sleep_time <= BACKOFF_CAP:
                print(f"  Rate-limited (429/transient). Backing off {sleep_time:.0f}s (attempt {attempt + 1}/{retries})...")
                time.sleep(sleep_time)
                continue

            if is_quota and (sleep_time is None or sleep_time > BACKOFF_CAP):
                print(f"  Quota exhausted with no short retry window: {err_msg[:120]}... -> NEEDS_MANUAL.")
            else:
                print(f"  Error calling Gemini Client: {e}. Falling back to NEEDS_MANUAL.")
            return "NEEDS_MANUAL"

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
