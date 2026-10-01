def prog(x):
  (pred, truth) = x
  return outer(pred, truth, 0, 0, 0)

def outer(pred, truth, tp, fp, fn):
  match pred:
    case List/Nil:
      return (tp, fp, fn)
    case List/Cons:
      match truth:
        case List/Nil:
          return (tp, fp, fn)
        case List/Cons:
          (next_tp, next_fp, next_fn) = inner(pred.tail, truth.tail, pred.head, truth.head, tp, fp, fn)
          return outer(pred.tail, truth.tail, next_tp, next_fp, next_fn)

def inner(pred, truth, pred_label, truth_label, tp, fp, fn):
  match pred:
    case List/Nil:
      return (tp, fp, fn)
    case List/Cons:
      match truth:
        case List/Nil:
          return (tp, fp, fn)
        case List/Cons:
          if pred_label == pred.head:
            if truth_label == truth.head:
              return inner(pred.tail, truth.tail, pred_label, truth_label, tp + 1, fp, fn)
            else:
              return inner(pred.tail, truth.tail, pred_label, truth_label, tp, fp + 1, fn)
          else:
            if truth_label == truth.head:
              return inner(pred.tail, truth.tail, pred_label, truth_label, tp, fp, fn + 1)
            else:
              return inner(pred.tail, truth.tail, pred_label, truth_label, tp, fp, fn)
