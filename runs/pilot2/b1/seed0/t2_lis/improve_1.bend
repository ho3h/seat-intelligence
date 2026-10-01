def prog(xs):
  return lis(xs, empty_tree(0), 0, 0, 1)

def lis(xs, tree, count, depth, capacity):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      if count == capacity:
        grown = make_node(tree, empty_tree(depth))
        new_depth = depth + 1
        new_capacity = capacity * 2
        updated = insert_tree(grown, new_depth, new_capacity / 2, xs.head)
        return lis(xs.tail, updated, count + 1, new_depth, new_capacity)
      else:
        updated = insert_tree(tree, depth, capacity / 2, xs.head)
        return lis(xs.tail, updated, count + 1, depth, capacity)

def empty_tree(depth):
  switch depth:
    case 0:
      return (0, 0, 0, 0)
    case _:
      sub = empty_tree(depth - 1)
      return make_node(sub, sub)

def make_node(left, right):
  (left_count, left_max, _, _) = left
  (right_count, right_max, _, _) = right
  total = left_count + right_count
  if left_count == 0:
    if right_count == 0:
      maximum = 0
    else:
      maximum = right_max
  else:
    if right_count == 0:
      maximum = left_max
    else:
      if left_max >= right_max:
        maximum = left_max
      else:
        maximum = right_max
  return (total, maximum, left, right)

def insert_tree(tree, depth, half, x):
  switch depth:
    case 0:
      (count, maximum, left, right) = tree
      if count == 0:
        return (1, x, 0, 0)
      else:
        if x <= maximum:
          return (1, x, 0, 0)
        else:
          return tree
    case _:
      (count, maximum, left, right) = tree
      (left_count, left_max, _, _) = left
      if left_count < half:
        updated_left = insert_tree(left, depth - 1, half / 2, x)
        return make_node(updated_left, right)
      else:
        if x <= left_max:
          updated_left = insert_tree(left, depth - 1, half / 2, x)
          return make_node(updated_left, right)
        else:
          updated_right = insert_tree(right, depth - 1, half / 2, x)
          return make_node(left, updated_right)
