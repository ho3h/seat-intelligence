def prog(x):
  (n, k, edges) = x
  if k == 0:
    return n
  else:
    (records, queue) = build_records(n, 0, edges, k)
    return peel(records, queue, k)

def collect_neighbors(v, edges, acc, count):
  match edges:
    case List/Nil:
      return (acc, count)
    case List/Cons:
      (a, b) = edges.head
      if a == v:
        return collect_neighbors(v, edges.tail, List/Cons(b, acc), count + 1)
      else:
        if b == v:
          return collect_neighbors(v, edges.tail, List/Cons(a, acc), count + 1)
        else:
          return collect_neighbors(v, edges.tail, acc, count)

def build_records(n, i, edges, k):
  if i == n:
    return ([], [])
  else:
    (neighbors, d) = collect_neighbors(i, edges, [], 0)
    (rest, queue) = build_records(n, i + 1, edges, k)
    if d < k:
      return (List/Cons((d, 2, neighbors), rest), List/Cons(i, queue))
    else:
      return (List/Cons((d, 1, neighbors), rest), queue)

def record_at(i, records):
  match records:
    case List/Nil:
      return (0, 0, [])
    case List/Cons:
      if i == 0:
        return records.head
      else:
        return record_at(i - 1, records.tail)

def replace_record(i, value, records):
  match records:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, records.tail)
      else:
        return List/Cons(records.head, replace_record(i - 1, value, records.tail))

def lower_degree(v, records, queue, k):
  (d, status, neighbors) = record_at(v, records)
  if status == 1:
    new_d = d - 1
    if new_d < k:
      new_records = replace_record(v, (new_d, 2, neighbors), records)
      return (new_records, List/Cons(v, queue))
    else:
      new_records = replace_record(v, (new_d, 1, neighbors), records)
      return (new_records, queue)
  else:
    return (records, queue)

def peel_neighbors(neighbors, records, queue, k):
  match neighbors:
    case List/Nil:
      return (records, queue)
    case List/Cons:
      (new_records, new_queue) = lower_degree(neighbors.head, records, queue, k)
      return peel_neighbors(neighbors.tail, new_records, new_queue, k)

def count_alive(records, acc):
  match records:
    case List/Nil:
      return acc
    case List/Cons:
      (d, status, neighbors) = records.head
      if status == 1:
        return count_alive(records.tail, acc + 1)
      else:
        return count_alive(records.tail, acc)

def peel(records, queue, k):
  match queue:
    case List/Nil:
      return count_alive(records, 0)
    case List/Cons:
      v = queue.head
      (d, status, neighbors) = record_at(v, records)
      new_records = replace_record(v, (d, 0, neighbors), records)
      (final_records, final_queue) = peel_neighbors(neighbors, new_records, queue.tail, k)
      return peel(final_records, final_queue, k)
