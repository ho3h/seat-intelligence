"""Builds the SFT set from verified, audited nets: short prompt (task only) -> net. Writes data/sft/{train,valid}.jsonl."""
import glob, json, os, random, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from genome.author_api import get_program
from genome.contract import prompt_short, prompt_short_b1

def main(arm="native"):
    src = "runs/datagen/native/seed0" if arm == "native" else "runs/datagen/b1/seed0"; out = "data/sft" if arm == "native" else "data/sft_bend"; ext = "hvm" if arm == "native" else "bend"
    rows = []
    for f in sorted(glob.glob(f"{src}/*/state.json")):
        s = json.load(open(f))
        if not (s["accepted"] and s.get("audit") == ["pass", "pass"]): continue
        best = os.path.join(os.path.dirname(f), "best." + ext)
        if not os.path.exists(best): continue
        p = get_program(s["pid"])
        net = open(best).read().strip()
        rows.append({"messages": [{"role": "user", "content": (prompt_short if arm == "native" else prompt_short_b1)(p)}, {"role": "assistant", "content": "```\n" + net + "\n```"}], "pid": s["pid"]})
    random.Random(0).shuffle(rows)
    nv = max(20, len(rows) // 20); os.makedirs(out, exist_ok=True)
    for name, part in (("valid", rows[:nv]), ("train", rows[nv:])):
        with open(os.path.join(out, name + ".jsonl"), "w") as fh:
            for r in part: fh.write(json.dumps({"messages": r["messages"]}) + "\n")
    print(f"train {len(rows) - nv}, valid {nv}")

if __name__ == "__main__": main(sys.argv[1] if len(sys.argv) > 1 else "native")
