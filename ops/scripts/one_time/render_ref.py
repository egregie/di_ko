"""Render sample pages of the 3 reference PDFs (visual-language reference) to PNG."""
import pypdfium2 as pdfium
import os

base = "C:/Users/candy/OneDrive/Рабочий стол"
out = "06_render/out/_ref"
os.makedirs(out, exist_ok=True)
refs = {
    "r2": "postakne model create 2.pdf",
    "r3": "postakne model create 3.pdf",
    "r4": "postakne model create 4.pdf",
}
for tag, fn in refs.items():
    p = os.path.join(base, fn)
    if not os.path.exists(p):
        print("MISSING:", p)
        continue
    pdf = pdfium.PdfDocument(p)
    n = len(pdf)
    print(f"{tag}: {n} pages -> {fn}")
    idxs = sorted(set([0, min(3, n - 1), min(6, n - 1), min(10, n - 1)]))
    for i in idxs:
        pil = pdf[i].render(scale=1.3).to_pil()
        pil.save(f"{out}/{tag}_p{i+1:03d}.png")
    pdf.close()
print("done")
