def prog(xs):
  ordered = radix_sort(xs, 22)
  match ordered:
    case List/Nil:
      return 0
    case List/Cons:
      return scan_mode(ordered.tail, ordered.head, 1, ordered.head, 0)

def radix_sort(xs, shift):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (p, q) = partition4(xs, shift)
          (a, b) = p
          (c, d) = q
          if shift == 0:
            return append(a, append(b, append(c, d)))
          else:
            sorted_a = radix_sort(a, shift - 2)
            sorted_b = radix_sort(b, shift - 2)
            sorted_c = radix_sort(c, shift - 2)
            sorted_d = radix_sort(d, shift - 2)
            return append(sorted_a, append(sorted_b, append(sorted_c, sorted_d)))

def partition4(xs, shift):
  match xs:
    case List/Nil:
      return (([], []), ([], []))
    case List/Cons:
      (p, q) = partition4(xs.tail, shift)
      (a, b) = p
      (c, d) = q
      digit = (xs.head >> shift) & 3
      if digit == 0:
        return ((List/Cons(xs.head, a), b), q)
      else:
        if digit == 1:
          return ((a, List/Cons(xs.head, b)), q)
        else:
          if digit == 2:
            return (p, (List/Cons(xs.head, c), d))
          else:
            return (p, (c, List/Cons(xs.head, d)))

def append(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      return List/Cons(left.head, append(left.tail, right))

def scan_mode(xs, current, current_count, best, best_count):
  match xs:
    case List/Nil:
      if current_count > best_count:
        return current
      else:
        return best
    case List/Cons:
      if xs.head == current:
        return scan_mode(xs.tail, current, current_count + 1, best, best_count)
      else:
        if current_count > best_count:
          return scan_mode(xs.tail, xs.head, 1, current, current_count)
        else:
          return scan_mode(xs.tail, xs.head, 1, best, best_count)
