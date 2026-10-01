import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, INF, TUP

def build():
    P = Program()

    def prog(d, k, key, c, attrs):
        d.erase(k, key, c, attrs)
        return INF

    P.prog("t5_prop_majority", prog)
    P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))

if __name__ == "__main__":
    build()
