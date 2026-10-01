def prog(x):
  (n, pairs) = x
  entries = make_entries(0, n)
  merged = process_edges(pairs, entries)
  return collect_sizes(0, merged)

def make_entries(i, n):
  if i == n:
    return []
  else:
    return List/Cons((i, 1), make_entries(i + 1, n))

def get_pair(entries, u, v, i, saved):
  match entries:
    case List/Nil:
      return (saved, saved)
    case List/Cons:
      if i == u:
        return get_pair(entries.tail, u, v, i + 1, entries.head)
      else:
        if i == v:
          return (saved, entries.head)
        else:
          return get_pair(entries.tail, u, v, i + 1, saved)

def merge_entries(entries, old_root, new_root, total):
  match entries:
    case List/Nil:
      return []
    case List/Cons:
      (root, size) = entries.head
      if root == old_root:
        return List/Cons((new_root, total), merge_entries(entries.tail, old_root, new_root, total))
      else:
        if root == new_root:
          return List/Cons((new_root, total), merge_entries(entries.tail, old_root, new_root, total))
        else:
          return List/Cons(entries.head, merge_entries(entries.tail, old_root, new_root, total))

def process_edges(edges, entries):
  match edges:
    case List/Nil:
      return entries
    case List/Cons:
      (u, v) = edges.head
      (entry_u, entry_v) = get_pair(entries, u, v, 0, (0, 0))
      (root_u, size_u) = entry_u
      (root_v, size_v) = entry_v
      if root_u == root_v:
        return process_edges(edges.tail, entries)
      else:
        total = size_u + size_v
        if root_u < root_v:
          updated = merge_entries(entries, root_u, root_v, total)
          return process_edges(edges.tail, updated)
        else:
          updated = merge_entries(entries, root_v, root_u, total)
          return process_edges(edges.tail, updated)

def collect_sizes(i, entries):
  match entries:
    case List/Nil:
      return []
    case List/Cons:
      (root, size) = entries.head
      rest = collect_sizes(i + 1, entries.tail)
      if root == i:
        return List/Cons(size, rest)
      else:
        return rest
