#!/usr/bin/env python3
"""HVM2 for t5_decide_stage_idem - outputs all proposals."""

import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP, HOLE

P = Program()

const_zeros = P.const_trie("z0", 0)
max_val = P.update("max_val", "max")

def ledger_step(d, L, blocked_trie, verb, target, status):
    is_blocking = d.op(status, "<", 2)
    verb_shifted = d.op(verb, "<<", 20)
    key = d.op(verb_shifted, "|", target)
    L1, L2 = d.fanout(L, 2)
    blocked_trie = d.call(max_val, t=blocked_trie, k=key, L=L1, P=is_blocking)
    return L2, blocked_trie

def ledger_fin(d, L, blocked_trie):
    d.erase(L)
    return blocked_trie

ledger_walker = P.stream("ledger", ledger_step, ledger_fin,
                         state=[("L", DEPTH), ("blocked_trie", TRIE(NUM))],
                         elem=TUP(NUM, NUM, NUM))

def proposal_step(d, L, output_val, output_hole, verb, target):
    pair = (verb, target)
    output_hole = d.fill_cons(output_hole, pair)
    return L, output_val, output_hole

def proposal_fin(d, L, output_val, output_hole):
    d.erase(L)
    d.fill(output_hole, d.nil())
    return output_val

proposal_walker = P.stream("proposal", proposal_step, proposal_fin,
                          state=[("L", DEPTH), ("output_val", LIST(TUP(NUM, NUM))),
                                 ("output_hole", HOLE(LIST(TUP(NUM, NUM))))],
                          elem=TUP(NUM, NUM))

def prog(d, ledger, proposals):
    L = 24

    # Process ledger
    initial_blocked = d.call(const_zeros, L=L)
    blocked_trie = d.call(ledger_walker, list=ledger, init=(L, initial_blocked))
    d.erase(blocked_trie)

    # Output all proposals
    output_val, output_hole = d.hole(LIST(TUP(NUM, NUM)))
    output_list = d.call(proposal_walker, list=proposals, init=(L, output_val, output_hole))

    return output_list

P.prog("t5_decide_stage_idem", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Generated net.hvm")
