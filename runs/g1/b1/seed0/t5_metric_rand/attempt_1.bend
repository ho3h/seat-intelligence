def prog(x):
  (pred, truth) = x
  return count_outer(pred, truth, 0)

def count_outer(pred, truth, acc):
  match pred:
    case List/Nil:
      return acc
    case List/Cons:
      match truth:
        case List/Nil:
          return acc
        case List/Cons:
          agreements = count_inner(pred.head, truth.head, pred.tail, truth.tail, 0)
          return count_outer(pred.tail, truth.tail, acc + agreements)

def count_inner(pred_label, truth_label, pred_rest, truth_rest, acc):
  match pred_rest:
    case List/Nil:
      return acc
    case List/Cons:
      match truth_rest:
        case List/Nil:
          return acc
        case List/Cons:
          pred_together = pred_label == pred_rest.head
          truth_together = truth_label == truth_rest.head
          if pred_together == truth_together:
            return count_inner(pred_label, truth_label, pred_rest.tail, truth_rest.tail, acc + 1)
          else:
            return count_inner(pred_label, truth_label, pred_rest.tail, truth_rest.tail, acc)
