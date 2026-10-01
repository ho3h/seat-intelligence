"""G0 driver: pull each author's latest submission from its transcript, verify it, log it.

Usage: python -m genome.g0 collect [prog ...]     verify any new submission, print feedback text
       python -m genome.g0 audit                  fresh-seed audit of every accepted program
"""
from __future__ import annotations
import json, os, re, sys
from .corpus import load_all
from .verify import verify, verify_b1, feedback_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "runs", "g0")
ARM = "native"


def configure(run_dir, arm="native"):
    global RUN, ARM
    RUN = os.path.join(ROOT, "runs", run_dir); ARM = arm

SUBAGENTS = os.path.expanduser("~/.claude/projects/-Users-tedsandtads-Genome/6e03fab2-29b1-44c6-a118-e3b339a8c685/subagents")
MAX_ATTEMPTS = 5


def transcript(agent_id):
    path = os.path.join(SUBAGENTS, f"agent-{agent_id}.jsonl")
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else []


def replies_and_tools(agent_id):
    """-> (assistant replies in order, list of (tool, input) calls excluding the hand-back).

    An author's reply is its SubagentHandback message (the harness's return channel); a plain
    final text block counts only if the turn made no hand-back call."""
    replies, tools, fallback = [], [], []
    for d in transcript(agent_id):
        m = d.get("message")
        if d.get("type") != "assistant" or not isinstance(m, dict): continue
        content = m.get("content")
        if isinstance(content, str): content = [{"type": "text", "text": content}]
        texts, handback = [], None
        for b in content or []:
            if b.get("type") == "text": texts.append(b["text"])
            if b.get("type") == "tool_use":
                if b["name"] == "SubagentHandback": handback = b.get("input", {}).get("message", "")
                else: tools.append((b["name"], b.get("input", {})))
        if handback is not None: replies.append(handback)
        elif texts and not any(b.get("type") == "tool_use" for b in content): fallback.append("\n".join(texts))
    return (replies or fallback), tools


def extract_net(text):
    blocks = re.findall(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
    return blocks[-1].strip() + "\n" if blocks else None


def tool_violations(prog, tools):
    ok_path = os.path.join(RUN, "prompts", f"{prog}.md")
    bad = []
    for name, inp in tools:
        if name == "Read" and inp.get("file_path") == ok_path: continue
        bad.append(f"{name} {json.dumps(inp)[:120]}")
    return bad


def collect(progs):
    R = load_all()
    agents = json.load(open(os.path.join(RUN, "agents.json")))
    for prog in progs:
        d = os.path.join(RUN, prog); os.makedirs(d, exist_ok=True)
        replies, tools = replies_and_tools(agents[prog])
        state_p = os.path.join(d, "state.json")
        state = json.load(open(state_p)) if os.path.exists(state_p) else {"attempts": [], "accepted": False}
        viol = tool_violations(prog, tools)
        state["tool_violations"] = viol
        for k in range(len(state["attempts"]), len(replies)):
            if state["accepted"] or k >= MAX_ATTEMPTS: break
            net = extract_net(replies[k])
            open(os.path.join(d, f"attempt_{k+1}." + ("hvm" if ARM == "native" else "bend")), "w").write(net or "")
            if net is None:
                res = {"status": "reject", "reason": "no fenced code block in reply"}
            else:
                res = verify(R[prog], net, seed=0) if ARM == 'native' else verify_b1(R[prog], net, seed=0)
            fb = feedback_text(R[prog], res)
            open(os.path.join(d, f"feedback_{k+1}.txt"), "w").write(fb + "\n")
            state["attempts"].append({"status": res["status"], "metrics": res.get("metrics"), "failed": res.get("failed")})
            state["accepted"] = res["status"] == "pass"
            state["exhausted"] = (not state["accepted"]) and len(state["attempts"]) >= MAX_ATTEMPTS
            print(f"== {prog} attempt {k+1}: {res['status']}" + (f"  [tool violations: {viol}]" if viol else ""))
            print(fb)
        json.dump(state, open(state_p, "w"), indent=1)
        if not replies: print(f"== {prog}: no reply yet")


def audit():
    R = load_all(); out = {}
    for prog in json.load(open(os.path.join(RUN, "agents.json"))):
        sp = os.path.join(RUN, prog, "state.json")
        if not os.path.exists(sp): continue
        st = json.load(open(sp))
        if not st["accepted"]: continue
        k = len(st["attempts"])
        net = open(os.path.join(RUN, prog, f"attempt_{k}." + ("hvm" if ARM == "native" else "bend"))).read()
        rs = [(verify if ARM == "native" else verify_b1)(R[prog], net, seed=s)["status"] for s in (1, 2)]
        st["audit"] = rs; json.dump(st, open(sp, "w"), indent=1)
        out[prog] = rs; print(prog, rs)
    return out


if __name__ == "__main__":
    if sys.argv[1].startswith("--run="):
        configure(sys.argv[1].split("=")[1], "b1" if "b1" in sys.argv[1] else "native"); sys.argv.pop(1)
    cmd = sys.argv[1]
    if cmd == "collect":
        progs = sys.argv[2:] or list(json.load(open(os.path.join(RUN, "agents.json"))))
        collect(progs)
    elif cmd == "audit":
        audit()
