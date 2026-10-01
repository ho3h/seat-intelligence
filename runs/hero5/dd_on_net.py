"""Run the delta-debugging SEARCH itself through the verified executor (not the reference) and compare with the stored answers."""
import sys, json, time
sys.path.insert(0, '<home>/Genome')
from concurrent.futures import ProcessPoolExecutor
from genome.hero5.run_eval import *
o = json.load(open('<home>/Genome/runs/hero5/eval_set.json'))
rows = {}
for l in open('<home>/Genome/runs/hero5/results_all.jsonl'):
    r = json.loads(l); rows[(r['id'], r['method'])] = r

def one(did):
    dec = next(d for d in o['decisions'] if d['id'] == did); pr = load_problem(o, dec['src'])
    subj = {dec['subject']} if dec['subject'] is not None else set()
    allf = set(range(pr.F)) - subj
    out = []
    for m in ('DD', 'DDc'):
        orc = Oracle(pr, dec, use_net=True)
        t0 = time.time()
        if m == 'DDc' and dec['polarity'] == 'same':
            fixed = set(range(pr.E, pr.E + pr.M + 1)); E = ddmin([k for k in sorted(allf) if k < pr.E], lambda S: orc(set(S) | fixed))
        else:
            E = ddmin(sorted(allf), orc)
        E = set(E) - subj
        out.append((did, m, sorted(E) == sorted(rows[(did, m)]['E']), orc.calls_net, orc.mismatch, round(time.time() - t0, 1)))
    return out

if __name__ == '__main__':
    ids = [d['id'] for d in o['decisions'] if d['id'] < 50 or d['id'] % 5 == 0]
    with ProcessPoolExecutor(3) as ex:
        for res in ex.map(one, ids):
            for r in res: print(json.dumps(r), flush=True)
