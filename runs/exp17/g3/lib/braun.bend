# ---- braun: a list walked once into a Braun tree by cons at the root (the chain of conses is pipelined:
# each cons rebuilds the root immediately). Index 0 = the LAST list element; bget(t, i) is O(log n).
def tobraun(xs, t, c):
  match xs:
    case List/Nil:
      return (t, c)
    case List/Cons:
      return tobraun(xs.tail, bins(t, xs.head), c + 1)

def bget(t, i):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      if i == 0:
        return t.e
      else:
        if i & 1:
          return bget(t.l, (i - 1) >> 1)
        else:
          return bget(t.r, (i - 2) >> 1)
