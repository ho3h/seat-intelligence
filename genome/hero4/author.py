"""Authoring harness + log for the ten NEW words.  python -m genome.hero4.author start|edit|verify|end <word> [note]
Every call appends one JSON line to runs/hero4/authoring_log.jsonl (wall clock included).  `verify` builds the net for each
test instance of the word and runs the hidden suite (genome.verify v2: edge + random + big + exhaustive small) at seeds 0,1,2."""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, sys, time, inspect
LOG = _REPO + "/runs/hero4/authoring_log.jsonl"

# test instances per word (parameters chosen to include edge parameters: k>=S identity, k=0/1, S=1/2, unused categories...)
INSTANCES = {
    "limit": [("government", 2, 6), ("investor", 1, 4), ("chips", 3, 5), ("ai_lab", 5, 5), ("big_tech", 2, 3)],
    "pair": [("ai_lab", "chips"), ("government", "investor"), ("big_tech", "software_security"), ("investor", "ai_lab")],
    "apart": [("Meta", "Amazon"), ("Palantir", "OpenAI"), ("AMD", "Altimeter"), ("Nvidia", "NASA")],
    "vip": [(4,), (0,), (12,), (31,)],
    "stagger": [(1,), (2,), (3,), (7,)],
    "headseat": [()],
    "bigfirst": [()],
    "waitlist": [("chips", 3), ("government", 1), ("ai_lab", 0), ("investor", 4)],
    "snake": [(6,), (3,), (1,), (2,), (10,)],
    "sectionlead": [(5,), (3,), (2,), (1,), (8,)],
}


def log(rec):
    rec["t"] = time.time(); rec["iso"] = time.strftime("%H:%M:%S")
    with open(LOG, "a") as f: f.write(json.dumps(rec, default=str) + "\n")


def do_verify(word, seeds=(0, 1, 2)):
    import importlib
    from genome.hero4 import newwords, wordtests
    importlib.reload(newwords)
    res = []; t0 = time.time(); ok = True
    for a in INSTANCES[word]:
        try:
            net = newwords.BUILD_NEW[word](list(a))
        except Exception as e:
            res.append({"args": a, "status": "build_error", "why": repr(e)[:300]}); ok = False; break
        for r in wordtests.run(word, list(a), net, seeds=seeds, workers=4, tag="new"):
            res.append({"args": a, **{k: r[k] for k in ("seed", "status", "cases", "failed", "cx", "reason")}})
            if r["status"] != "pass": ok = False; break
        if not ok: break
    return ok, res, time.time() - t0


if __name__ == "__main__":
    cmd, word = sys.argv[1], sys.argv[2]; note = " ".join(sys.argv[3:])
    if cmd in ("start", "edit", "end"):
        rec = {"event": cmd, "word": word, "note": note}
        if cmd == "end":
            from genome.hero4 import newwords
            fs = newwords.SRC[word]; fs = fs if isinstance(fs, (tuple, list)) else [fs]; src = ''.join(inspect.getsource(f) for f in fs)
            rec.update(lines=len(src.splitlines()), chars=len(src))
        log(rec); print("logged", cmd, word)
    elif cmd == "verify":
        ok, res, secs = do_verify(word)
        bad = [r for r in res if r.get("status") != "pass"]
        log({"event": "verify", "word": word, "pass": ok, "secs": round(secs, 1), "n_pass": len(res) - len(bad), "first_fail": bad[:1]})
        print("PASS" if ok else "FAIL", f"{len(res)-len(bad)}/{len(res)} runs  {secs:.1f}s")
        if bad: print(json.dumps(bad[0], default=str)[:1500])
