### Bend vs machine-rewritten native (same balanced rope, depth oracle)
| fold | n | native depth | Bend depth | Bend/native depth | native itrs | Bend itrs | Bend/native itrs |
|---|---|---|---|---|---|---|---|
| sum | 1,000 | 151 | 163 | 1.08 | 36,982 | 35,984 | 0.97 |
| sum | 10,000 | 203 | 221 | 1.09 | 369,996 | 360,012 | 0.97 |
| sum | 100,000 | 249 | 268 | 1.08 | 3,700,108 | 3,600,492 | 0.97 |
| max | 1,000 | 231 | 220 | 0.95 | 50,968 | 48,971 | 0.96 |
| max | 10,000 | 315 | 299 | 0.95 | 509,982 | 489,999 | 0.96 |
| max | 100,000 | 385 | 360 | 0.94 | 5,100,094 | 4,900,479 | 0.96 |
| argmax_first | 1,000 | 245 | 292 | 1.19 | 74,950 | 67,701 | 0.90 |
| argmax_first | 10,000 | 337 | 400 | 1.19 | 749,964 | 678,979 | 0.91 |
| argmax_first | 100,000 | 406 | 481 | 1.18 | 7,500,076 | 6,795,175 | 0.91 |
| category_counts | 1,000 | 159 | 171 | 1.08 | 86,952 | 102,943 | 1.18 |
| category_counts | 10,000 | 211 | 229 | 1.09 | 869,966 | 1,029,971 | 1.18 |
| category_counts | 100,000 | 257 | 276 | 1.07 | 8,700,078 | 10,300,451 | 1.18 |
| first_violation | 1,000 | 251 | 267 | 1.06 | 83,951 | 68,231 | 0.81 |
| first_violation | 10,000 | 343 | 336 | 0.98 | 839,965 | 683,898 | 0.81 |
| first_violation | 100,000 | 412 | 413 | 1.00 | 8,400,077 | 6,845,985 | 0.81 |
geomean Bend/native depth 1.059 (range 0.94-1.19); interactions 0.960 (range 0.81-1.18); Bend depth exponents: {'sum': 0.108, 'max': 0.107, 'argmax_first': 0.108, 'category_counts': 0.104, 'first_violation': 0.095}

### Median over the 31 associative folds (rounds / interactions)
| variant | depth 1k | 10k | 100k | depth exponent (median) | itrs 100k | itrs exponent (median) |
|---|---|---|---|---|---|---|
| tree fold on rope (rewrite) | 231 | 315 | 385 | 0.109 | 5,200,097 | 1.000 |
| original list walker | 10,015 | 100,015 | 1,000,015 | 1.000 | 3,900,084 | 1.000 |
| original + K=16 lookahead | 10,016 | 100,016 | 1,000,016 | 1.000 | 3,812,785 | 0.999 |
| in-order sequential fold on the rope (control) | 10,120 | 100,163 | 1,000,197 | 0.997 | 6,300,115 | 1.000 |
| list -> rope -> tree fold (ingest) | 7,852 | 75,492 | 750,585 | 0.990 | 8,700,696 | 0.999 |
| ingest after K=16 lookahead | 2,708 | 24,200 | 238,038 | 0.972 | 8,440,243 | 0.996 |

Per-element rounds at n=100k (median over folds): tree 0.0039 seq 10.00 seq+K16 10.00 ingest 7.51 ingest+K16 2.38
ingest+K16 shallower than the original list walker at 100k on 31/31 folds; vs original+K16 walker: 31/31
ingest+K16 / original ratio at 100k: median 4.20 min 2.94 max 11.33

### Authored originals (accepted corpus nets from the G1 runs) vs the rewrite, 12 corpus folds
| fold | authored depth 1k | 100k | exp | rewrite depth 100k | authored/rewrite |
|---|---|---|---|---|---|
| sum | 7,009 | 700,075 | 1.00 | 249 | 2812x |
| product | 7,508 | 750,074 | 1.00 | 249 | 3012x |
| length | 7,009 | 700,075 | 1.00 | 249 | 2812x |
| max | 16,002 | 1,600,068 | 1.00 | 385 | 4156x |
| min | 16,000 | 1,600,066 | 1.00 | 385 | 4156x |
| count_even | 8,508 | 850,074 | 1.00 | 253 | 3360x |
| argmax_first | 16,011 | 1,600,077 | 1.00 | 406 | 3941x |
| argmin_first | 16,001 | 1,600,068 | 1.00 | 406 | 3941x |
| second_largest | 34,970 | 3,500,034 | 1.00 | 543 | 6446x |
| longest_run | 19,182 | 1,905,732 | 1.00 | 662 | 2879x |
| is_sorted | 2,046 | 3,021 | 0.08 | 388 | 8x |
| last | 7,009 | 700,075 | 1.00 | 273 | 2564x |

### Detection power vs nominal violation rate 2^-k (tester: 10 seeds; verify on the forced tree: seeds 0-2)
{'k': 4, 'tester_detect': 10, 'tester_runs': 10, 'verify': ['fail', 'fail', 'fail']}
{'k': 6, 'tester_detect': 10, 'tester_runs': 10, 'verify': ['fail', 'fail', 'fail']}
{'k': 8, 'tester_detect': 10, 'tester_runs': 10, 'verify': ['fail', 'fail', 'fail']}
{'k': 10, 'tester_detect': 10, 'tester_runs': 10, 'verify': ['fail', 'fail', 'fail']}
{'k': 12, 'tester_detect': 9, 'tester_runs': 10, 'verify': ['fail', 'fail', 'fail']}
{'k': 14, 'tester_detect': 7, 'tester_runs': 10, 'verify': ['pass', 'pass', 'fail']}
{'k': 16, 'tester_detect': 1, 'tester_runs': 10, 'verify': ['pass', 'pass', 'pass']}
{'k': 20, 'tester_detect': 0, 'tester_runs': 10, 'verify': ['pass', 'pass', 'pass']}
{'k': 24, 'tester_detect': 1, 'tester_runs': 10, 'verify': ['fail', 'pass', 'fail']}

### Shape sensitivity (sum)
{'shape': 'balanced', 'n': 1000, 'depth': 151, 'itrs': 36982, 'ok': True}
{'shape': 'balanced', 'n': 5000, 'depth': 189, 'itrs': 184988, 'ok': True}
{'shape': 'left', 'n': 1000, 'depth': 14000, 'itrs': 36982, 'ok': True}
{'shape': 'left', 'n': 5000, 'depth': 70010, 'itrs': 184992, 'ok': True}
{'shape': 'right', 'n': 1000, 'depth': 12004, 'itrs': 36982, 'ok': True}
{'shape': 'right', 'n': 5000, 'depth': 60014, 'itrs': 184992, 'ok': True}
{'shape': 'random', 'n': 1000, 'depth': 7839, 'itrs': 37046, 'ok': True}
{'shape': 'random', 'n': 5000, 'depth': 62463, 'itrs': 185056, 'ok': True}
