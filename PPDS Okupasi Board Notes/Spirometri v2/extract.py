import sys, json, re, pathlib
sys.stdout.reconfigure(encoding="utf-8")
D = pathlib.Path(__file__).parent
SRC = {
 "16298470": "06_Chemical Hazard and RPP.pptx", "97b1d489": "Konsensus Spirometri PERDOKI 2019",
 "542462bd": "Video 9. Spirometri part 1", "7292d7aa": "Video 9. Spirometri part 2",
 "a9acdfc9": "ATS/ERS 2019 Standardization", "da835c15": "Catatan_Board (docx lama)",
 "6954846a": "PEMBACAAN HASIL SPIROMETRI ATO.docx", "644b9f22": "Spirometri untuk ujian board.pptx",
 "16def2ad": "Spirometri-board (2).pdf", "bb35fccc": "Presentasi Spirometri 2 - Marsen (Des 2024)",
 "2243fc3f": "ERS/ATS 2022 Interpretive strategies", "949ca41b": "Guideline_for... (PDF)",
 "9d39cb33": "GLI 2012 Multi-Ethnic Reference Values", "63e17587": "NIOSH Spirometry Training Guide 2004",
 "14749248": "Respiratory Protection Program.pptx", "1f4b1352": "Spirometri - Erika, Kresna.pptx",
 "b636e3ec": "Video Spirometri dr. Aziz Sp.Ok 18 Sep 2024", "fa5e0eb9": "Spirometry step by step.pdf",
 "17c4e590": "Spirometry in Occupational Health 2020 (Townsend/ACOEM)", "0854671d": "Ujian Spirometri - Tambahan Adit.pptx",
 "65c51788": "Y. Sim 2017 Spirometry & BD test",
}
for f in sorted(sys.argv[1:]):
    p = D / f"{f}.json"
    raw = p.read_text(encoding="utf-8-sig")
    j = json.loads(raw)
    ref = {}
    for r in j.get("references", []):
        ref.setdefault(r["citation_number"], SRC.get(r["source_id"][:8], r["source_id"][:8]))
    ans = j["answer"]
    # replace [1, 2] style citations with source short names
    def rep(m):
        nums = [int(x) for x in re.findall(r"\d+", m.group(0))]
        names = sorted({ref.get(n, f"#{n}") for n in nums})
        return " [" + "; ".join(names) + "]"
    ans2 = re.sub(r"\s?\[(\d+(?:\s*[,\-–]\s*\d+)*)\]", rep, ans)
    out = D / f"{f}.md"
    out.write_text(ans2, encoding="utf-8")
    print(f, len(ans2))
