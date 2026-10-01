import sys
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.corpus import load_all
from genome import bend_io as B
p = load_all()[sys.argv[1]]
book, err = B.compile_bend(B.bend_source(p, open(sys.argv[2]).read()))
print(err or book)
