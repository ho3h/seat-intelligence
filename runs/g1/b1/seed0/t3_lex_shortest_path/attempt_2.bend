def prog(x):
  (n, s, t, edges) = x
  if s >= n:
    return []
  else:
    if t >= n:
      return []
    else:
      if s == t:
        return List/Cons(s, [])
      else:
        states = make_states(n)
        from_t = set_state(states, t, (0, 0, 0, 0))
        optimal = dijkstra(edges, from_t, n, n)
        (hi, lo, hops, done) = get_state(optimal, s)
        if hi == 16777215:
          return []
        else:
          return build_path(edges, optimal, n, s, t)

def make_states(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons((16777215, 0, 16777215, 0), make_states(n - 1))

def get_state(xs, idx):
  match xs:
    case List/Nil:
      return (16777215, 0, 16777215, 0)
    case List/Cons:
      if idx == 0:
        return xs.head
      else:
        return get_state(xs.tail, idx - 1)

def set_state(xs, idx, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_state(xs.tail, idx - 1, value))

def better_pair(ch, cl, cp, bh, bl, bp):
  if ch < bh:
    return 1
  else:
    if ch > bh:
      return 0
    else:
      if cl < bl:
        return 1
      else:
        if cl > bl:
          return 0
        else:
          if cp < bp:
            return 1
          else:
            return 0

def select_min(xs, idx, best_idx, best_hi, best_lo, best_hops):
  match xs:
    case List/Nil:
      return (best_idx, best_hi, best_lo, best_hops)
    case List/Cons:
      (hi, lo, hops, done) = xs.head
      if done == 0:
        if hi != 16777215:
          if better_pair(hi, lo, hops, best_hi, best_lo, best_hops) == 1:
            return select_min(xs.tail, idx + 1, idx, hi, lo, hops)
          else:
            return select_min(xs.tail, idx + 1, best_idx, best_hi, best_lo, best_hops)
        else:
          return select_min(xs.tail, idx + 1, best_idx, best_hi, best_lo, best_hops)
      else:
        return select_min(xs.tail, idx + 1, best_idx, best_hi, best_lo, best_hops)

def mark_done(xs, idx):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        (hi, lo, hops, done) = xs.head
        return List/Cons((hi, lo, hops, 1), xs.tail)
      else:
        return List/Cons(xs.head, mark_done(xs.tail, idx - 1))

def relax_one(states, n, dest, hi, lo, hops, w):
  if dest >= n:
    return states
  else:
    new_lo = lo + w
    if new_lo < lo:
      new_hi = hi + 1
    else:
      new_hi = hi
    new_hops = hops + 1
    (old_hi, old_lo, old_hops, done) = get_state(states, dest)
    if better_pair(new_hi, new_lo, new_hops, old_hi, old_lo, old_hops) == 1:
      return set_state(states, dest, (new_hi, new_lo, new_hops, done))
    else:
      return states

def relax_edges(edges, states, n, current, hi, lo, hops):
  match edges:
    case List/Nil:
      return states
    case List/Cons:
      (u, v, w) = edges.head
      if u == current:
        after_uv = relax_one(states, n, v, hi, lo, hops, w)
      else:
        after_uv = states
      if v == current:
        after_vu = relax_one(after_uv, n, u, hi, lo, hops, w)
      else:
        after_vu = after_uv
      return relax_edges(edges.tail, after_vu, n, current, hi, lo, hops)

def dijkstra(edges, states, n, rounds):
  switch rounds:
    case 0:
      return states
    case _:
      (idx, hi, lo, hops) = select_min(states, 0, n, 16777215, 0, 16777215)
      if idx >= n:
        return states
      else:
        marked = mark_done(states, idx)
        updated = relax_edges(edges, marked, n, idx, hi, lo, hops)
        return dijkstra(edges, updated, n, rounds - 1)

def is_opt_step(states, current, nxt, w):
  (ch, cl, cp, cd) = get_state(states, current)
  (nh, nl, np, nd) = get_state(states, nxt)
  if nh == 16777215:
    return 0
  else:
    total_lo = nl + w
    if total_lo < nl:
      total_hi = nh + 1
    else:
      total_hi = nh
    if total_hi != ch:
      return 0
    else:
      if total_lo != cl:
        return 0
      else:
        if np + 1 != cp:
          return 0
        else:
          return 1

def consider_next(states, current, candidate, w, best):
  if is_opt_step(states, current, candidate, w) == 1:
    if candidate < best:
      return candidate
    else:
      return best
  else:
    return best

def choose_next(edges, states, current, best):
  match edges:
    case List/Nil:
      return best
    case List/Cons:
      (u, v, w) = edges.head
      if u == current:
        best1 = consider_next(states, current, v, w, best)
      else:
        best1 = best
      if v == current:
        best2 = consider_next(states, current, u, w, best1)
      else:
        best2 = best1
      return choose_next(edges.tail, states, current, best2)

def build_path(edges, states, n, current, t):
  if current == t:
    return List/Cons(current, [])
  else:
    nxt = choose_next(edges, states, current, n)
    if nxt >= n:
      return []
    else:
      return List/Cons(current, build_path(edges, states, n, nxt, t))
