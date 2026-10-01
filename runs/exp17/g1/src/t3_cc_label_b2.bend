# t3_cc_label (channel variant): min-label propagation with pre-wired channels (RECON-SWING's idea, in Bend).
# The edge walk creates, per undirected edge, two channels made of unscoped lambdas: the sender `lambda $a` sits in
# u's channel list, the receiver `$a` in v's (and vice versa); both lists are pushed into a vertex-keyed tuple tree
# (keys are input data: the pushes collapse). A round needs no keyed routing: every vertex sends (label, $next) on
# each outgoing channel, reading (label', rest) from each incoming one, where `lambda $next` becomes the channel's
# next sender. Each vertex runs B rounds as a local loop (neighbours synchronise only through the channels, as
# dataflow); after every batch a balanced OR of 'the batch's last round changed something' decides, with the next
# batch spawned before the decision (one-batch lookahead).
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walk(es, zl(l), l, m)
  S0 = st0(A, l, 0, n)
  return flat(loop(S0, 1, l, 2), l, 0, n, [])

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, push(push(A, u, l, m, (lambda $a: 0, $b)), v, l, m, (lambda $b: 0, $a)), l, m)

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

def loop(S, any, l, B):
  (S2, Lin, any2) = rall(S, l, B)
  if any:
    return loop(S2, any2, l, B)
  else:
    return Lin

def rall(S, lv, B):
  switch lv:
    case 0:
      (x, cs) = S
      (x2, cs2, ch) = vrun(x, cs, B, 0)
      return ((x2, cs2), x, ch)
    case _:
      (a, b) = S
      (a2, la, fa) = rall(a, lv-1, B)
      (b2, lb, fb) = rall(b, lv-1, B)
      return ((a2, b2), (la, lb), fa | fb)

def cstep(cs, x):
  match cs:
    case List/Nil:
      return ([], 16777215, 0)
    case List/Cons:
      (s, r) = cs.head
      z = s((x, $n))
      (y, r2) = r
      (rest, my, zs) = cstep(cs.tail, x)
      return (List/Cons((lambda $n: 0, r2), rest), mn(y, my), z | zs)

def vrun(x, cs, B, ch):
  switch B:
    case 0:
      return (x, cs, ch)
    case _:
      (cs2, my, zs) = cstep(cs, x)
      x2 = mn(x, my)
      return vrun(x2, cs2, B-1, (x2 < x) | zs)
