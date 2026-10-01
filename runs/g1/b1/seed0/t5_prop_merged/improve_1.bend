def prog(x):
  (clusters, attrs) = x
  groups = build_groups(attrs, clusters, [])
  return emit_groups(groups)

def get_at(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return get_at(xs.tail, index - 1)

def build_groups(attrs, clusters, groups):
  match attrs:
    case List/Nil:
      return groups
    case List/Cons:
      (node, key, value) = attrs.head
      canonical = get_at(clusters, node)
      updated = add_group(groups, canonical, key, value)
      return build_groups(attrs.tail, clusters, updated)

def add_group(groups, canonical, key, value):
  match groups:
    case List/Nil:
      values = List/Cons((value, 1), [])
      return List/Cons(((canonical, key), values), [])
    case List/Cons:
      (group_key, values) = groups.head
      (group_canonical, group_attribute_key) = group_key
      if canonical < group_canonical:
        new_values = List/Cons((value, 1), [])
        return List/Cons(((canonical, key), new_values), groups)
      else:
        if canonical == group_canonical:
          if key < group_attribute_key:
            new_values = List/Cons((value, 1), [])
            return List/Cons(((canonical, key), new_values), groups)
          else:
            if key == group_attribute_key:
              updated_values = increment_value(values, value)
              return List/Cons((group_key, updated_values), groups.tail)
            else:
              updated_tail = add_group(groups.tail, canonical, key, value)
              return List/Cons(groups.head, updated_tail)
        else:
          updated_tail = add_group(groups.tail, canonical, key, value)
          return List/Cons(groups.head, updated_tail)

def increment_value(values, value):
  match values:
    case List/Nil:
      return List/Cons((value, 1), [])
    case List/Cons:
      (old_value, count) = values.head
      if value == old_value:
        return List/Cons((old_value, count + 1), values.tail)
      else:
        updated_tail = increment_value(values.tail, value)
        return List/Cons(values.head, updated_tail)

def emit_groups(groups):
  match groups:
    case List/Nil:
      return []
    case List/Cons:
      (group_key, values) = groups.head
      (canonical, key) = group_key
      (value, count) = find_best(values, 0, 0, 0)
      return List/Cons((canonical, key, value), emit_groups(groups.tail))

def find_best(values, best_value, best_count, found):
  match values:
    case List/Nil:
      return (best_value, best_count)
    case List/Cons:
      (value, count) = values.head
      if found == 0:
        return find_best(values.tail, value, count, 1)
      else:
        if count > best_count:
          return find_best(values.tail, value, count, 1)
        else:
          if count == best_count:
            if value < best_value:
              return find_best(values.tail, value, count, 1)
            else:
              return find_best(values.tail, best_value, best_count, 1)
          else:
            return find_best(values.tail, best_value, best_count, 1)
