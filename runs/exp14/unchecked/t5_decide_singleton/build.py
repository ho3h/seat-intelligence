#!/usr/bin/env python3
"""Build net.hvm for t5_decide_singleton."""

import sys, os
D = os.path.dirname(os.path.abspath(__file__))

hvm_code = """@prog = ((tau probs) out)
  & @loop ~ ((probs (0 (6 0))) (tau out))
@loop = ((lst idx min_idx max) (tau out))
  & lst ~ ?((@fin @cont) (idx (min_idx (max (tau out)))))
@fin = (idx (min_idx (max (tau out))))
  & idx ~ *
  & max ~ $([<] $(tau check))
  & check ~ ?((@return_6 @return_min) (min_idx out))
@return_6 = (min_idx out)
  & min_idx ~ *
  & 6 ~ out
@return_min = (* (min_idx out))
  & min_idx ~ out
@cont = ((* (val rest)) (idx (min_idx (max (tau out)))))
  & max ~ {max1 max2}
  & val ~ {val1 val2}
  & max1 ~ $([<] $(val1 cond))
  & cond ~ ?((@no_upd @do_upd) (val2 (idx (rest (min_idx (max2 (tau out)))))))
@no_upd = (v (i (r (mi (m (tau out))))))
  & v ~ *
  & i ~ $([+1] ni)
  & @loop ~ ((r (ni (mi m))) (tau out))
@do_upd = (* (v (i (r (mi (m (tau out)))))))
  & mi ~ *
  & m ~ *
  & i ~ $([+1] ni)
  & @loop ~ ((r (ni v)) (tau out))
"""

if __name__ == "__main__":
    path = os.path.join(D, "net.hvm")
    with open(path, "w") as f:
        f.write(hvm_code)
    print(f"wrote {path}")
