def prog(x):
  (c, attrs) = x
  mapped = map_attrs(attrs, c)
  return count_clusters(c, mapped, 0, 0)

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return at(xs.tail, i - 1)

def map_attrs(attrs, c):
  match attrs:
    case List/Nil:
      return []
    case List/Cons:
      (node, key, value) = attrs.head
      cluster = at(c, node)
      return List/Cons((cluster, key, value), map_attrs(attrs.tail, c))

def scan_attrs(attrs, cluster, s0, v0, f0, s1, v1, f1, s2, v2, f2, s3, v3, f3):
  match attrs:
    case List/Nil:
      return f0 + f1 + f2 + f3
    case List/Cons:
      (other_cluster, key, value) = attrs.head
      if other_cluster == cluster:
        if key == 0:
          if s0 == 0:
            return scan_attrs(attrs.tail, cluster, 1, value, f0, s1, v1, f1, s2, v2, f2, s3, v3, f3)
          else:
            if value != v0:
              return scan_attrs(attrs.tail, cluster, s0, v0, 1, s1, v1, f1, s2, v2, f2, s3, v3, f3)
            else:
              return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, f1, s2, v2, f2, s3, v3, f3)
        else:
          if key == 1:
            if s1 == 0:
              return scan_attrs(attrs.tail, cluster, s0, v0, f0, 1, value, f1, s2, v2, f2, s3, v3, f3)
            else:
              if value != v1:
                return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, 1, s2, v2, f2, s3, v3, f3)
              else:
                return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, f1, s2, v2, f2, s3, v3, f3)
          else:
            if key == 2:
              if s2 == 0:
                return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, f1, 1, value, f2, s3, v3, f3)
              else:
                if value != v2:
                  return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, f1, s2, v2, 1, s3, v3, f3)
                else:
                  return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, f1, s2, v2, f2, s3, v3, f3)
            else:
              if s3 == 0:
                return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, f1, s2, v2, f2, 1, value, f3)
              else:
                if value != v3:
                  return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, f1, s2, v2, f2, s3, v3, 1)
                else:
                  return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, f1, s2, v2, f2, s3, v3, f3)
      else:
        return scan_attrs(attrs.tail, cluster, s0, v0, f0, s1, v1, f1, s2, v2, f2, s3, v3, f3)

def count_clusters(c, attrs, index, acc):
  match c:
    case List/Nil:
      return acc
    case List/Cons:
      rest = count_clusters(c.tail, attrs, index + 1, acc)
      if c.head == index:
        conflicts = scan_attrs(attrs, index, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        return rest + conflicts
      else:
        return rest
