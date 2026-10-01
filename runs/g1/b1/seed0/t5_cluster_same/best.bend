def prog(x):
  (n, pairs, queries) = x
  return answer_queries(queries, pairs)

def answer_queries(queries, edges):
  match queries:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (a, b) = queries.head
      if a == b:
        return List/Cons(1, answer_queries(queries.tail, edges))
      else:
        result = search(List/Cons(a, List/Nil), List/Nil, b, edges)
        return List/Cons(result, answer_queries(queries.tail, edges))

def search(todo, visited, target, edges):
  match todo:
    case List/Nil:
      return 0
    case List/Cons:
      node = todo.head
      rest = todo.tail
      if node == target:
        return 1
      else:
        already_visited = contains(node, visited)
        if already_visited == 1:
          return search(rest, visited, target, edges)
        else:
          more = add_neighbors(node, edges, rest)
          return search(more, List/Cons(node, visited), target, edges)

def contains(value, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(value, xs.tail)

def add_neighbors(node, edges, todo):
  match edges:
    case List/Nil:
      return todo
    case List/Cons:
      (u, v) = edges.head
      if u == node:
        return add_neighbors(node, edges.tail, List/Cons(v, todo))
      else:
        if v == node:
          return add_neighbors(node, edges.tail, List/Cons(u, todo))
        else:
          return add_neighbors(node, edges.tail, todo)
