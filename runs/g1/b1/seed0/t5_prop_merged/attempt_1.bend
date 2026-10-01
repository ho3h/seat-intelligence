def prog(x):
  (clusters, attrs) = x
  normalized = normalize_attrs(attrs, clusters)
  return scan_nodes(clusters, normalized, 0)

def get_at(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return get_at(xs.tail, index - 1)

def normalize_attrs(attrs, clusters):
  match attrs:
    case List/Nil:
      return []
    case List/Cons:
      (node, key, value) = attrs.head
      canonical = get_at(clusters, node)
      return List/Cons((canonical, key, value), normalize_attrs(attrs.tail, clusters))

def scan_nodes(clusters, attrs, index):
  match clusters:
    case List/Nil:
      return []
    case List/Cons:
      if clusters.head == index:
        return scan_keys(attrs, index, 0, clusters.tail, index + 1)
      else:
        return scan_nodes(clusters.tail, attrs, index + 1)

def scan_keys(attrs, canonical, key, remaining_clusters, next_index):
  if key == 4:
    return scan_nodes(remaining_clusters, attrs, next_index)
  else:
    (found, value, count) = find_mode(attrs, canonical, key, 0, 0, 0, 0)
    if found == 1:
      return List/Cons((canonical, key, value), scan_keys(attrs, canonical, key + 1, remaining_clusters, next_index))
    else:
      return scan_keys(attrs, canonical, key + 1, remaining_clusters, next_index)

def count_value(attrs, canonical, key, value, acc):
  match attrs:
    case List/Nil:
      return acc
    case List/Cons:
      (attr_canonical, attr_key, attr_value) = attrs.head
      if attr_canonical == canonical:
        if attr_key == key:
          if attr_value == value:
            return count_value(attrs.tail, canonical, key, value, acc + 1)
          else:
            return count_value(attrs.tail, canonical, key, value, acc)
        else:
          return count_value(attrs.tail, canonical, key, value, acc)
      else:
        return count_value(attrs.tail, canonical, key, value, acc)

def find_mode(attrs, canonical, key, best_found, best_value, best_count, unused):
  match attrs:
    case List/Nil:
      return (best_found, best_value, best_count)
    case List/Cons:
      (attr_canonical, attr_key, attr_value) = attrs.head
      if attr_canonical == canonical:
        if attr_key == key:
          count = count_value(attrs, canonical, key, attr_value, 0)
          if best_found == 0:
            return find_mode(attrs.tail, canonical, key, 1, attr_value, count, 0)
          else:
            if count > best_count:
              return find_mode(attrs.tail, canonical, key, 1, attr_value, count, 0)
            else:
              if count == best_count:
                if attr_value < best_value:
                  return find_mode(attrs.tail, canonical, key, 1, attr_value, count, 0)
                else:
                  return find_mode(attrs.tail, canonical, key, best_found, best_value, best_count, 0)
              else:
                return find_mode(attrs.tail, canonical, key, best_found, best_value, best_count, 0)
        else:
          return find_mode(attrs.tail, canonical, key, best_found, best_value, best_count, 0)
      else:
        return find_mode(attrs.tail, canonical, key, best_found, best_value, best_count, 0)
