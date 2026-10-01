def prog(xs):
  return check_starts(xs, xs, 0)

def check_starts(xs, starts, i):
  match starts:
    case List/Nil:
      return 0
    case List/Cons:
      found = brent_start(xs, i)
      rest = check_starts(xs, starts.tail, i + 1)
      return found + rest

def brent_start(xs, start):
  hare = get_at(xs, start)
  return brent_loop(xs, start, hare, 1, 1)

def brent_loop(xs, tortoise, hare, power, lam):
  if tortoise == hare:
    if lam == 1:
      return 0
    else:
      return 1
  else:
    if power == lam:
      next_hare = get_at(xs, hare)
      return brent_loop(xs, hare, next_hare, power * 2, 1)
    else:
      next_hare = get_at(xs, hare)
      return brent_loop(xs, tortoise, next_hare, power, lam + 1)

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)
