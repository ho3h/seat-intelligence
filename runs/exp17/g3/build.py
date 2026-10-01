"""Expand `#include name` lines in src/<prog>.bend with lib/<name>.bend -> <prog>.bend (self-contained)."""
import sys, os, re
D = os.path.dirname(os.path.abspath(__file__))
def expand(path, seen):
    out = []
    for line in open(path):
        m = re.match(r"#include (\w+)", line)
        if m:
            if m.group(1) not in seen:
                seen.add(m.group(1)); out.append(expand(os.path.join(D, "lib", m.group(1) + ".bend"), seen))
        else: out.append(line)
    return "".join(out)
for prog in sys.argv[1:]:
    src = os.path.join(D, "src", prog + ".bend")
    open(os.path.join(D, "out", prog + ".bend"), "w").write(expand(src, set()))
