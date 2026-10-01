"""Cross-check of the inet reducer against the real HVM2 executor on CONCRETE closed nets (dev/validation, not a proof attempt).
For each (program, input): reduce `@main` with inet, reduce with the executor, compare the printed result (as a net, canonical code)
and the interaction counts. usage: python3 -m genome.hero2.xcheck [n_programs] [inputs_each]"""
import glob, os, random, sys, time, json
from genome import netast
from genome.corpus import load_all
from genome.executor import run_net
from genome.verify import assemble, build_cases
from genome.hero2 import inet as I


def reduce_closed(text, fuel=3_000_000):
    reg = I.Registry().add_book(text, "").finalize()
    d = reg.defs["main"]
    net = d.tpl.copy()
    I.Engine(reg, fuel=fuel).run(net)
    return net


def result_net(res: str):
    defs, order = netast.parse_book("@r = " + res)
    root, reds = defs["r"]
    return I.build_trees(root, reds)


def compare(text, timeout=30):
    r = run_net(text, "run", timeout)
    if not r.ok: return {"exec_ok": False, "err": r.error[:100]}
    net = reduce_closed(text)
    if "fuel" in net.flags: return {"exec_ok": True, "mine": "fuel", "itrs_exec": r.itrs}
    idc = lambda n: n
    a = I.canon(net, idc)
    try:
        b = I.canon(result_net(r.result), idc)
    except Exception as e:
        return {"exec_ok": True, "mine": "parse-fail " + str(e)[:80], "itrs_exec": r.itrs}
    return {"exec_ok": True, "same": a == b, "itrs_exec": r.itrs, "itrs_mine": net.itrs, "flags": sorted(net.flags)}


def main():
    nprog = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    each = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    R = load_all()
    files = sorted(glob.glob("runs/exp3/base/*.native.hvm"))
    rng = random.Random(7)
    rng.shuffle(files)
    tot = same = 0; diffs = []; itr_eq = 0; itr_n = 0; allpairs = []
    t0 = time.time()
    for f in files[:nprog]:
        pid = os.path.basename(f)[:-len(".native.hvm")]
        p = R[pid]; book = open(f).read()
        cases = [c for c in build_cases(p, 77) if c[0] in ("edge", "small", "enum")]
        rng.shuffle(cases)
        for kind, n, x in cases[:each]:
            text = assemble(p, book, x)
            res = compare(text)
            tot += 1
            if res.get("same"):
                same += 1
                itr_n += 1; itr_eq += (res["itrs_exec"] == res["itrs_mine"]); allpairs.append((res["itrs_exec"], res["itrs_mine"]))
                if res["itrs_exec"] != res["itrs_mine"]: diffs.append((pid, "itrs", res["itrs_exec"], res["itrs_mine"]))
            else: diffs.append((pid, kind, res))
        print(pid, "done", flush=True)
    dd = sorted(e - m for e, m in allpairs)
    print(f"itrs exec-mine: min {dd[0]} median {dd[len(dd)//2]} max {dd[-1]}; exactly +1 (the root call): {sum(1 for x in dd if x == 1)}/{len(dd)}; negative: {sum(1 for x in dd if x < 0)}")
    print(f"programs={nprog} runs={tot} identical-normal-form={same} itrs-equal={itr_eq}/{itr_n} secs={time.time()-t0:.0f}")
    for d in diffs[:30]: print(d)

main()
