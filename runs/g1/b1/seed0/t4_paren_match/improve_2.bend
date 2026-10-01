type Tree: Empty | Leaf { value } | Join { left, right }

def prog(xs):
  parsed = parse_seq(xs, 0)
  (remaining, rest1) = parsed
  (next_i, rest2) = rest1
  (tree, stop_i) = rest2
  return flatten(tree)

def parse_seq(xs, i):
  match xs:
    case List/Nil:
      return ([], (i, (Tree/Empty, 0)))
    case List/Cons:
      if xs.head == 41:
        return (xs.tail, (i + 1, (Tree/Empty, i)))
      else:
        inner_result = parse_seq(xs.tail, i + 1)
        (after_inner, inner_rest1) = inner_result
        (after_inner_i, inner_rest2) = inner_rest1
        (inner_tree, close_i) = inner_rest2

        rest_result = parse_seq(after_inner, after_inner_i)
        (after_rest, rest1) = rest_result
        (after_rest_i, rest2) = rest1
        (rest_tree, stop_i) = rest2

        group = make_group(close_i, inner_tree, i)
        tree = append_tree(group, rest_tree)
        return (after_rest, (after_rest_i, (tree, stop_i)))

def make_group(close_i, inner_tree, open_i):
  match inner_tree:
    case Tree/Empty:
      return Tree/Join(Tree/Leaf(close_i), Tree/Leaf(open_i))
    case Tree/Leaf:
      return Tree/Join(
        Tree/Leaf(close_i),
        Tree/Join(inner_tree, Tree/Leaf(open_i))
      )
    case Tree/Join:
      return Tree/Join(
        Tree/Leaf(close_i),
        Tree/Join(inner_tree, Tree/Leaf(open_i))
      )

def append_tree(left, right):
  match right:
    case Tree/Empty:
      return left
    case Tree/Leaf:
      return Tree/Join(left, right)
    case Tree/Join:
      return Tree/Join(left, right)

def flatten(tree):
  return flatten_stack(List/Cons(tree, []), [])

def flatten_stack(stack, out):
  match stack:
    case List/Nil:
      return out
    case List/Cons:
      match stack.head:
        case Tree/Empty:
          return flatten_stack(stack.tail, out)
        case Tree/Leaf:
          return flatten_stack(stack.tail, List/Cons(stack.head.value, out))
        case Tree/Join:
          return flatten_stack(
            List/Cons(
              stack.head.right,
              List/Cons(stack.head.left, stack.tail)
            ),
            out
          )
