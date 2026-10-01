"""Group-1 builder: runs/exp17/<prog>.bend = g1/src/lib.bend + g1/src/<prog>.bend (lib omitted if source starts '# nolib').
A line `# @lpcore {json kwargs}` is replaced by the channel label-propagation core from lpgen.py."""
import sys, json, re
sys.path.insert(0, "/Users/tedsandtads/Genome/runs/exp17/g1")
from lpgen import core
D = "/Users/tedsandtads/Genome/runs/exp17"
for prog in sys.argv[1:]:
    src = open(f"{D}/g1/src/{prog}.bend").read()
    src = re.sub(r"(?m)^# @lpcore (.*)$", lambda m: core(**json.loads(m.group(1))), src)
    lib = "" if src.startswith("# nolib") else open(f"{D}/g1/src/lib.bend").read() + "\n"
    head, rest = src.split("\n", 1)
    open(f"{D}/{prog}.bend", "w").write(head + "\n" + lib + rest)
