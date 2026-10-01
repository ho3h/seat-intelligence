"""Manifest of 60 tasks that are in BOTH adapters' SFT train rows (not valid), stratified by family: the 'can it reproduce
what it was trained on' probe.   python3 -m genome.exp.trainset_probe  -> data/tasksets/train_probe.json"""
import json, os, random, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
from genome.taskgen import task
from genome.contract import prompt_short, prompt_short_b1

WANT = {"pipeline": 12, "reduce": 12, "position": 8, "scan": 8, "treefold": 6, "arith": 6, "rangefn": 5, "sortlike": 3}


def main():
    tr = json.load(open(os.path.join(ROOT, "data/tasksets/train.json")))
    nat = {json.loads(l)["messages"][0]["content"] for l in open(os.path.join(ROOT, "data/sft/train.jsonl"))}
    ben = {json.loads(l)["messages"][0]["content"] for l in open(os.path.join(ROOT, "data/sft_bend/train.jsonl"))}
    both = collections.defaultdict(list)
    for f, i in tr:
        p = task(f, i)
        if prompt_short(p) in nat and prompt_short_b1(p) in ben: both[f].append([f, i])
    r = random.Random(0); out = []
    for f, k in WANT.items(): out += r.sample(both[f], min(k, len(both[f])))
    json.dump(out, open(os.path.join(ROOT, "data/tasksets/train_probe.json"), "w"))
    print(len(out), {f: len(v) for f, v in both.items()})


if __name__ == "__main__": main()
