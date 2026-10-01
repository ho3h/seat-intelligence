"""Assemble runs/exp17/<prog>.bend from runs/exp17/src/<prog>.src: lines `#include <name>` are replaced by
runs/exp17/lib/<name>.bend (each library fragment included once). Usage: build.py prog [out_path]"""
import sys, os, re
D = "/Users/tedsandtads/Genome/runs/exp17"
def build(prog, out=None):
    seen = set(); lines = []
    def emit(path):
        for ln in open(path).read().splitlines():
            m = re.match(r"#include\s+(\S+)", ln)
            if m:
                if m.group(1) not in seen:
                    seen.add(m.group(1)); emit(f"{D}/lib/{m.group(1)}.bend")
            else: lines.append(ln)
    emit(f"{D}/src/{prog}.src")
    out = out or f"{D}/{prog}.bend"
    open(out, "w").write("\n".join(lines).strip() + "\n")
    return out
if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
