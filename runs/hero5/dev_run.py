import json,sys,time
sys.path.insert(0,'<home>/Genome')
from genome.hero5.run_eval import *
o=json.load(open('runs/hero5/dev_set.json'))
ids=[int(x) for x in sys.argv[1:]]
for i in ids:
    t=time.time()
    rows=one(('runs/hero5/dev_set.json','runs/hero5/traces_dev',i))
    d=o['decisions'][i]
    print(i,d['src'],d['kind'],d['a'],d['b'],round(time.time()-t,1),flush=True)
    for r in rows: print('   ',r['method'],r['cls'],r['size'],'S',r['S'],'N',r['N'],'M',r['M'],'F',r['F'],r['claimed'],'calls',r['cost']['net_calls'],round(r['cost']['ref_wall'],1),r['cost'].get('net_replay_secs'),'Nfull',r.get('N_full'),(r.get('sentence') or '')[:150],flush=True)
