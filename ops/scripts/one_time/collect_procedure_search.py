"""Phase 8.7b C2 discovery: live PubMed search for PROCEDURE scarring candidates.
Reuses hardened fetch (evidence.py). Raw -> .tmp/. Discovery only; verification
(grounded judge) is a separate gated step. Procedures not yet represented as
candidates are prioritized (subcision, fractional RF, medium-depth peel).
"""
import json
import os
import sys
import urllib.parse
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "..", "lib"))
import evidence  # noqa: E402

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
TMP = os.path.join(PROJECT_ROOT, ".tmp")
os.makedirs(TMP, exist_ok=True)
TOOL = "tool=ym_proskin&email=admin@ym-proskin.local"

QUERIES = {
    "subcision": 'subcision AND "acne scars" AND (randomized OR comparative OR efficacy)',
    "subcision_rolling": 'subcision AND rolling AND "acne scars"',
    "fractional_rf": '"fractional radiofrequency" AND "atrophic acne scars" AND (randomized OR efficacy)',
    "medium_peel": '"medium-depth" AND peel AND "acne scars"',
    "ablative_co2": '"ablative fractional" AND "carbon dioxide" AND "atrophic acne scars"',
}
RETMAX = 6


def fetch_json(url):
    evidence.throttle_ncbi()
    req = urllib.request.Request(url, headers={"User-Agent": "ym_proskin_collector/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            evidence.log_api_call(url, "200")
            return json.load(r)
    except Exception as e:
        evidence.log_api_call(url, "ERROR")
        print(f"  ERROR {e}", file=sys.stderr)
        return None


def main():
    results, seen = {}, set()
    for key, term in QUERIES.items():
        q = urllib.parse.quote(term)
        url = (f"{evidence.EUTILS}/esearch.fcgi?db=pubmed&term={q}"
               f"&retmode=json&retmax={RETMAX}&sort=relevance&{TOOL}")
        data = fetch_json(url)
        pmids = data.get("esearchresult", {}).get("idlist", []) if data else []
        print(f"[{key}] {pmids}", file=sys.stderr)
        entries = []
        for pmid in pmids:
            if pmid in seen:
                continue
            seen.add(pmid)
            res = evidence.check_source(pmid, force_live=False)
            if res.get("exists") and res.get("abstract"):
                entries.append({"pmid": pmid, "title": res.get("title", ""),
                                "pubtype": res.get("pubtype", []), "abstract": res.get("abstract", "")})
        results[key] = {"term": term, "entries": entries}

    with open(os.path.join(TMP, "procedure_search.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open(os.path.join(TMP, "procedure_search.md"), "w", encoding="utf-8") as f:
        for key, block in results.items():
            f.write(f"\n# {key} — {block['term']}\n")
            for e in block["entries"]:
                f.write(f"\n## PMID {e['pmid']} | {' / '.join(e['pubtype'])}\n**{e['title']}**\n\n{e['abstract']}\n")
    total = sum(len(b["entries"]) for b in results.values())
    print(json.dumps({"queries": len(QUERIES), "unique_with_abstract": total}))


if __name__ == "__main__":
    main()
