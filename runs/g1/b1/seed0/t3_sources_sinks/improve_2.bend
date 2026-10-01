def prog(x):
  (n, edges) = x
  blocks = block_count(n)
  return count_blocks(0, blocks, n, edges)

def block_count(n):
  q = n / 24
  r = n % 24
  if r == 0:
    return q
  else:
    return q + 1

def mark_vertex(mask, vertex, base):
  if vertex >= base:
    offset = vertex - base
    if offset < 24:
      return mask | (1 << offset)
    else:
      return mask
  else:
    return mask

def scan_block(base, edges, incoming, outgoing):
  match edges:
    case List/Nil:
      return (incoming, outgoing)
    case List/Cons:
      (u, v) = edges.head
      next_incoming = mark_vertex(incoming, v, base)
      next_outgoing = mark_vertex(outgoing, u, base)
      return scan_block(base, edges.tail, next_incoming, next_outgoing)

def popcount24(x):
  a = x - ((x >> 1) & 5592405)
  b = (a & 3355443) + ((a >> 2) & 3355443)
  c = (b + (b >> 4)) & 986895
  d = c + (c >> 8)
  e = d + (d >> 16)
  return e & 63

def count_blocks(lo, hi, n, edges):
  if hi <= lo:
    return (0, 0)
  else:
    if hi - lo == 1:
      base = lo * 24
      remaining = n - base
      if remaining < 24:
        valid = remaining
      else:
        valid = 24
      (incoming, outgoing) = scan_block(base, edges, 0, 0)
      return (valid - popcount24(incoming), valid - popcount24(outgoing))
    else:
      mid = lo + (hi - lo) / 2
      (left_sources, left_sinks) = count_blocks(lo, mid, n, edges)
      (right_sources, right_sinks) = count_blocks(mid, hi, n, edges)
      return (left_sources + right_sources, left_sinks + right_sinks)
