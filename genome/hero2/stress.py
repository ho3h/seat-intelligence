"""POST-REGISTRATION stress test on real nets (not part of the frozen corpus; reported separately).
Candidates = genome/exp3 mutation operators applied to native base nets: targeted peepholes (mostly exact) and random structural
mutations (mostly wrong). Ground truth for each candidate = 250 executor runs vs the original. Question: does the normalizer ever
prove a candidate that the executor separates from the original?   usage: python3 -m genome.hero2.stress SHARD NSHARDS OUT.jsonl"""
import glob, json, os, random, sys, time
from genome.netast import parse_book, print_book
from genome.corpus import load_all
from genome.exp3 import mut as M
from genome.hero2.corpus import Case
from genome.hero2.harness import sample_pair
from genome.hero2.prove import Prover
from genome.verify import lint_net


def main():
    shard, nsh, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    every = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    R = load_all()
    files = sorted(glob.glob("runs/exp3/base/*.native.hvm"))
    pids = [os.path.basename(f)[:-len(".native.hvm")] for f in files][3::every]
    pids = pids[shard::nsh]
    done = set()
    if os.path.exists(out):
        for l in open(out):
            r = json.loads(l); done.add((r["pid"], r["op"]))
    fo = open(out, "a")
    import signal
    def _alarm(*a): raise TimeoutError("prover wall-clock guard")
    signal.signal(signal.SIGALRM, _alarm)
    for pid in pids:
        text = open(f"runs/exp3/base/{pid}.native.hvm").read()
        defs, order = parse_book(text)
        cands = []
        for op in M.TARGETED:
            try:
                nd, k = M.apply_all(defs, op)
            except Exception:
                continue
            if k > 0: cands.append((f"T:{op}", nd))
        for op, fn in M.RANDOM.items():
            for i in range(3):
                rng = random.Random(f"{pid}|{op}|{i}")
                try: nd = fn(defs, rng)
                except Exception: nd = None
                if nd is not None: cands.append((f"R:{op}#{i}", nd))
        for name, nd in cands:
            try: ctext = print_book(nd, list(nd))
            except Exception: continue
            if lint_net(ctext) or ctext.strip() == text.strip(): continue
            if (pid, name) in done: continue
            t0 = time.time()
            signal.alarm(90)
            try:
                v = Prover(text, ctext, fuel_def=15000, fuel_top=150000).prove()
                proved, tier, reason = v.equal, v.tier, v.reason
            except Exception as e:
                proved, tier, reason = False, None, "EXC " + repr(e)[:80]
            finally:
                signal.alarm(0)
            case = Case(f"{pid}|{name}", "S", "?", text, ctext, prog=R[pid])
            s = sample_pair(case, 250 if proved else 100, seed=12000, workers=2, timeout=4.0, first_only=not proved)
            rec = {"pid": pid, "op": name, "proved": proved, "tier": tier, "n": s["n"], "disagree": s["disagree"], "secs": round(time.time() - t0, 1)}
            if proved and s["disagree"]: rec["witness"] = s["witnesses"][:2]
            fo.write(json.dumps(rec) + "\n"); fo.flush()
            print(rec, flush=True)


main()
