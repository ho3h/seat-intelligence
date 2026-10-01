"""Step 2 data: the native SFT set (data/sft) with each assistant net replaced by its skeleton (wires blanked to `_`).

  python3 -m genome.exp4.sft_skel      -> data/sft_skel/{train,valid}.jsonl
Same prompts (genome.contract.prompt_short, verbatim from data/sft) and same tasks; only the target changes.
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
from genome.netast import parse_book
from genome.exp4.skel import to_skeleton, skeleton_text
from genome.g0 import extract_net


def main():
    os.makedirs("data/sft_skel", exist_ok=True)
    for part in ("train", "valid"):
        n = bad = 0; out = []
        for line in open(f"data/sft/{part}.jsonl"):
            r = json.loads(line); msg = r["messages"]; net = extract_net(msg[-1]["content"])
            try:
                d, o = parse_book(net); sk, _ = to_skeleton(d, o)
            except Exception: bad += 1; continue
            msg = [dict(m) for m in msg]; msg[-1]["content"] = "```\n" + skeleton_text(sk, o) + "```"
            out.append(json.dumps({"messages": msg})); n += 1
        open(f"data/sft_skel/{part}.jsonl", "w").write("\n".join(out) + "\n")
        print(part, n, "skipped", bad)


if __name__ == "__main__": main()
