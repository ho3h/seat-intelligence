def prog(formula):
  return popcount8(truth_mask(formula))

def truth_mask(formula):
  match formula:
    case Gbool/C0:
      return 0
    case Gbool/C1:
      return 255
    case Gbool/C2:
      if formula.f0 == 0:
        return 170
      else:
        if formula.f0 == 1:
          return 204
        else:
          return 240
    case Gbool/C3:
      return 255 ^ truth_mask(formula.f0)
    case Gbool/C4:
      return truth_mask(formula.f0) & truth_mask(formula.f1)
    case Gbool/C5:
      return truth_mask(formula.f0) | truth_mask(formula.f1)

def popcount8(x):
  a = x - ((x >> 1) & 85)
  b = (a & 51) + ((a >> 2) & 51)
  return (b & 15) + (b >> 4)
