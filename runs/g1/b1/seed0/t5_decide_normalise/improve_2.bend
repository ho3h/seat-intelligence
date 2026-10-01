def prog(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      normalized = normalize(xs)
      tree = radix(normalized, 48)
      return emit(tree, List/Nil)

def normalize(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (u, v, score) = xs.head
      tail = normalize(xs.tail)
      if u < v:
        return List/Cons((u, v, score), tail)
      else:
        return List/Cons((v, u, score), tail)

def bit_at(u, v, pos):
  if pos >= 24:
    shift = pos - 24
    return (u >> shift) & 1
  else:
    return (v >> pos) & 1

def partition(xs, pos):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      (zeros, ones) = partition(xs.tail, pos)
      (u, v, score) = xs.head
      bit = bit_at(u, v, pos)
      if bit == 0:
        return (List/Cons(xs.head, zeros), ones)
      else:
        return (zeros, List/Cons(xs.head, ones))

def radix(xs, remaining):
  match xs:
    case List/Nil:
      return (0, (0, 0, 0))
    case List/Cons:
      if remaining == 0:
        (u, v, score) = xs.head
        return leaf_max(xs.tail, u, v, score)
      else:
        pos = remaining - 1
        (zeros, ones) = partition(xs, pos)
        match zeros:
          case List/Nil:
            return radix(ones, pos)
          case List/Cons:
            match ones:
              case List/Nil:
                return radix(zeros, pos)
              case List/Cons:
                zero_tree = radix(zeros, pos)
                one_tree = radix(ones, pos)
                return (1, (zero_tree, one_tree))

def leaf_max(xs, u, v, best):
  match xs:
    case List/Nil:
      return (0, (u, v, best))
    case List/Cons:
      (a, b, score) = xs.head
      if score > best:
        return leaf_max(xs.tail, u, v, score)
      else:
        return leaf_max(xs.tail, u, v, best)

def emit(tree, suffix):
  (tag, payload) = tree
  if tag == 0:
    (u, v, score) = payload
    return List/Cons((u, v, score), suffix)
  else:
    (left, right) = payload
    right_result = emit(right, suffix)
    return emit(left, right_result)
