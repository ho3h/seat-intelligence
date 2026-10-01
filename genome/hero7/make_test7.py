"""Freeze data/hero/policies_test7.json: the request texts written by a fresh subagent (policies_test7_raw.json, which saw only
the guest list and the plain meaning of the seven words) plus the gold program for each, written by me (HERO-7 author) before
any HERO-7 model existed. Refuses to overwrite."""
import json, os, sys
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)
from genome.hero6 import lang6 as L
GOLD = {
 "t001": "avoid Hock_Tan Lisa_Su", "t002": "size 3", "t003": "size 4\npair Alex_Karp Shyam_Sankar", "t004": "size 4\norder government",
 "t005": "size 5\npair Brad_Gerstner Scott_Kupor", "t006": "together ai_lab\napart ai_lab chips", "t007": "avoid Nvidia Sanjay_Mehrotra",
 "t008": "limit government 1", "t009": "size 3\npair Brandon_Rahbar_Daniels Sean_Cairncross", "t010": "size 5\napart big_tech investor",
 "t011": "size 5\npair Greg_Brockman Odalys_Ferreira-Quint", "t012": "order government unlabelled investor",
 "t013": "size 4\navoid Elon_Musk Greg_Brockman\navoid Dario_Amodei Greg_Brockman", "t014": "limit chips 2",
 "t015": "apart ai_lab chips\npair Secretary_Scott_Bessent Speaker_Johnson", "t016": "together company",
 "t017": "avoid Michael_Kratsios Richard_Walters", "t018": "size 2\napart software_security government", "t019": "avoid Anthropic Palantir",
 "t020": "apart ai_lab big_tech", "t021": "order government big_tech\navoid AMD Broadcom", "t022": "size 4\ntogether investor\norder investor big_tech",
 "t023": "avoid Brad_Gerstner Teodor_Vasquez-Lind", "t024": "apart ai_lab chips", "t025": "pair Speaker_Johnson VPOTUS",
 "t026": "together company\nlimit government 2", "t027": "limit government 2\npair Satya_Nadella Sundar_Pichai", "t028": "limit investor 1",
 "t029": "pair Elon_Musk Jared_Isaacman", "t030": "order investor", "t031": "size 4\navoid Elon_Musk Mark_Zuckerberg",
 "t032": "size 3\napart ai_lab government", "t033": "apart investor government\npair Chamath_Palihapitiya David_Sacks",
 "t034": "size 5\ntogether chips", "t035": "pair Priyanka_Oduya Sanjay_Mehrotra", "t036": "order unlabelled government",
 "t037": "size 5\navoid Chairman_Andrew_Ferguson Meta\npair Susie_Wiles Will_Scharf", "t038": "limit ai_lab 1\nlimit chips 1",
 "t039": "pair Jensen_Huang Lisa_Su", "t040": "limit big_tech investor 2", "t041": "pair Bill_McDermott Nikesh_Arora",
 "t042": "size 5\ntogether software_security", "t043": "together investor\navoid Jeff_Bezos Secretary_Lutnick",
 "t044": "apart investor government\norder chips", "t045": "size 3\navoid Alex_Karp Brandon_Rahbar_Daniels", "t046": "size 2",
 "t047": "limit chips 2\navoid Ingrid_Achterberg Jensen_Huang\navoid Ingrid_Achterberg Lisa_Su", "t048": "apart big_tech chips",
 "t049": "avoid Anthropic OpenAI", "t050": "size 4\nlimit government 1\nlimit ai_lab 1", "t051": "order government\npair Director_Clayton POTUS",
 "t052": "together unlabelled", "t053": "avoid Greg_Brockman Tom_Brown", "t054": "size 6\norder government big_tech ai_lab\napart ai_lab investor",
 "t055": "limit investor 2\navoid Brad_Gerstner Chamath_Palihapitiya", "t056": "size 4\ntogether company", "t057": "pair Michael_Kratsios Sundar_Pichai",
 "t058": "size 4\napart chips investor", "t059": "pair Alex_Karp Bashir_Lindqvist\navoid Malcolm_Ebrahimi-Stone Michael_Kratsios",
 "t060": "limit government unlabelled 2", "t061": "size 4\norder big_tech chips\npair Dario_Amodei Jensen_Huang", "t062": "together big_tech",
 "t063": "together investor\navoid Satya_Nadella Sundar_Pichai\navoid Hock_Tan Lisa_Su", "t064": "limit investor 1\nlimit big_tech 1",
 "t065": "avoid Chairman_Andrew_Ferguson Sundar_Pichai", "t066": "size 5\norder ai_lab chips big_tech",
 "t067": "pair Alex_Karp Shyam_Sankar\navoid Alex_Karp Exiger\navoid Exiger Shyam_Sankar", "t068": "together ai_lab",
 "t069": "avoid Elon_Musk VPOTUS", "t070": "size 3\napart government unlabelled",
 "t071": "avoid Celestine_Mbatha-Ruiz David_Sacks\navoid Celestine_Mbatha-Ruiz Chamath_Palihapitiya", "t072": "apart ai_lab software_security",
 "t073": "limit big_tech 1\npair Secretary_Lutnick Secretary_Scott_Bessent", "t074": "size 6\ntogether chips\norder chips investor",
 "t075": "pair Hock_Tan Sanjay_Mehrotra", "t076": "limit ai_lab chips 2", "t077": "avoid Craft_Ventures Scott_Kupor",
 "t078": "size 3\napart government big_tech", "t079": "size 5\navoid Sean_Cairncross Susie_Wiles", "t080": "size 5\napart investor government",
 "t081": "pair Shyam_Sankar Will_Scharf", "t082": "order investor software_security government", "t083": "size 4\npair Nikesh_Arora Rafferty_Okonkwo",
 "t084": "size 3\nlimit government 1\napart ai_lab big_tech", "t085": "size 3\navoid Google Meta\npair Microsoft Nvidia",
 "t086": "together company\napart chips software_security", "t087": "order government investor\npair Jared_Isaacman Michael_Kratsios",
 "t088": "together big_tech\nlimit ai_lab 2", "t089": "avoid Brandon_Rahbar_Daniels Nikesh_Arora", "t090": "size 4\norder government",
 "t091": "limit chips 2\npair Lisa_Su Satya_Nadella", "t092": "together software_security", "t093": "together software_security\npair Jensen_Huang Richard_Walters",
 "t094": "limit investor 2\nlimit chips 2", "t095": "avoid Emeric_Tsvetkov OpenAI\npair Sundar_Pichai Yusra_Delacroix-Hahn",
 "t096": "apart ai_lab unlabelled", "t097": "avoid Mark_Zuckerberg POTUS", "t098": "size 2\norder government ai_lab chips",
 "t099": "size 4\nlimit government 1\navoid Bill_McDermott Jeff_Bezos", "t100": "limit government investor 3",
}
NOTES = {"t067": "ambiguous: 'Palantir duo' read as the two Palantir guests on the original chart (Karp, Sankar), 'them' = those two; "
                 "the test-7 guest list also has a third Palantir guest (Bashir Lindqvist)",
         "t054": "'six per section' = the default size; the canonical program has no size line",
         "t074": "'sections of six' = the default size", "t092": "'Cap 6' = the default size"}
OUT = _REPO + "/data/hero/policies_test7.json"
if os.path.exists(OUT): sys.exit("refusing to overwrite " + OUT)
raw = json.load(open(_REPO + "/data/hero/policies_test7_raw.json"))
pols = []
for p in raw["policies"]:
    g = GOLD[p["id"]]; L.parse(g)
    pols.append(dict(id=p["id"], voice=p["voice"], text=p["text"], gold=g, invented=p["invented"], names_guests=p["names_guests"],
                     author_meaning=p["meaning"], **({"gold_note": NOTES[p["id"]]} if p["id"] in NOTES else {})))
assert len(pols) == 100 and set(GOLD) == {p["id"] for p in pols}
json.dump(dict(note="HERO-7 fresh final test set. Request texts and extra_guests: a separate subagent that saw only the guest list "
               "(names, companies, categories) and the plain meaning of the seven words (no repo access). Gold programs: written by the "
               "HERO-7 author from the texts before any HERO-7 training. Frozen; see docs/HERO-7.md section 1.",
               author_note=raw["author_note"], extra_guests=raw["extra_guests"], policies=pols), open(OUT, "w"), indent=1)
print("wrote", OUT, len(pols))
