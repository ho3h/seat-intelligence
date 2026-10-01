"""Why tier D is conditional: feed a DUP NODE (not encoded data) to two nets that tier D calls equal, on the real executor."""
from genome.executor import run_net
CASES = [
    ("F3_dup_erase_one", "@prog = (x out)\n  & x ~ {out *}\n", "@prog = (x x)\n"),
    ("F3_dup_reassoc", "@prog = (x out)\n  & x ~ {a {b c}}\n  & a ~ $([+] $(b s))\n  & s ~ $([+] $(c out))\n",
                       "@prog = (x out)\n  & x ~ {{a b} c}\n  & a ~ $([+] $(b s))\n  & s ~ $([+] $(c out))\n"),
]
for name, A, B in CASES:
    res = []
    for book in (A, B):
        r = run_net("@main = r\n  & @prog ~ ({p q} r)\n  & p ~ 7\n  & q ~ 8\n\n" + book, "run", 10)
        res.append(r.result if r.ok else "ERR")
    print(f"{name}: input = a duplicator node {{7 8}}   A -> {res[0]}   B -> {res[1]}   {'AGREE' if res[0] == res[1] else 'DIFFER'}")
