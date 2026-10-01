"""Q3 depth-vs-size ladder, Q4 core scaling on arm64 C, Q5 stress at large input sizes."""
import glob, json, os, random, re, statistics as S, sys, tempfile, subprocess, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from genome import bend_io as B
from genome.corpus import load_all
from genome.corpus.check import SIZE_EXEMPT
from genome.executor import run_net, HVM, ENV
from genome.verify import assemble, assemble_digest
from genome.digest import py_digest
from genome.types import decode, tup, u24
R = load_all()
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
both = sorted(p for p in NB if p in BB and ok(NB[p][0]) and ok(BB[p][0]))

def nets(p):
    n = open(os.path.join(NB[p][1], "best.hvm")).read()
    bcode = open(os.path.join(BB[p][1], "best.bend")).read()
    book, err = B.compile_bend(B.bend_source(R[p], bcode))
    return n, book

which = sys.argv[1]
rng = random.Random(3)
if which == "q3":
    cands = [p for p in both if p.startswith(("t1_", "t2_", "t4_")) and p not in SIZE_EXEMPT and R[p].inp.__class__.__name__ in ("List", "Tup", "Adt")][:200]
    random.Random(1).shuffle(cands); rows = []
    for p in cands:
        if len(rows) >= 14: break
        prog = R[p]
        try: n, bk = nets(p)
        except Exception: continue
        res = {}
        for sz in (32, 128, 512):
            try:
                x = prog.gen(random.Random(7), sz)
                a = run_net(assemble(prog, n, x), "depth", 60)
                b = run_net(B.assemble_bend(prog, bk, x, digest=False), "depth", 60)
            except Exception: a = b = None
            if not (a and b and a.ok and b.ok): res = None; break
            res[sz] = (a.depth, b.depth, a.itrs, b.itrs)
        if res: rows.append((p, res)); print(p, {k: f"nat {v[0]} / bend {v[1]}" for k, v in res.items()}, flush=True)
    grow = [(r[512][0] / r[32][0]) / (r[512][1] / r[32][1]) for _, r in rows]
    print(f"\nQ3  {len(rows)} programs. depth growth 32->512 (native relative to Bend): median {S.median(grow):.2f}  (<1 means native's advantage grows with size)")
    json.dump([(p, {str(k): v for k, v in r.items()}) for p, r in rows], open("runs/q3.json", "w"))

if which == "q5":
    cands = [p for p in both if p not in SIZE_EXEMPT and not p.startswith("t3_")]
    random.Random(2).shuffle(cands); good = bad = 0; fails = []; tried = 0
    for p in cands:
        if tried >= 40: break
        prog = R[p]; n = open(os.path.join(NB[p][1], "best.hvm")).read()
        big = max(prog.sizes) * 64
        try:
            x = prog.gen(random.Random(11), big); exp = prog.ref(x)
        except Exception: continue
        tried += 1
        r = run_net(assemble_digest(prog, n, x), "run", 120)
        if r.ok:
            try:
                if decode(r.result, tup(u24, u24)) == py_digest(exp, prog.out): good += 1; continue
            except Exception: pass
        bad += 1; fails.append((p, r.error[:60] if not r.ok else "wrong digest"))
    print(f"Q5  correctness at 64x authoring size: {good}/{good+bad} nets still correct; failures: {fails[:8]}")

if which == "q4":
    cands = [p for p in both if p.startswith(("t2_", "t4_")) and p not in SIZE_EXEMPT][:60]; random.Random(5).shuffle(cands); done = 0
    for p in cands:
        if done >= 4: break
        prog = R[p]
        try: n, bk = nets(p)
        except Exception: continue
        x = prog.gen(random.Random(9), max(prog.sizes) * 24)
        row = {}
        for label, text in (("native", assemble(prog, n, x)), ("bend", B.assemble_bend(prog, bk, x, digest=False))):
            d = tempfile.mkdtemp(dir=os.path.join(ROOT, "scratch")); open(d + "/n.hvm", "w").write(text)
            g = subprocess.run([HVM, "gen-c", d + "/n.hvm"], capture_output=True, text=True, env=ENV)
            if g.returncode: row = None; break
            times = {}
            for l2 in (0, 2, 4):
                src = re.sub(r"#define TPC_L2 \d+", f"#define TPC_L2 {l2}", g.stdout); open(d + f"/n{l2}.c", "w").write(src)
                c = subprocess.run(["clang", "-O3", "-mcpu=native", "-o", d + f"/n{l2}", d + f"/n{l2}.c", "-lpthread"], capture_output=True)
                if c.returncode: continue
                t0 = time.time(); r = subprocess.run([d + f"/n{l2}"], capture_output=True, text=True, timeout=120); dt = time.time() - t0
                m = re.search(r"ITRS: (\d+)", r.stdout); times[2 ** l2] = (int(m.group(1)) if m else 0, round(dt, 3))
            row[label] = times
        if row and len(row) == 2: done += 1; print(p, row, flush=True)
