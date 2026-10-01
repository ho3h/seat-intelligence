# ---- hooks for components: mode 0 labels = id (min = smallest member), mode 1 labels = 4095 - id (min = largest)
def lab0(mode, base):
  switch mode:
    case 0:
      return base
    case _:
      return 4095 - base

def upd(mode, lab, x):
  return lab - (lab > x) * (lab - x)

def fin(mode, base, lab, ins):
  return ([], lab)
