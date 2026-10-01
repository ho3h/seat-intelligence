"""Build t5_decide_count: count list triples with score >= tau."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
# Add <home>/Genome to path
sys.path.insert(0, "<home>/Genome")
from genome.lib.graphprims import Book

def decide_count():
    """Count triples (u, v, score) in a list where score >= tau.

    Input: (tau, cands) where tau is 0..1000 and cands is a list of triples.
    Output: count of triples with score >= tau.

    Algorithm: simple recursive list walker that checks each score against tau.
    """
    b = Book()

    b.add("""
@prog = ((tau cands) out)
  & @go ~ (cands (tau (0 out)))

@go = (list state)
  & list ~ ?((@stop @next) state)

@stop = (state s)
  & s ~ (tau (acc out))
  & tau ~ *
  & out ~ acc

@next = (* (tail s))
  & s ~ (tau (acc out))
  & tau ~ {tau1 tau2}
  & tau1 ~ *
  & tail ~ (u_v_score rest)
  & u_v_score ~ (u v_score_pair)
  & u ~ *
  & v_score_pair ~ (v score)
  & v ~ *
  & tau2 ~ {tau2a tau2b}
  & tau2a ~ $([>] $(score cond))
  & cond ~ ?((@skip @incr) (rest (tau2b (acc out))))

@skip = (rest s)
  & s ~ (tau (acc out))
  & @go ~ (rest (tau (acc out)))

@incr = (* ((rest s) z))
  & z ~ *
  & s ~ (tau (acc out))
  & tau ~ *
  & acc ~ $([+] $(1 new_acc))
  & @go ~ (rest (tau (new_acc out)))
""")
    return b

if __name__ == "__main__":
    b = decide_count()
    net_path = os.path.join(D, "net.hvm")
    with open(net_path, "w") as f:
        f.write(b.text())
    print(f"Wrote {net_path}")
    print(f"Net size: {b.size()}")
