def prog(x):
  (n, edges) = x
  states = make_states(n, 0)
  states1 = process_edges(edges, states)
  (active_count, odd_count, min_active, min_odd, connected) =
    summarize(states1, 0, 0, 0, 16777215, 16777215, 16777215, 1)
  if active_count == 0:
    return 16777215
  else:
    if connected == 0:
      return 16777215
    else:
      if odd_count == 0:
        return min_active
      else:
        if odd_count == 2:
          return min_odd
        else:
          return 16777215

def make_states(n, i):
  if i == n:
    return List/Nil
  else:
    return List/Cons((0, 0, i), make_states(n, i + 1))

def process_edges(edges, states):
  match edges:
    case List/Nil:
      return states
    case List/Cons:
      (u, v) = edges.head
      (cu, cv) = find_comps(states, 0, u, v, 0, 0, 0, 0)
      states1 = update_edge(states, 0, u, v, cu, cv)
      return process_edges(edges.tail, states1)

def find_comps(states, i, u, v, cu, cv, found_u, found_v):
  if found_u == 1:
    if found_v == 1:
      return (cu, cv)
    else:
      match states:
        case List/Nil:
          return (cu, cv)
        case List/Cons:
          (active, odd, comp) = states.head
          if i == v:
            return find_comps(states.tail, i + 1, u, v, cu, comp, found_u, 1)
          else:
            return find_comps(states.tail, i + 1, u, v, cu, cv, found_u, found_v)
  else:
    if found_v == 1:
      match states:
        case List/Nil:
          return (cu, cv)
        case List/Cons:
          (active, odd, comp) = states.head
          if i == u:
            return find_comps(states.tail, i + 1, u, v, comp, cv, 1, found_v)
          else:
            return find_comps(states.tail, i + 1, u, v, cu, cv, found_u, found_v)
    else:
      match states:
        case List/Nil:
          return (cu, cv)
        case List/Cons:
          (active, odd, comp) = states.head
          if i == u:
            if i == v:
              return find_comps(states.tail, i + 1, u, v, comp, comp, 1, 1)
            else:
              return find_comps(states.tail, i + 1, u, v, comp, cv, 1, found_v)
          else:
            if i == v:
              return find_comps(states.tail, i + 1, u, v, cu, comp, found_u, 1)
            else:
              return find_comps(states.tail, i + 1, u, v, cu, cv, found_u, found_v)

def update_edge(states, i, u, v, cu, cv):
  match states:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (active, odd, comp) = states.head
      if i == u:
        active1 = 1
        odd1 = odd ^ 1
      else:
        active1 = active
        odd1 = odd
      if i == v:
        active2 = 1
        odd2 = odd1 ^ 1
      else:
        active2 = active1
        odd2 = odd1
      if cu != cv:
        if comp == cv:
          comp1 = cu
        else:
          comp1 = comp
      else:
        comp1 = comp
      tail1 = update_edge(states.tail, i + 1, u, v, cu, cv)
      return List/Cons((active2, odd2, comp1), tail1)

def summarize(states, i, active_count, odd_count, min_active, min_odd, root, connected):
  match states:
    case List/Nil:
      return (active_count, odd_count, min_active, min_odd, connected)
    case List/Cons:
      (active, odd, comp) = states.head
      if active == 1:
        if active_count == 0:
          root1 = comp
          connected1 = connected
        else:
          root1 = root
          if comp == root:
            connected1 = connected
          else:
            connected1 = 0
        active_count1 = active_count + 1
        if i < min_active:
          min_active1 = i
        else:
          min_active1 = min_active
      else:
        root1 = root
        connected1 = connected
        active_count1 = active_count
        min_active1 = min_active
      if odd == 1:
        odd_count1 = odd_count + 1
        if i < min_odd:
          min_odd1 = i
        else:
          min_odd1 = min_odd
      else:
        odd_count1 = odd_count
        min_odd1 = min_odd
      return summarize(states.tail, i + 1, active_count1, odd_count1, min_active1, min_odd1, root1, connected1)
