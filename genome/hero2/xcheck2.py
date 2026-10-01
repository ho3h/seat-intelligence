"""Open-net cross-check: reduce `@prog ~ (x r)` with x OPEN, THEN plug the concrete input into the residual net and finish reducing;
the result must equal the executor's result on the same input. Validates that partial evaluation with open wires preserves behaviour.
usage: python3 -m genome.hero2.xcheck2 [n_programs] [inputs_each]"""
import glob, os, random, sys
from genome import netast
from genome.corpus import load_all
from genome.executor import run_net
from genome.types import encode
from genome.verify import assemble, build_cases
from genome.hero2 import inet as I
from genome.hero2.prove import call_net


def main():
    nprog = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    each = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    R = load_all()
    files = sorted(glob.glob("runs/exp3/base/*.native.hvm"))
    rng = random.Random(11); rng.shuffle(files)
    tot = ok = 0; bad = []
    for f in files[:nprog]:
        pid = os.path.basename(f)[:-len(".native.hvm")]
        p = R[pid]; book = open(f).read()
        cases = [c for c in build_cases(p, 91) if c[0] in ("edge", "small", "enum")]
        rng.shuffle(cases)
        for kind, n, x in cases[:each]:
            root, defs = encode(x, p.inp)
            reg = I.Registry().add_book(book + "\n" + "\n".join(defs) + "\n", "A:").finalize()
            eng = I.Engine(reg, fuel=3_000_000)
            net = call_net("A:")
            eng.run(net)
            itr_open = net.itrs
            tree = netast.parse_book("@t = " + root)[0]["t"][0]
            dnet = I.build_trees(tree, [], "A:")
            fx = next(i for i, k in enumerate(net.kind) if k == "F" and net.val[i] == "x")
            q = net.p[fx][0]
            rp = I.instantiate(net, dnet)
            net.kind[fx] = None
            net.link(rp, q)
            eng.run(net)
            r = run_net(assemble(p, book, x), "run", 30)
            tot += 1
            if not r.ok: bad.append((pid, "exec fail")); continue
            rn = netast.parse_book("@r = " + r.result)[0]["r"]
            expect = I.canon(I.build_trees(rn[0], rn[1], "", root_name="r"), lambda n: n)
            got = I.canon(net, lambda n: n)
            if expect == got: ok += 1
            else: bad.append((pid, kind, "differs", sorted(net.flags)))
    print(f"open-then-plug vs executor: {ok}/{tot} identical results; bad={bad[:10]}")


main()
