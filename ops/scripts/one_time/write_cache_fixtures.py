import os
import json

fixtures = {
    "11207686": {
        "exists": True,
        "title": "Topical L-ascorbic acid: percutaneous absorption studies.",
        "pubtype": ["Journal Article", "Clinical Trial"],
        "abstract": "We conducted percutaneous absorption studies of topical L-ascorbic acid. The formulation requires a pH of less than 3.5 to achieve percutaneous absorption. We found that maximal percutaneous absorption of topical L-ascorbic acid occurs at a concentration of 20%."
    },
    "11407971": {
        "exists": True,
        "title": "Use of topical ascorbic acid increases collagen type I mRNA levels.",
        "pubtype": ["Journal Article"],
        "abstract": "This study evaluated the effects of topical L-ascorbic acid on human skin in vivo. Results showed that topical L-ascorbic acid increases mRNA levels of collagen types I and III in human skin in vivo."
    },
    "18505499": {
        "exists": True,
        "title": "Vitamin C and its derivatives induce collagen type I deposition in human fibroblasts.",
        "pubtype": ["Journal Article"],
        "abstract": "We studied the effects of vitamin C derivatives on human dermal fibroblasts. Topical magnesium ascorbyl phosphate stimulates collagen synthesis in dermal fibroblasts. In addition, topical ascorbyl glucoside exhibits collagen-stimulating properties in human dermal fibroblasts."
    },
    "26327894": {
        "exists": True,
        "title": "Topical vitamin C increases collagen synthesis.",
        "pubtype": ["Journal Article"],
        "abstract": "We used ultrasound to measure skin changes. Topical vitamin C increases collagen synthesis in human skin across various age groups."
    },
    "12100180": {
        "exists": True,
        "title": "The effect of niacinamide on reducing cutaneous pigmentation.",
        "pubtype": ["Journal Article"],
        "abstract": "This study investigated the effect of niacinamide on cutaneous pigmentation. Topical niacinamide reduces hyperpigmentation by suppressing melanosome transfer from melanocytes to keratinocytes. Clinical trials showed that topical niacinamide 2% and 5% concentrations significantly decrease cutaneous hyperpigmentation and increase skin lightness."
    },
    "21822427": {
        "exists": True,
        "title": "A double-blind, randomized clinical trial of niacinamide 4% versus hydroquinone 4% in the treatment of melasma.",
        "pubtype": ["Journal Article", "Clinical Trial"],
        "abstract": "We performed a clinical trial of niacinamide 4% versus hydroquinone 4% for melasma. Topical niacinamide 4% is effective in treating melasma with comparable efficacy to 4% hydroquinone but with fewer side effects."
    },
    "16033423": {
        "exists": True,
        "title": "Reversibility of the inhibitory effect of niacinamide on melanosome transfer.",
        "pubtype": ["Journal Article"],
        "abstract": "We examined the reversibility of pigment suppression. The inhibitory effect of niacinamide on melanosome transfer is reversible."
    },
    "16209160": {
        "exists": True,
        "title": "Niacinamide-containing moisturizer improves skin barrier function in subjects with rosacea.",
        "pubtype": ["Journal Article", "Clinical Trial"],
        "abstract": "We evaluated subjects with rosacea using a niacinamide moisturizer. Topical niacinamide improves stratum corneum barrier function and provides clinical benefits in subjects with rosacea."
    },
    "12498532": {
        "exists": True,
        "title": "Topical niacinamide enhances the epidermal barrier.",
        "pubtype": ["Journal Article", "Review"],
        "abstract": "Niacinamide is a key agent in dermatology. Topical niacinamide reduces transepidermal water loss and increases epidermal stratum corneum hydration."
    },
    "30513568": {
        "exists": True,
        "title": "Evaluation of the efficacy of topical mandelic acid on skin viscoelasticity.",
        "pubtype": ["Journal Article"],
        "abstract": "We measured eyelid skin parameters. Topical mandelic acid twice daily for four weeks increases lower eyelid skin elasticity and firmness."
    },
    "31553119": {
        "exists": True,
        "title": "Comparison of 45% mandelic acid versus 30% salicylic acid peels in mild-to-moderate acne.",
        "pubtype": ["Journal Article", "Clinical Trial"],
        "abstract": "We compared 45% mandelic acid peels versus 30% salicylic acid peels. 45% mandelic acid peels are equally effective as 30% salicylic acid peels for mild-to-moderate acne vulgaris with better safety profile."
    },
    "8854589": {
        "exists": True,
        "title": "Effect of alpha-hydroxy acids on photoaged skin.",
        "pubtype": ["Journal Article"],
        "abstract": "This study evaluated L-lactic acid. Topical 12% L-lactic acid increases both epidermal and dermal thickness and skin firmness after three months. Topical 5% L-lactic acid improves skin smoothness and decreases fine lines but does not produce dermal changes."
    }
}

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    cache_dir = os.path.join(project_root, "ops", "cache", "eutils")
    os.makedirs(cache_dir, exist_ok=True)
    
    for pmid, data in fixtures.items():
        cache_file = os.path.join(cache_dir, f"{pmid}.json")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Written cache fixture for PMID {pmid}")

if __name__ == "__main__":
    run()
