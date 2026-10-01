"""Sharing-gain micro-benchmark: superposed search vs the same candidates evaluated one at a time."""
import json, random, sys, statistics
from concurrent.futures import ThreadPoolExecutor
from genome.exp6.synth import *

def bench(stage_names, max_len, examples, n_sample=200, tag="b", seed=0):
    hs = [CAT[n][0] for n in stage_names]
    d, t = sup_program(hs, max_len)
    sup = run_hvm(main_src(t, examples, d), f"runs/exp6/{tag}_sup.hvm")
    n_cand = sum(len(stage_names) ** L for L in range(1, max_len + 1))
    rng = random.Random(seed)
    # uniform sample over the candidate set (weight lengths by their counts)
    lens = list(range(1, max_len + 1)); w = [len(stage_names) ** L for L in lens]
    sample = [[rng.choice(stage_names) for _ in range(rng.choices(lens, w)[0])] for _ in range(n_sample)]
    def one(ip):
        i, p = ip
        return run_hvm(main_src(hlist([CAT[n][0] for n in p]), examples), f"runs/exp6/tmp/{tag}_{i % 6}_{i}.hvm")
    os.makedirs("runs/exp6/tmp", exist_ok=True)
    with ThreadPoolExecutor(6) as ex: ind = list(ex.map(one, enumerate(sample)))
    mean = statistics.mean(r["itrs"] for r in ind)
    wall_mean = statistics.mean(r["wall"] for r in ind)
    # exact survivor count check in python
    py_sols = sum(1 for p in all_programs(stage_names, max_len) if all(py_run(p, xs) == ys for xs, ys in examples)) if n_cand < 2e6 else None
    res = {"tag": tag, "dsl_size": len(stage_names), "max_len": max_len, "n_examples": len(examples), "n_candidates": n_cand,
           "sup_itrs": sup["itrs"], "sup_wall": sup["wall"], "sup_heap": sup["heap"], "sup_survivors": len(sup["sols"]), "py_survivors": py_sols,
           "ind_sample": n_sample, "ind_mean_itrs": mean, "ind_min": min(r["itrs"] for r in ind), "ind_max": max(r["itrs"] for r in ind),
           "ind_total_itrs_extrap": mean * n_cand, "ind_wall_extrap": wall_mean * n_cand,
           "gain_itrs": mean * n_cand / sup["itrs"], "first_sols": sup["sols"][:5]}
    return res

if __name__ == "__main__":
    print(json.dumps(bench(*json.loads(sys.argv[1])), indent=1))
