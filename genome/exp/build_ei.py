"""Expert iteration data: the model's own verified samples on the pool, added to the original SFT set.

  python3 -m genome.exp.build_ei native runs/exp/A_native_v1_pool.scored.json data/sft_ei_native [--per-task 2]

Keeps up to --per-task distinct passing samples per task (whitespace-normalised dedup), in the same row format as
genome.build_sft (short prompt -> fenced code). Train = new rows + an equal number of original rows drawn at random (replay),
shuffled; valid = original valid. Prints the suggested iteration count (one pass over train at batch 4).
"""
import json, os, random, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
from genome.taskgen import task
from genome.contract import prompt_short, prompt_short_b1


def main(arm, scored, out, per_task=2):
    src = "data/sft" if arm == "native" else "data/sft_bend"; mk = prompt_short if arm == "native" else prompt_short_b1
    S = json.load(open(scored))["scored"]; rows, fam = [], collections.Counter()
    for f, i in json.load(open(scored))["tasks"]:
        p = task(f, i); seen = set(); k = 0
        for s in S[p.id]:
            if s["status"] != "pass" or k >= per_task: continue
            key = re.sub(r"\s+", " ", s["net"]).strip()
            if key in seen: continue
            seen.add(key); k += 1; fam[f] += 1
            rows.append({"messages": [{"role": "user", "content": mk(p)}, {"role": "assistant", "content": "```\n" + s["net"].strip() + "\n```"}]})
    old = [json.loads(l) for l in open(os.path.join(src, "train.jsonl"))]
    rng = random.Random(1); allr = rows + rng.sample(old, min(len(old), len(rows))); rng.shuffle(allr)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "train.jsonl"), "w") as fh:
        for r in allr: fh.write(json.dumps(r) + "\n")
    open(os.path.join(out, "valid.jsonl"), "w").write(open(os.path.join(src, "valid.jsonl")).read())
    tasks_hit = sum(1 for v in S.values() if any(s["status"] == "pass" for s in v))
    print(json.dumps({"arm": arm, "old_rows": len(old), "new_rows": len(rows), "pool_tasks": len(S), "pool_tasks_with_a_pass": tasks_hit, "new_rows_per_family": fam, "train_rows": len(allr), "iters": max(80, min(250, (len(allr) + 3) // 4))}))


if __name__ == "__main__":
    a = sys.argv[1:]; pt = 2
    if "--per-task" in a: j = a.index("--per-task"); pt = int(a[j + 1]); a = a[:j] + a[j + 2:]
    main(a[0], a[1], a[2], pt)
