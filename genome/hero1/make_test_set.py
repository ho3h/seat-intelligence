"""Writes data/hero/policies_test.json: 72 hand-written seating policies in 6 voices, written BEFORE any model was trained or
evaluated and not edited afterwards (sha256 in docs/HERO-1.md). Gold = canonical stage program. Run once."""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, hashlib, sys, os
sys.path.insert(0, _REPO)
from genome.hero1.lang import parse, to_text

H = {"H1": {"tc", "apt", "ord"}, "H2": {"size", "tk", "lim"}, "H3": {"lim", "apt", "ord"},
     "H4": {"size", "tc", "tk", "ord"}, "H5": {"tk", "apt"}, "H6": {"size", "lim", "apt", "ord"}}

P = {}
P["terse"] = [
 ("Colleagues together. Max 4 per section.", "size 4\ntogether company"),
 ("No two government officials in one section.", "limit government 1"),
 ("AI labs and big tech apart. Sections of 5.", "size 5\napart ai_lab big_tech"),
 ("Investors first, then AI labs. Same company together.", "order investor ai_lab\ntogether company"),
 ("Pairs only. Chips and software apart.", "size 2\napart chips software_security"),
 ("Max two investors per section; four per section overall.", "limit investor 2\nsize 4"),
 ("Keep all AI labs together.", "together ai_lab"),
 ("Cap 3. Government officials first.", "size 3\norder government"),
 ("No two of big tech or chips per section; colleagues together.", "limit big_tech chips 1\ntogether company"),
 ("Chips first, then big tech, then AI labs.", "order chips big_tech ai_lab"),
 ("Company groups stay whole. Investors and government apart. Government seated first.", "together company\napart investor government\norder government"),
 ("Sections of 3. Chip makers together. Max 1 investor per section.", "size 3\ntogether chips\nlimit investor 1"),
]
P["formal"] = [
 ("Guests employed by the same company shall be seated in the same section wherever the section size permits.", "together company"),
 ("No section shall contain more than four guests, and no section shall contain more than one guest from the software and security category.", "size 4\nlimit software_security 1"),
 ("Representatives of AI laboratories and of the investment community are to be seated in separate sections.", "apart ai_lab investor"),
 ("Government officials are to be seated first, followed by representatives of big technology companies.", "order government big_tech"),
 ("It is requested that at most two government officials be assigned to any one section, and that colleagues be kept together.", "limit government 2\ntogether company"),
 ("Sections shall be limited to five guests. Chip manufacturers shall not share a section with AI laboratory representatives.", "size 5\napart chips ai_lab"),
 ("The host directs that all investors be seated together, that no section exceed three guests, and that AI laboratory guests be seated first.", "together investor\nsize 3\norder ai_lab"),
 ("No section shall include more than one guest drawn from either the AI laboratories or the big technology companies.", "limit ai_lab big_tech 1"),
 ("Guests of a common employer shall be placed together; big technology and chip manufacturers shall be kept in separate sections.", "together company\napart big_tech chips"),
 ("Seat the government officials first, then the investors, then the remaining guests, with no more than four persons per section.", "order government investor\nsize 4"),
 ("No section shall hold more than one investor; AI laboratories and government officials are to be kept apart; and chip manufacturers are to be seated first.", "limit investor 1\napart ai_lab government\norder chips"),
 ("Sections of at most four; guests of one company are to sit together; all government officials are to be grouped; AI laboratories are seated first.", "size 4\ntogether company\ntogether government\norder ai_lab"),
]
P["chatty"] = [
 ("Okay so basically I just want people from the same company sitting together, that's it.", "together company"),
 ("Can we make sure there are never more than 3 folks in a section? And let's keep the AI lab people and the big tech people in different sections, just to mix the room up.", "size 3\napart ai_lab big_tech"),
 ("I'd love it if the chip folks got the first sections, then the AI labs.", "order chips ai_lab"),
 ("Let's not put two investors in the same section, mixing it up is more fun.", "limit investor 1"),
 ("Honestly just keep the government people together and make sections of four.", "together government\nsize 4"),
 ("So, colleagues sit together, and I don't want more than two government officials in any one section, okay?", "together company\nlimit government 2"),
 ("Small sections please, like two people each, and chip makers away from investors.", "size 2\napart chips investor"),
 ("Start with the investors, then the big tech crowd, and try to keep each company together.", "order investor big_tech\ntogether company"),
 ("Put the software and security companies together in one bunch, and max five to a section.", "together software_security\nsize 5"),
 ("I want at most one person from AI labs or chips per section, and the AI labs go first.", "limit ai_lab chips 1\norder ai_lab"),
 ("Same-company folks go together, please keep investors and big tech in separate sections, and seat the investors first!", "together company\napart investor big_tech\norder investor"),
 ("Sections of three, the AI lab people all sit together, and no more than one government person per section.", "size 3\ntogether ai_lab\nlimit government 1"),
]
P["negative"] = [
 ("Don't let any section have more than four guests.", "size 4"),
 ("Never seat two government officials in the same section, and never split up a company.", "limit government 1\ntogether company"),
 ("Do not put AI labs anywhere near big tech, and don't let sections exceed five.", "size 5\napart ai_lab big_tech"),
 ("Nobody from a chip maker sits in a section with an investor. Nobody gets seated ahead of the AI labs.", "apart chips investor\norder ai_lab"),
 ("No section may hold more than two investors, and no section may hold more than six people, obviously.", "limit investor 2"),
 ("Don't scatter the government officials across the room; keep them together.", "together government"),
 ("Nothing fancy: no more than one guest from big tech or AI labs in a section, and never more than three guests total.", "limit ai_lab big_tech 1\nsize 3"),
 ("Don't seat anyone before the investors and the chip makers, in that order, and don't let any company be split up.", "order investor chips\ntogether company"),
 ("No AI lab guest should share a section with a software or security guest, and no investor should share one with a software or security guest either.", "apart ai_lab software_security\napart investor software_security"),
 ("Never more than two chip makers in a section; never mix government officials with investors.", "limit chips 2\napart government investor"),
 ("Don't split up the AI labs, and don't ever put big tech in the same section as government officials.", "together ai_lab\napart big_tech government"),
 ("No section bigger than four, no more than one investor in any section, no AI lab in a section with a chip maker, and don't seat anyone ahead of government officials.", "size 4\nlimit investor 1\napart ai_lab chips\norder government"),
]
P["list"] = [
 ("Rules:\n- same company together\n- max 3 per section", "together company\nsize 3"),
 ("1. no more than 2 government per section\n2. investors first", "limit government 2\norder investor"),
 ("* AI labs together\n* big tech apart from investors\n* sections of 4", "together ai_lab\napart big_tech investor\nsize 4"),
 ("Seating rules; (a) sections of 4 (b) chips and software apart (c) colleagues together", "size 4\napart chips software_security\ntogether company"),
 ("- keep investors together\n- at most 5 per section", "together investor\nsize 5"),
 ("Constraints: one investor per section max; one AI lab per section max.", "limit investor 1\nlimit ai_lab 1"),
 ("1) government first\n2) then big tech\n3) then AI labs", "order government big_tech ai_lab"),
 ("- apart: AI labs / chips\n- apart: government / software & security\n- cap: 3", "apart ai_lab chips\napart government software_security\nsize 3"),
 ("Do: colleagues together; chip makers together. Limit: two per section.", "together company\ntogether chips\nsize 2"),
 ("Rules: max 2 big tech or AI labs per section (combined); AI labs seated first", "limit ai_lab big_tech 2\norder ai_lab"),
 ("- max 1 government per section\n- AI labs and investors apart\n- big tech first", "limit government 1\napart ai_lab investor\norder big_tech"),
 ("• sections ≤ 5\n• colleagues together\n• government together\n• investors first", "size 5\ntogether company\ntogether government\norder investor"),
]
P["wedding"] = [
 ("Guests who work at the same company are like family, so let's keep them in the same section, and let's keep every section to a cosy four.", "together company\nsize 4"),
 ("We shall have our AI lab guests toasted first, taking the first sections, followed by the chip makers.", "order ai_lab chips"),
 ("Let's not seat two government officials in the same section, it would be too much of the same flavour.", "limit government 1"),
 ("Big tech and investors should each have their own sections, never mixed, with a lovely intimate three per section.", "apart big_tech investor\nsize 3"),
 ("All our software and security friends in one section together, please, wherever it fits.", "together software_security"),
 ("Table-plan rule of the day: sprinkle the government officials thinly, two per section at most, and keep colleagues side by side.", "limit government 2\ntogether company"),
 ("We want the investors seated first as our guests of honour, then the AI labs, and keep the chip makers and the big tech guests in separate sections.", "order investor ai_lab\napart chips big_tech"),
 ("Small and sweet: two to a section, and colleagues stay together.", "size 2\ntogether company"),
 ("One AI lab or big tech guest per section, sweetheart, and the government officials go first.", "limit ai_lab big_tech 1\norder government"),
 ("Keep every chip maker together, no more than five to a section, and never put chips with AI labs.", "together chips\nsize 5\napart chips ai_lab"),
 ("Seat all the investors together as a group and keep them apart from the government officials.", "together investor\napart investor government"),
 ("Lovely sections of four, please: one investor at most per section, AI labs and big tech in different sections, and the government officials must come first.", "size 4\nlimit investor 1\napart ai_lab big_tech\norder government"),
]
HELD = {("terse", 10): "H1", ("terse", 11): "H2", ("formal", 10): "H3", ("formal", 11): "H4", ("chatty", 10): "H1", ("chatty", 11): "H2",
        ("negative", 10): "H5", ("negative", 11): "H6", ("list", 10): "H3", ("list", 11): "H4", ("wedding", 10): "H5", ("wedding", 11): "H6"}

rows = []
for v, items in P.items():
    assert len(items) == 12, v
    for i, (text, gold) in enumerate(items):
        pol = parse(gold)
        sig = sorted(pol.sig())
        h = HELD.get((v, i))
        if h: assert set(sig) == H[h], (v, i, sig, h)
        else: assert set(sig) not in H.values(), (v, i, sig)
        rows.append(dict(id=f"{v[:3]}{i+1:02d}", voice=v, text=text, gold=to_text(pol), sig=sig, heldout_combo=h))
out = dict(note="HERO-1 independent test policies, hand-written before any training/evaluation; frozen. gold = canonical stage program.",
           heldout_signatures={k: sorted(v) for k, v in H.items()}, policies=rows)
path = _REPO + "/data/hero/policies_test.json"
assert not os.path.exists(path), "already frozen"
s = json.dumps(out, indent=1, ensure_ascii=False)
open(path, "w").write(s + "\n")
print(len(rows), hashlib.sha256(open(path, "rb").read()).hexdigest())
