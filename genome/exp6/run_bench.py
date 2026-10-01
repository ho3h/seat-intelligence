import json, random, sys
from genome.exp6.bench import bench
from genome.exp6.synth import CAT, py_run
SUB16 = ['rev','sort','dedup','scan','take2','take3','drop1','drop2','gt5','lt10','mod2eq0','mod2eq1','aff2_1','add1','xor3','div2']
def examples(tgt, n=3, length=8, hi=30, seed=1):
    rng = random.Random(seed); ex = []
    for _ in range(n):
        xs = [rng.randrange(hi) for _ in range(length)]; ex.append((xs, py_run(tgt, xs)))
    return ex
cfgs = {
 "full108L2": (list(CAT), 2, ['sort','aff2_1']),
 "full108L3": (list(CAT), 3, ['sort','take3','aff2_1']),
 "m16L4": (SUB16, 4, ['sort','take3','aff2_1','rev']),
 "m16L5": (SUB16, 5, ['sort','take3','aff2_1','rev']),
 "m32L3": (SUB16 + [n for n in CAT if n not in SUB16][:16], 3, ['sort','take3','aff2_1']),
}
tag = sys.argv[1]; names, L, tgt = cfgs[tag]
nex = int(sys.argv[2]) if len(sys.argv) > 2 else 3
r = bench(names, L, examples(tgt, nex), n_sample=200, tag=tag + f"_e{nex}")
r["target"] = tgt
json.dump(r, open(f"runs/exp6/bench_{tag}_e{nex}.json", "w"), indent=1)
print(json.dumps(r, indent=1))
