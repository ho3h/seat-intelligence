def prog(xs):
  return choose_mode(xs, xs, 0, 0)

def choose_mode(xs, all, best_value, best_count):
  match xs:
    case List/Nil:
      return best_value
    case List/Cons:
      count = frequency(all, xs.head, 0)
      if count > best_count:
        return choose_mode(xs.tail, all, xs.head, count)
      else:
        if count == best_count:
          if xs.head < best_value:
            return choose_mode(xs.tail, all, xs.head, count)
          else:
            return choose_mode(xs.tail, all, best_value, best_count)
        else:
          return choose_mode(xs.tail, all, best_value, best_count)

def frequency(xs, value, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head == value:
        return frequency(xs.tail, value, acc + 1)
      else:
        return frequency(xs.tail, value, acc)
