def prog(x):
  (n, tau, cands) = x
  ordered = sort_candidates(cands, tau, [])
  parents = make_parents(0, n)
  return merge_edges(ordered, parents, 0)

def sort_candidates(xs, tau, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = xs.head
      if score >= tau:
        next_acc = insert_sorted(xs.head, acc)
        return sort_candidates(xs.tail, tau, next_acc)
      else:
        return sort_candidates(xs.tail, tau, acc)

def insert_sorted(edge, xs):
  match xs:
    case List/Nil:
      return List/Cons(edge, List/Nil)
    case List/Cons:
      if comes_before(edge, xs.head):
        return List/Cons(edge, xs)
      else:
        rest = insert_sorted(edge, xs.tail)
        return List/Cons(xs.head, rest)

def comes_before(a, b):
  (au, av, ascore) = a
  (bu, bv, bscore) = b
  if ascore > bscore:
    return true
  else:
    if ascore < bscore:
      return false
    else:
      if au < bu:
        return true
      else:
        if au > bu:
          return false
        else:
          return av < bv

def make_parents(i, n):
  if i == n:
    return List/Nil
  else:
    rest = make_parents(i + 1, n)
    return List/Cons(i, rest)

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        rest = set_at(xs.tail, i - 1, value)
        return List/Cons(xs.head, rest)

def find_root(parents, x):
  p = get_at(parents, x)
  if p == x:
    return x
  else:
    return find_root(parents, p)

def merge_edges(edges, parents, count):
  match edges:
    case List/Nil:
      return count
    case List/Cons:
      (u, v, score) = edges.head
      ru = find_root(parents, u)
      rv = find_root(parents, v)
      if ru == rv:
        return merge_edges(edges.tail, parents, count)
      else:
        next_parents = set_at(parents, rv, ru)
        return merge_edges(edges.tail, next_parents, count + 1)
