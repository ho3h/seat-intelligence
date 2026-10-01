def prog(xs):
  return lis(xs, empty_tree(0), 0, 0, 1)

def lis(xs, tree, count, depth, capacity):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      state = step(tree, count, depth, capacity, xs.head)
      (next_tree, next_count, next_depth, next_capacity) = state
      return batch(xs.tail, next_tree, next_count, next_depth, next_capacity)

def batch(xs, tree, count, depth, capacity):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      state1 = step(tree, count, depth, capacity, xs.head)
      (tree1, count1, depth1, capacity1) = state1
      rest1 = xs.tail
      match rest1:
        case List/Nil:
          return count1
        case List/Cons:
          state2 = step(tree1, count1, depth1, capacity1, rest1.head)
          (tree2, count2, depth2, capacity2) = state2
          rest2 = rest1.tail
          match rest2:
            case List/Nil:
              return count2
            case List/Cons:
              state3 = step(tree2, count2, depth2, capacity2, rest2.head)
              (tree3, count3, depth3, capacity3) = state3
              return lis(rest2.tail, tree3, count3, depth3, capacity3)

def step(tree, count, depth, capacity, x):
  if count == capacity:
    grown = make_node(tree, empty_tree(depth))
    new_depth = depth + 1
    new_capacity = capacity * 2
    updated = insert_tree(grown, new_depth, capacity, count, x)
    return (updated, count + 1, new_depth, new_capacity)
  else:
    updated = insert_tree(tree, depth, capacity / 2, count, x)
    return (updated, count + 1, depth, capacity)

def empty_tree(depth):
  switch depth:
    case 0:
      return (0, 0, 0)
    case _:
      sub = empty_tree(depth - 1)
      return make_node(sub, sub)

def make_node(left, right):
  (left_max, _, _) = left
  (right_max, _, _) = right
  if left_max >= right_max:
    maximum = left_max
  else:
    maximum = right_max
  return (maximum, left, right)

def insert_tree(tree, depth, half, count, x):
  switch depth:
    case 0:
      return (x, 0, 0)
    case _:
      (maximum, left, right) = tree
      (left_max, _, _) = left
      if count < half:
        updated_left = insert_tree(left, depth - 1, half / 2, count, x)
        return make_node(updated_left, right)
      else:
        if x <= left_max:
          updated_left = insert_tree(left, depth - 1, half / 2, half, x)
          return make_node(updated_left, right)
        else:
          updated_right = insert_tree(right, depth - 1, half / 2, count - half, x)
          return make_node(left, updated_right)
