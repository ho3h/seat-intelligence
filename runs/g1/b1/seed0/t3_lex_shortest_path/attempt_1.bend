def prog(x):
  (n, s, t, edges) = x
  if s >= n:
    return []
  else:
    if t >= n:
      return []
    else:
      states = make_states(n)
      from_t = set_state(states, t, (0, 0, 0))
      optimal = improve(edges, from_t, n - 1)
      (hi, lo, hops) = get_state(optimal, s)
      if hi == 16777215:
        return []
      else:
        return build_path(edges, optimal, n, s, t)

def make_states(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons((16777215, 0, 16777215), make_states(n - 1))

def get_state(xs, idx):
  match xs:
    case List/Nil:
      return (16777215, 0, 16777215)
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

def relax_one(states, a, b, w):
  (ah, al, ap) = get_state(states, a)
  if ah == 16777215:
    return states
  else:
    new_lo = al + w
    if new_lo < al:
      new_hi = ah + 1
    else:
      new_hi = ah
    new_hops = ap + 1
    (bh, bl, bp) = get_state(states, b)
    if better_pair(new_hi, new_lo, new_hops, bh, bl, bp) == 1:
      return set_state(states, b, (new_hi, new_lo, new_hops))
    else:
      return states

def relax_edges(edges, states):
  match edges:
    case List/Nil:
      return states
    case List/Cons:
      (u, v, w) = edges.head
      after_uv = relax_one(states, u, v, w)
      after_vu = relax_one(after_uv, v, u, w)
      return relax_edges(edges.tail, after_vu)

def improve(edges, states, rounds):
  switch rounds:
    case 0:
      return states
    case _:
      next_states = relax_edges(edges, states)
      return improve(edges, next_states, rounds - 1)

def is_opt_step(states, current, nxt, w):
  (ch, cl, cp) = get_state(states, current)
  (nh, nl, np) = get_state(states, nxt)
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
