type Tree: Empty | Node { left, val, right, size, height }

def prog(xs):
  return lis(xs, Tree/Empty)

def lis(xs, tails):
  match xs:
    case List/Nil:
      return tree_size(tails)
    case List/Cons:
      next_tails = update(tails, xs.head)
      return lis(xs.tail, next_tails)

def update(t, x):
  (t2, found) = replace_lower(t, x)
  if found == 1:
    return t2
  else:
    return append(t, x)

def replace_lower(t, x):
  match t:
    case Tree/Empty:
      return (Tree/Empty, 0)
    case Tree/Node:
      if x <= t.val:
        (left2, found) = replace_lower(t.left, x)
        if found == 1:
          return (make_node(left2, t.val, t.right), 1)
        else:
          return (make_node(t.left, x, t.right), 1)
      else:
        (right2, found) = replace_lower(t.right, x)
        if found == 1:
          return (make_node(t.left, t.val, right2), 1)
        else:
          return (t, 0)

def append(t, x):
  match t:
    case Tree/Empty:
      return make_node(Tree/Empty, x, Tree/Empty)
    case Tree/Node:
      right2 = append(t.right, x)
      return balance(t.left, t.val, right2)

def balance(left, val, right):
  hl = tree_height(left)
  hr = tree_height(right)
  if hr > hl + 1:
    match right:
      case Tree/Empty:
        return make_node(left, val, right)
      case Tree/Node:
        hrl = tree_height(right.left)
        hrr = tree_height(right.right)
        if hrr >= hrl:
          left2 = make_node(left, val, right.left)
          return make_node(left2, right.val, right.right)
        else:
          match right.left:
            case Tree/Empty:
              return make_node(left, val, right)
            case Tree/Node:
              left2 = make_node(left, val, right.left.left)
              right2 = make_node(right.left.right, right.val, right.right)
              return make_node(left2, right.left.val, right2)
  else:
    return make_node(left, val, right)

def make_node(left, val, right):
  size = tree_size(left) + tree_size(right) + 1
  hl = tree_height(left)
  hr = tree_height(right)
  if hl > hr:
    height = hl + 1
  else:
    height = hr + 1
  return Tree/Node(left, val, right, size, height)

def tree_size(t):
  match t:
    case Tree/Empty:
      return 0
    case Tree/Node:
      return t.size

def tree_height(t):
  match t:
    case Tree/Empty:
      return 0
    case Tree/Node:
      return t.height
