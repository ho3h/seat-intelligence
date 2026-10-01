# t3_wsp_dist: Bellman-Ford as a stream dataflow (see sps): every vertex runs its own process emitting its
# distance stream d_0 = (0 at s, INF elsewhere), d_{r+1} = min(d_r, d_r(w) + weight) over its neighbours'
# streams (read through wires set up during the edge walk), with a lagged global change stream for
# termination. Answer: the final distance at t.
#include base
#include sps
def prog(x):
  (n, s, t, es) = x
  if (s >= n) | (t >= n):
    return 16777215
  else:
    (l, m) = lvl(n, 0, 1)
    (D, z) = sps(es, l, m, s)
    return z + get(D, t, l, m)
