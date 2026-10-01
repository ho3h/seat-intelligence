"""promote.py prog suffix: src/<prog><suffix>.bend becomes src/<prog>.bend (old kept in old/), results copied."""
import sys, shutil, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
prog, suf = sys.argv[1], sys.argv[2]
n = 1
while os.path.exists(f"{D}/old/{prog}.v{n}.bend"): n += 1
shutil.copy(f"{D}/src/{prog}.bend", f"{D}/old/{prog}.v{n}.bend")
for s in (0, 1):
    if os.path.exists(f"{D}/res/{prog}.seed{s}.json"): shutil.copy(f"{D}/res/{prog}.seed{s}.json", f"{D}/old/{prog}.v{n}.seed{s}.json")
    shutil.copy(f"{D}/res/{prog}{suf}.seed{s}.json", f"{D}/res/{prog}.seed{s}.json")
shutil.copy(f"{D}/src/{prog}{suf}.bend", f"{D}/src/{prog}.bend")
subprocess.run([sys.executable, f"{D}/build.py", prog], check=True)
print("promoted", prog, suf, "old ->", f"v{n}")
