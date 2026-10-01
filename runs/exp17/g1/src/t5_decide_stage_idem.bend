# t5_decide_stage_idem: keyed trees + return wires + an order-preserving filter whose cells are independent.
# key = target * 8 + verb. The ledger walk ORs a block flag (status <= 1) into Bl; the proposal walk (in parallel)
# min-updates the index of each key's first proposal into F (keys are input data, so both collapse once the depth
# is known), plants a sink for (block, first) at the key, and builds the output as a chain of pick(keep_i, p_i,
# rest) cells, each waiting only for its own keep_i = !block & first == i.
def prog(x):
  (ld, ps) = x
  (Lt, Mt) = lvl(mx(mxl(ld, 0), mxp(ps, 0)) + 1, 0, 1)
  L = Lt + 3
  M = Mt << 3 | (4 * (Lt == 0))
  Bl = lw(ld, zt(L), L, M)
  (out, F, Q) = pw(ps, 0, zinf(L), zl(L), L, M)
  z = deliver_all(zip(Bl, F, L), Q, L)
  if z == 0:
    return out
  else:
    return out

def mxl(xs, a):
  match xs:
    case List/Nil:
      return a
    case List/Cons:
      (vb, t, st) = xs.head
      return mxl(xs.tail, mx(a, t))

def mxp(xs, a):
  match xs:
    case List/Nil:
      return a
    case List/Cons:
      (vb, t) = xs.head
      return mxp(xs.tail, mx(a, t))

def lw(xs, B, L, M):
  match xs:
    case List/Nil:
      return B
    case List/Cons:
      (vb, t, st) = xs.head
      return lw(xs.tail, ork(B, t * 8 + vb, L, M, st <= 1), L, M)

def pw(xs, i, F, Q, L, M):
  match xs:
    case List/Nil:
      return ([], F, Q)
    case List/Cons:
      (vb, t) = xs.head
      k = t * 8 + vb
      (rest, F2, Q2) = pw(xs.tail, i + 1, mink(F, k, L, M, i), push(Q, k, L, M, lambda $bf: 0), L, M)
      (b, f) = $bf
      return (pick((b == 0) & (f == i), (vb, t), rest), F2, Q2)

def pick(k, p, r):
  if k:
    return List/Cons(p, r)
  else:
    return r

def zip(a, b, l):
  switch l:
    case 0:
      return (a, b)
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (zip(a1, b1, l-1), zip(a2, b2, l-1))
