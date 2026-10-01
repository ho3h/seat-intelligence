"""Showcase: 5 English policies on the real 34-guest luncheon chart via model -> program -> verified net.
   python3 -m genome.hero1.showcase [--gold]     (--gold skips the model and uses the gold programs; for testing)
Writes runs/hero1/showcase.json and runs/hero1/authoring.json.  Game rules only: nothing here claims anything about a guest."""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, sys, time
sys.path.insert(0, _REPO)
from genome.hero1.lang import parse, to_text, load_real, violations, posted_assignment, prep, ParseError, CATS
from genome.hero1.pipeline import run_net_assign
from genome.hero1.gen_train import prompt

SHOW = [
 ("show1", "Keep colleagues together, sections of at most four, and never put two government officials in the same section.",
  "size 4\ntogether company\nlimit government 1"),
 ("show2", "AI labs and big tech go in separate sections, chip makers get seated first, and no section bigger than five.",
  "apart ai_lab big_tech\norder chips\nsize 5"),
 ("show3", "Seat all the investors together, keep sections to three guests, and keep the AI labs away from the chip makers.",
  "together investor\nsize 3\napart ai_lab chips"),
 ("show4", "At most two government officials per section, software and security firms together, colleagues together, and investors first.",
  "limit government 2\ntogether software_security\ntogether company\norder investor"),
 ("show5", "Pairs only, please. Big tech before AI labs, and never two investors in one section.",
  "size 2\norder big_tech ai_lab\nlimit investor 1"),
]
MODEL = "mlx-community/Qwen3-1.7B-4bit"
ADAPTER = _REPO + "/adapters/hero1_1p7b"


def author_all(use_gold, reuse=False):
    out = {}
    if reuse: return json.load(open(_REPO + "/runs/hero1/authoring.json"))
    if use_gold:
        return {sid: dict(program=g, tokens_in=0, tokens_out=0, secs=0.0) for sid, _, g in SHOW}
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler
    model, tok = load(MODEL, adapter_path=ADAPTER)
    sampler = make_sampler(temp=0.0)
    def chat(text):
        m = [{"role": "user", "content": prompt(text)}]
        return tok.apply_chat_template(m, add_generation_prompt=True, enable_thinking=False)
    list(stream_generate(model, tok, chat("warm up"), max_tokens=8, sampler=sampler))    # compile / cache warm-up, not counted
    for sid, text, gold in SHOW:
        t0 = time.time(); last = None; txt = ""
        for resp in stream_generate(model, tok, chat(text), max_tokens=120, sampler=sampler):
            txt += resp.text; last = resp
        secs = time.time() - t0
        out[sid] = dict(program=txt.strip(), tokens_in=last.prompt_tokens, tokens_out=last.generation_tokens, secs=round(secs, 3),
                        prompt_tps=round(last.prompt_tps, 1), gen_tps=round(last.generation_tps, 1))
    return out


def layout(n):
    """walk around the table: left row 0..16 then right row 16..0; guest index = position in luncheon.json"""
    half = n // 2
    return list(range(half)) + [half + r for r in range(half - 1, -1, -1)]


def main(use_gold=False, reuse=False):
    guests, seats = load_real(); n = len(guests); walk = layout(n)
    auth = author_all(use_gold, reuse); res = []
    for sid, text, gold in SHOW:
        prog = auth[sid]["program"]; goldpol = parse(gold)
        rec = dict(id=sid, policy=text, gold_program=to_text(goldpol), emitted_program=prog, model_program_equals_gold=None)
        try: pol = parse(prog)
        except ParseError as e:
            rec["error"] = f"parse: {e}"; res.append(rec); continue
        rec["emitted_program_canonical"] = to_text(pol); rec["model_program_equals_gold"] = to_text(pol) == to_text(goldpol)
        a1, run1 = run_net_assign(guests, pol); a2, run2 = run_net_assign(guests, pol)
        rec["net_ok"] = a1 is not None; rec["net_interactions"] = run1.itrs
        rec["deterministic_rerun_identical"] = a1 == a2
        seq = prep(guests, pol)
        pos = {gi: p for p, (gi, _, _) in enumerate(seq)}
        secs = {}
        for gi, s in enumerate(a1): secs.setdefault(s, []).append(gi)
        rec["sections"] = [dict(section=s, size=len(ms), guests=[dict(position=pos[gi], new_seat=dict(side=seats[walk[pos[gi]]]["side"], row=seats[walk[pos[gi]]]["row"]), name=seats[gi]["name"],
                              org=seats[gi]["org"], category=seats[gi]["category"], posted_seat=dict(side=seats[gi]["side"], row=seats[gi]["row"])) for gi in sorted(ms, key=lambda g: pos[g])]) for s, ms in sorted(secs.items())]
        rec["assignment_by_guest"] = {seats[gi]["name"]: a1[gi] for gi in range(n)}
        rec["violations_of_emitted_rules"] = violations(guests, pol, a1)
        rec["violations_of_stated_rules"] = violations(guests, goldpol, a1)
        posted = posted_assignment(n, goldpol.cap)
        rec["posted_arrangement_sections"] = "posted chart walked around the table (left row 0..16, then right row 16..0), cut into consecutive blocks of %d seats" % goldpol.cap
        rec["posted_arrangement_violations"] = violations(guests, goldpol, posted)
        rec["posted_arrangement_violation_count"] = rec["posted_arrangement_violations"]["total"]
        if not rec["model_program_equals_gold"]:
            ag, _ = run_net_assign(guests, goldpol)
            rec["note"] = "the model misread this policy; the arrangement below is what the emitted program produced. For reference the arrangement of the gold program:"
            rec["assignment_by_guest_if_gold_program"] = {seats[gi]["name"]: ag[gi] for gi in range(n)}
            rec["violations_of_stated_rules_if_gold_program"] = violations(guests, goldpol, ag)
        rec["authoring"] = auth[sid]
        res.append(rec)
    out = dict(note="Game rules chosen by the host for a demonstration; they make no claim about any guest. Guests are described only by printed company and coarse category (data/hero/luncheon.json).",
               model=None if use_gold else dict(base=MODEL, adapter="adapters/hero1_1p7b", decoding="greedy"), showcase=res)
    p = _REPO + "/runs/hero1/showcase" + ("_gold" if use_gold else "") + ".json"
    out["seat_layout"] = "new_seat = the position-th seat of a walk around the table: left row 0..16, then right row 16..0; a section is a contiguous run of that walk"
    json.dump(out, open(p, "w"), indent=1)
    for r in res:
        print(r["id"], "| prog==gold:", r.get("model_program_equals_gold"), "| viol emitted/stated:", r.get("violations_of_emitted_rules", {}).get("total"),
              r.get("violations_of_stated_rules", {}).get("total"), "| posted:", r.get("posted_arrangement_violation_count"), "| sections", len(r.get("sections", [])), "| toks", r.get("authoring", {}).get("tokens_out"))
    if not use_gold and not reuse: json.dump(auth, open(_REPO + "/runs/hero1/authoring.json", "w"), indent=1)


if __name__ == "__main__": main("--gold" in sys.argv, "--reuse" in sys.argv)
