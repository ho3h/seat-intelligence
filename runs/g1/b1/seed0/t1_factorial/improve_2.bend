def prog(n):
  if n >= 28:
    return 0
  else:
    if n < 16:
      if n < 8:
        if n < 4:
          if n < 2:
            if n < 1:
              return 1
            else:
              return 2
          else:
            if n < 3:
              return 6
            else:
              return 24
        else:
          if n < 6:
            if n < 5:
              return 120
            else:
              return 720
          else:
            if n < 7:
              return 5040
            else:
              return 40320
      else:
        if n < 12:
          if n < 10:
            if n < 9:
              return 40320
            else:
              return 362880
          else:
            if n < 11:
              return 3628800
            else:
              return 6362368
        else:
          if n < 14:
            if n < 13:
              return 9239552
            else:
              return 2673664
          else:
            if n < 15:
              return 3876864
            else:
              return 7821312
    else:
      if n < 22:
        if n < 19:
          if n < 17:
            return 7700480
          else:
            if n < 18:
              return 13467648
            else:
              return 7536640
        else:
          if n < 20:
            return 8978432
          else:
            if n < 21:
              return 11796480
            else:
              return 12845056
      else:
        if n < 25:
          if n < 23:
            return 14155776
          else:
            if n < 24:
              return 6815744
            else:
              return 12582912
        else:
          if n < 26:
            return 12582912
          else:
            return 8388608
