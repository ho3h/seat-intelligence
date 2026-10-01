"""Print the swing-20 result logs compactly. usage: python3 -m genome.exp16.show [files...]"""
import json, sys, glob, os
from .run import RUNS
KEYS = ("net", "mode", "N", "n", "accepted", "lp_rounds", "max_deg", "depth", "width", "itrs", "rt_secs", "wall", "max_rss_mb", "correct")
for f in sys.argv[1:] or sorted(glob.glob(os.path.join(RUNS, "*.log"))):
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        print(os.path.basename(f), {k: d[k] for k in KEYS if k in d and d[k] is not None})
