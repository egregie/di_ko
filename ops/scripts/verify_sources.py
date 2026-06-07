import os
import json
import time
import urllib.request
import urllib.parse

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def pmid_summary(pmid):
    url = f"{EUTILS}/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
        rec = data.get("result", {}).get(str(pmid))
        if rec and not rec.get("error"):
            return {
                "exists": True,
                "title": rec.get("title", ""),
                "pubtype": rec.get("pubtype", [])
            }
        else:
            return {"exists": False, "title": "", "pubtype": []}
    except Exception as e:
        return {"exists": False, "title": "", "pubtype": [], "error": str(e)}

def pmid_abstract(pmid):
    url = f"{EUTILS}/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=text"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            text = r.read().decode('utf-8')
        return text.strip()
    except Exception as e:
        return ""

def doi_check(doi):
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'mailto:admin@ym-proskin.local'}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
        title_list = data.get("message", {}).get("title", [])
        title = title_list[0] if title_list else ""
        pubtype = [data.get("message", {}).get("type", "")]
        return {
            "exists": True,
            "title": title,
            "pubtype": pubtype
        }
    except Exception as e:
        return {"exists": False, "title": "", "pubtype": [], "error": str(e)}

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    sources_path = os.path.join(project_root, "03_knowledge_graph", "sources.json")
    logs_dir = os.path.join(project_root, "ops", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    with open(sources_path, "r", encoding="utf-8") as f:
        sources_data = json.load(f)
    
    results = []
    for src in sources_data.get("sources", []):
        sid = src.get("source_id")
        pmid = src.get("pmid")
        doi = src.get("doi")
        
        # Skip if no pmid and no doi
        if not pmid and not doi:
            results.append({
                "source_id": sid,
                "pmid": "",
                "doi": "",
                "exists": False,
                "title": "",
                "pubtype": [],
                "abstract": ""
            })
            continue
            
        exists = False
        title = ""
        pubtype = []
        abstract = ""
        
        if pmid:
            print(f"Checking PMID {pmid} for source {sid}...")
            sum_res = pmid_summary(pmid)
            if sum_res.get("exists"):
                exists = True
                title = sum_res.get("title")
                pubtype = sum_res.get("pubtype")
                # Fetch abstract too
                abstract = pmid_abstract(pmid)
            else:
                print(f"PMID {pmid} does not exist in PubMed.")
            time.sleep(0.34) # throttle limit
        elif doi:
            print(f"Checking DOI {doi} for source {sid}...")
            doi_res = doi_check(doi)
            if doi_res.get("exists"):
                exists = True
                title = doi_res.get("title")
                pubtype = doi_res.get("pubtype")
            else:
                print(f"DOI {doi} does not exist in Crossref.")
            time.sleep(0.34)
            
        results.append({
            "source_id": sid,
            "pmid": pmid or "",
            "doi": doi or "",
            "exists": exists,
            "title": title,
            "pubtype": pubtype,
            "abstract": abstract
        })
        
    out_path = os.path.join(logs_dir, "source_check_phase1.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Source check complete. Output written to {out_path}")

if __name__ == "__main__":
    main()
