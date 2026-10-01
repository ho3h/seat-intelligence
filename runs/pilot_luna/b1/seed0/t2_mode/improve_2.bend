def prog(xs):
  sorted = radix_sort(xs, 23, [])
  match sorted:
    case List/Nil:
      return 0
    case List/Cons:
      return scan_mode(sorted.tail, sorted.head, 1, sorted.head, 1)

def radix_sort(xs, bit, tail):
  match xs:
    case List/Nil:
      return tail
    case List/Cons:
      (zero, one) = partition_bit(xs, bit, [], [])
      if bit == 0:
        return append(zero, append(one, tail))
      else:
        sorted_one = radix_sort(one, bit - 1, tail)
        return radix_sort(zero, bit - 1, sorted_one)

def partition_bit(xs, bit, zero, one):
  match xs:
    case List/Nil:
      return (zero, one)
    case List/Cons:
      if ((xs.head >> bit) & 1) == 0:
        return partition_bit(xs.tail, bit, List/Cons(xs.head, zero), one)
      else:
        return partition_bit(xs.tail, bit, zero, List/Cons(xs.head, one))

def append(xs, tail):
  match xs:
    case List/Nil:
      return tail
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, tail))

def scan_mode(xs, current, count, best, best_count):
  match xs:
    case List/Nil:
      if count > best_count:
        return current
      else:
        return best
    case List/Cons:
      if xs.head == current:
        return scan_mode(xs.tail, current, count + 1, best, best_count)
      else:
        if count > best_count:
          return scan_mode(xs.tail, xs.head, 1, current, count)
        else:
          return scan_mode(xs.tail, xs.head, 1, best, best_count)
