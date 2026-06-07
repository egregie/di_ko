import os
import json
import time
import urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

PMIDS = [
    32250551,  # Glycolic/Salicylic combo for acne (Level A, Clinical Study)
    19076192,  # Glycolic vs Salicylic-Mandelic peels for acne (Level A, Comparative Study)
    9537006,   # Salicylic acid for photoaging (Level A, Clinical Trial)
    8634809,   # 50% Glycolic acid for photoaging (Level A, RCT)
    29104718,  # Topical Vitamin C in dermatology (Level A, Review)
    20367669,  # SAP for acne (Level A, RCT)
    19165682,  # SAP + Retinol acne synergy (Level A, Clinical Trial)
    17147561,  # Niacinamide barrier function & acne (Level A, Review)
    28220628   # Niacinamide in acne treatment review (Level A, Review)
]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    cache_dir = os.path.join(project_root, "ops", "cache", "eutils")
    os.makedirs(cache_dir, exist_ok=True)
    
    print(f"Caching {len(PMIDS)} PMIDs to {cache_dir}...")
    
    for pmid in PMIDS:
        cache_file = os.path.join(cache_dir, f"{pmid}.json")
        if os.path.exists(cache_file):
            print(f"PMID {pmid} already cached. Skipping.")
            continue
            
        print(f"Fetching PMID {pmid}...")
        
        # 1. Fetch summary
        summary_url = f"{EUTILS}/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        title = ""
        pubtype = []
        exists = False
        
        try:
            req = urllib.request.Request(summary_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            
            rec = data.get("result", {}).get(str(pmid))
            if rec and not rec.get("error"):
                exists = True
                title = rec.get("title", "")
                pubtype = rec.get("pubtype", [])
        except Exception as e:
            print(f"Error fetching summary for {pmid}: {e}")
            time.sleep(1)
            continue
            
        if not exists:
            print(f"PMID {pmid} does not exist in PubMed.")
            time.sleep(0.5)
            continue
            
        # 2. Fetch abstract
        time.sleep(0.34)
        abstract_url = f"{EUTILS}/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=text"
        abstract = ""
        
        try:
            req = urllib.request.Request(abstract_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                abstract = r.read().decode('utf-8').strip()
        except Exception as e:
            print(f"Error fetching abstract for {pmid}: {e}")
            
        # Write cache
        cache_data = {
            "exists": True,
            "title": title,
            "pubtype": pubtype,
            "abstract": abstract
        }
        
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
        print(f"PMID {pmid} cached successfully.")
        time.sleep(0.34)

if __name__ == "__main__":
    main()
