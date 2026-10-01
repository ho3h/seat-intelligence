def prog(n):
  return count_bits(n, 0)

def count_bits(n, acc):
  if n == 0:
    return acc
  else:
    return count_bits(n & (n - 1), acc + 1)
