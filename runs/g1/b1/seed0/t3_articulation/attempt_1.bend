def prog(x):
  (n, edges) = x
  adj0 = make_adj(0, n)
  adj = build_adj(edges, adj0)
  word_count = (n + 23) / 24
  marks = make_words(0, word_count)
  base = count_components(0, n, adj, n, marks, 0)
  return count_articulations(0, n, adj, base, 0)

def make_adj(i, n):
  if i == n:
    return []
  else:
    return List/Cons([], make_adj(i + 1, n))

def build_adj(edges, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = add_neighbor(adj, u, v)
      adj2 = add_neighbor(adj1, v, u)
      return build_adj(edges.tail, adj2)

def add_neighbor(adj, index, neighbor):
  match adj:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return List/Cons(List/Cons(neighbor, adj.head), adj.tail)
      else:
        rest = add_neighbor(adj.tail, index - 1, neighbor)
        return List/Cons(adj.head, rest)

def get_adj(adj, index):
  match adj:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return adj.head
      else:
        return get_adj(adj.tail, index - 1)

def make_words(i, count):
  if i == count:
    return []
  else:
    return List/Cons(0, make_words(i + 1, count))

def get_word(words, index):
  match words:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return words.head
      else:
        return get_word(words.tail, index - 1)

def set_word(words, index, value):
  match words:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return List/Cons(value, words.tail)
      else:
        rest = set_word(words.tail, index - 1, value)
        return List/Cons(words.head, rest)

def is_marked(marks, vertex):
  word = get_word(marks, vertex / 24)
  bit = 1 << (vertex % 24)
  if (word & bit) != 0:
    return 1
  else:
    return 0

def mark_vertex(marks, vertex):
  index = vertex / 24
  word = get_word(marks, index)
  bit = 1 << (vertex % 24)
  return set_word(marks, index, word | bit)

def push_all(neighbors, todo):
  match neighbors:
    case List/Nil:
      return todo
    case List/Cons:
      todo2 = List/Cons(neighbors.head, todo)
      return push_all(neighbors.tail, todo2)

def flood(todo, marks, adj, removed):
  match todo:
    case List/Nil:
      return marks
    case List/Cons:
      vertex = todo.head
      rest = todo.tail
      if vertex == removed:
        return flood(rest, marks, adj, removed)
      else:
        already_marked = is_marked(marks, vertex)
        if already_marked == 1:
          return flood(rest, marks, adj, removed)
        else:
          marks2 = mark_vertex(marks, vertex)
          neighbors = get_adj(adj, vertex)
          todo2 = push_all(neighbors, rest)
          return flood(todo2, marks2, adj, removed)

def count_components(i, n, adj, removed, marks, count):
  if i == n:
    return count
  else:
    if i == removed:
      return count_components(i + 1, n, adj, removed, marks, count)
    else:
      already_marked = is_marked(marks, i)
      if already_marked == 1:
        return count_components(i + 1, n, adj, removed, marks, count)
      else:
        todo = List/Cons(i, [])
        marks2 = flood(todo, marks, adj, removed)
        return count_components(i + 1, n, adj, removed, marks2, count + 1)

def count_articulations(i, n, adj, base, count):
  if i == n:
    return count
  else:
    word_count = (n + 23) / 24
    marks = make_words(0, word_count)
    after = count_components(0, n, adj, i, marks, 0)
    if after > base:
      return count_articulations(i + 1, n, adj, base, count + 1)
    else:
      return count_articulations(i + 1, n, adj, base, count)
