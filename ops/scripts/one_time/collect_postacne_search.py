"""Phase 8.7a discovery: live PubMed search for postacne fact candidates.

Reuses the hardened fetch layer from ops/scripts/lib/evidence.py (IPv4 force,
<=3 req/s throttle, tool/email params, api call logging). Raw results go to
.tmp/ (intermediates, never committed). Selection of facts from abstracts is
a human/orchestrator decision - this script only gathers evidence honestly.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "..", "lib"))
import evidence  # noqa: E402  (side effects: IPv4 force, throttle, logging)

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
TMP_DIR = os.path.join(PROJECT_ROOT, ".tmp")
os.makedirs(TMP_DIR, exist_ok=True)

TOOL_PARAMS = "tool=ym_proskin&email=admin@ym-proskin.local"

# Clinically focused queries per TZ Phase 8.7a Block A2
QUERIES = {
    "pih_azelaic": '"azelaic acid" AND (hyperpigmentation OR "postinflammatory") AND acne',
    "pih_retinoid": '(tretinoin OR retinoid) AND "postinflammatory hyperpigmentation"',
    "pih_peels": '(glycolic OR salicylic) AND peel AND ("postinflammatory hyperpigmentation" OR "acne scars")',
    "pih_niacinamide": 'niacinamide AND (hyperpigmentation OR pigmentation) AND clinical',
    "scars_microneedling": 'microneedling AND "acne scars" AND (randomized OR "systematic review")',
    "scars_tca_cross": '"trichloroacetic acid" AND CROSS AND "acne scars"',
    "scars_fractional": 'fractional AND laser AND "atrophic acne scars" AND (randomized OR comparative)',
    "scars_adapalene": 'adapalene AND "acne scars"',
    "pie_erythema": '"postinflammatory erythema" AND (acne OR treatment)',
    "azelaic_acne_rct": '"azelaic acid" AND acne AND (randomized OR "double-blind")',
}
RETMAX = 8


def fetch_json(url):
    evidence.throttle_ncbi()
    req = urllib.request.Request(url, headers={"User-Agent": "ym_proskin_collector/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            evidence.log_api_call(url, "200")
            return json.load(r)
    except Exception as e:
        evidence.log_api_call(url, "ERROR")
        print(f"  ERROR {e} for {url[:120]}", file=sys.stderr)
        return None


def main():
    results = {}
    seen_pmids = set()
    for key, term in QUERIES.items():
        q = urllib.parse.quote(term)
        url = (f"{evidence.EUTILS}/esearch.fcgi?db=pubmed&term={q}"
               f"&retmode=json&retmax={RETMAX}&sort=relevance&{TOOL_PARAMS}")
        data = fetch_json(url)
        if not data:
            results[key] = {"error": "esearch failed", "pmids": []}
            continue
        pmids = data.get("esearchresult", {}).get("idlist", [])
        print(f"[{key}] {len(pmids)} pmids: {pmids}", file=sys.stderr)
        entries = []
        for pmid in pmids:
            if pmid in seen_pmids:
                continue
            seen_pmids.add(pmid)
            # check_source = the same live path the verify gate uses
            # (esummary title/pubtype + efetch abstract, cached under ops/cache/eutils)
            res = evidence.check_source(pmid, force_live=False)
            if res.get("exists") and res.get("abstract"):
                entries.append({
                    "pmid": pmid,
                    "title": res.get("title", ""),
                    "pubtype": res.get("pubtype", []),
                    "abstract": res.get("abstract", ""),
                })
        results[key] = {"term": term, "entries": entries}

    out_json = os.path.join(TMP_DIR, "postacne_search.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Human-readable digest for fact selection
    out_md = os.path.join(TMP_DIR, "postacne_search.md")
    with open(out_md, "w", encoding="utf-8") as f:
        for key, block in results.items():
            f.write(f"\n# {key} — {block.get('term','')}\n")
            for e in block.get("entries", []):
                f.write(f"\n## PMID {e['pmid']} | {' / '.join(e['pubtype'])}\n")
                f.write(f"**{e['title']}**\n\n{e['abstract']}\n")
    total = sum(len(b.get("entries", [])) for b in results.values())
    print(json.dumps({"queries": len(QUERIES), "unique_with_abstract": total,
                      "json": out_json, "md": out_md}))


if __name__ == "__main__":
    main()
