type Tails: Empty | Node { left, val, right, height }

def prog(xs):
  return lis(xs, Tails/Empty, 0)

def lis(xs, tails, count):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      (tails1, added1) = update(tails, xs.head)
      match xs.tail:
        case List/Nil:
          return count + added1
        case List/Cons:
          (tails2, added2) = update(tails1, xs.tail.head)
          return lis(xs.tail.tail, tails2, count + added1 + added2)

def update(tails, x):
  (tails2, found) = replace_lower(tails, x)
  if found == 1:
    return (tails2, 0)
  else:
    return (append(tails, x), 1)

def replace_lower(tails, x):
  match tails:
    case Tails/Empty:
      return (Tails/Empty, 0)
    case Tails/Node:
      if x <= tails.val:
        (left2, found) = replace_lower(tails.left, x)
        if found == 1:
          return (Tails/Node(left2, tails.val, tails.right, tails.height), 1)
        else:
          return (Tails/Node(tails.left, x, tails.right, tails.height), 1)
      else:
        (right2, found) = replace_lower(tails.right, x)
        if found == 1:
          return (Tails/Node(tails.left, tails.val, right2, tails.height), 1)
        else:
          return (tails, 0)

def append(tails, x):
  match tails:
    case Tails/Empty:
      return make_node(Tails/Empty, x, Tails/Empty)
    case Tails/Node:
      right2 = append(tails.right, x)
      return balance(tails.left, tails.val, right2)

def balance(left, val, right):
  hl = tree_height(left)
  hr = tree_height(right)
  if hr > hl + 1:
    match right:
      case Tails/Empty:
        return make_node(left, val, right)
      case Tails/Node:
        hrl = tree_height(right.left)
        hrr = tree_height(right.right)
        if hrr >= hrl:
          left2 = make_node(left, val, right.left)
          return make_node(left2, right.val, right.right)
        else:
          match right.left:
            case Tails/Empty:
              return make_node(left, val, right)
            case Tails/Node:
              left2 = make_node(left, val, right.left.left)
              right2 = make_node(right.left.right, right.val, right.right)
              return make_node(left2, right.left.val, right2)
  else:
    return make_node(left, val, right)

def make_node(left, val, right):
  hl = tree_height(left)
  hr = tree_height(right)
  if hl > hr:
    return Tails/Node(left, val, right, hl + 1)
  else:
    return Tails/Node(left, val, right, hr + 1)

def tree_height(tails):
  match tails:
    case Tails/Empty:
      return 0
    case Tails/Node:
      return tails.height
