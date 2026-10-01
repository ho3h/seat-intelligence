def prog(x):
  (k, key, clusters, attrs) = x
  values = collect(attrs, clusters, k, key, [])
  return choose(values, values, 16777215, 0)

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return at(xs.tail, i - 1)

def collect(attrs, clusters, k, key, values):
  match attrs:
    case List/Nil:
      return values
    case List/Cons:
      (node, attr_key, value) = attrs.head
      if attr_key == key:
        cluster_id = at(clusters, node)
        if cluster_id == k:
          return collect(attrs.tail, clusters, k, key, List/Cons(value, values))
        else:
          return collect(attrs.tail, clusters, k, key, values)
      else:
        return collect(attrs.tail, clusters, k, key, values)

def count_value(values, target, count):
  match values:
    case List/Nil:
      return count
    case List/Cons:
      if values.head == target:
        return count_value(values.tail, target, count + 1)
      else:
        return count_value(values.tail, target, count)

def choose(candidates, values, best_value, best_count):
  match candidates:
    case List/Nil:
      if best_count == 0:
        return 16777215
      else:
        return best_value
    case List/Cons:
      candidate = candidates.head
      count = count_value(values, candidate, 0)
      if count > best_count:
        return choose(candidates.tail, values, candidate, count)
      else:
        if count == best_count:
          if candidate < best_value:
            return choose(candidates.tail, values, candidate, count)
          else:
            return choose(candidates.tail, values, best_value, best_count)
        else:
          return choose(candidates.tail, values, best_value, best_count)
