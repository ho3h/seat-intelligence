type MyTree:
  Leaf
  Node { left, value, right }

def prog(x):
  (a, b) = x
  return insert(a, b)

def insert(x, t):
  match t:
    case MyTree/Leaf:
      return MyTree/Node(MyTree/Leaf, x, MyTree/Leaf)
    case MyTree/Node:
      if x < t.value:
        return MyTree/Node(insert(x, t.left), t.value, t.right)
      else:
        if x > t.value:
          return MyTree/Node(t.left, t.value, insert(x, t.right))
        else:
          return t
