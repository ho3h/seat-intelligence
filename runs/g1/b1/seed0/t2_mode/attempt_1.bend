def prog(xs):
  return scan(xs, xs, 0, 0)

def scan(rest, all_values, best, best_count):
  match rest:
    case List/Nil:
      return best
    case List/Cons:
      value = rest.head
      count = count_value(all_values, value, 0)
      if count > best_count:
        return scan(rest.tail, all_values, value, count)
      else:
        if count == best_count:
          if value < best:
            return scan(rest.tail, all_values, value, count)
          else:
            return scan(rest.tail, all_values, best, best_count)
        else:
          return scan(rest.tail, all_values, best, best_count)

def count_value(xs, value, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head == value:
        return count_value(xs.tail, value, acc + 1)
      else:
        return count_value(xs.tail, value, acc)
