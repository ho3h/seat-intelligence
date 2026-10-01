"""Fixed sample for exp3: programs solved (accepted + audit-clean) by BOTH arms at G1 seed 0, same layering as genome/opt_eval.py.
Writes runs/exp3/base/{pid}.native.hvm and {pid}.bend.hvm (Bend compiled with the B1 settings) and runs/exp3/sample.json."""
import glob, json, os, random, sys
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT); os.chdir(ROOT)
from genome import bend_io as B
from genome.corpus import load_all

ok = lambda s: s["accepted"] and s.get("audit") == ["pass", "pass"]


def layers(pats):
    out = {}
    for pat in pats:
        for f in glob.glob(pat):
            s = json.load(open(f))
            if s["pid"] not in out or (not ok(out[s["pid"]][0]) and ok(s)): out[s["pid"]] = (s, os.path.dirname(f))
    return out


NB = layers(["runs/g1/native/seed0/*/state.json", "runs/g1r1/native/seed0/*/state.json", "runs/probe2/dsv4/native/seed0/*/state.json", "runs/g1esc/native/seed0/*/state.json"])
BB = layers(["runs/g1/b1/seed0/*/state.json", "runs/g1r1/b1/seed0/*/state.json", "runs/g1esc/b1/seed0/*/state.json"])

if __name__ == "__main__":
    R = load_all()
    both = sorted(p for p in NB if ok(NB[p][0]) and p in BB and ok(BB[p][0]) and NB[p][0].get("best")
                  and os.path.exists(os.path.join(NB[p][1], "best.hvm")) and os.path.exists(os.path.join(BB[p][1], "best.bend")))

    def prep(pid):
        open(f"runs/exp3/base/{pid}.native.hvm", "w").write(open(os.path.join(NB[pid][1], "best.hvm")).read())
        book, err = B.compile_bend(B.bend_source(R[pid], open(os.path.join(BB[pid][1], "best.bend")).read()))
        if err: return pid, False
        open(f"runs/exp3/base/{pid}.bend.hvm", "w").write(book); return pid, True

    with ThreadPoolExecutor(12) as ex: res = dict(ex.map(prep, both))
    both = [p for p in both if res[p]]
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    samp = sorted(random.Random(0).sample(both, min(n, len(both))))
    json.dump({"jointly_solved": both, "sample": samp}, open("runs/exp3/sample.json", "w"), indent=1)
    print(len(both), "jointly solved;", len(samp), "sampled")
