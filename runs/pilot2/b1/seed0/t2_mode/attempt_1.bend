def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return mode_scan(xs, xs, 0, 0)

def mode_scan(candidates, all_values, best, best_count):
  match candidates:
    case List/Nil:
      return best
    case List/Cons:
      value = candidates.head
      count = count_value(all_values, value, 0)
      if count > best_count:
        return mode_scan(candidates.tail, all_values, value, count)
      else:
        if count == best_count:
          if value < best:
            return mode_scan(candidates.tail, all_values, value, count)
          else:
            return mode_scan(candidates.tail, all_values, best, best_count)
        else:
          return mode_scan(candidates.tail, all_values, best, best_count)

def count_value(xs, value, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head == value:
        return count_value(xs.tail, value, acc + 1)
      else:
        return count_value(xs.tail, value, acc)
