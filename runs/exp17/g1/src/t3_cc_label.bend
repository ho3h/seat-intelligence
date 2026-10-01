# t3_cc_label: min-label propagation with pre-wired channels (RECON-SWING's idea, expressed in Bend).
# The edge walk creates two channels per undirected edge from unscoped lambdas: the sender `lambda $c` goes to u's
# out-list, the receiver `$c` to v's in-list (keyed pushes into a vertex-keyed tuple tree; keys are input data, so
# they collapse). A round needs no keyed routing: every vertex sends (label, $next) on each out-channel (`lambda
# $next` becomes that channel's next sender) and destructures (label', rest) from each in-channel. Each vertex runs
# B = 2 rounds as a local loop (neighbours synchronise only through the channels, as dataflow); after each batch a
# balanced OR of "the batch's last round changed something" decides, with the next batch spawned before the
# decision (one-batch lookahead). Labels start as own ids; output = labels.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walk(es, zoi(l), l, m)
  return flat(loop(st0(A, l, 0, n), 1, l, 2), l, 0, n, [])

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, chan(chan(A, u, v, l, m), v, u, l, m), l, m)

def st0(A, lv, base, n):
  switch lv:
    case 0:
      if base < n:
        return (base, A)
      else:
        return (16777215, A)
    case _:
      (a, b) = A
      h = 1 << (lv-1)
      return (st0(a, lv-1, base, n), st0(b, lv-1, base + h, n))
# @lpcore {}
