#!/usr/bin/env python3
"""t5_decide_stage_idem: filter proposals based on ledger and dedup.

Algorithm:
1. Walk the ledger, marking (verb, target) pairs as "blocked" if status is 0 (Staged) or 1 (Applied).
2. Walk the proposals, keeping only those (verb, target) pairs that are:
   - Not marked in the blocked trie, AND
   - Not already kept in this pass (maintained in a kept trie for dedup).
3. Output the kept proposals in original order.

Key packing: (verb << 18) | target fits in 24 bits for verb in 0-5 and target in 0-262143.
"""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, EDGE, WEDGE, HOLE, INF

P = Program()

# Primitives
lg = P.lg()
zeros = P.const_trie("z0", 0)
or_blocked = P.update("or_blocked", "or")      # OR blocking status into trie
peek_check = P.update("peek_check", "peek")    # Check without consuming

def prog(d, ledger, proposals):
    # Use a fixed key depth for tries (20 bits = 1M entries)
    # verb is 0-5 (3 bits) + target should fit comfortably
    L_key = 20
    L_fanout = d.fanout(L_key, 8)  # Fanned out for multiple trie operations

    # ========== Phase 1: Build blocked set from ledger ==========
    # Walk the ledger and mark (verb, target) in blocked trie if status <= 1

    def ledger_step(d, blocked, verb, target, status):
        """For each ledger entry, OR is_blocking into the trie at (verb, target)."""
        # Pack key: (verb << 18) | target
        key = d.op(d.op(verb, "<<", 18), "|", target)

        # Check if status <= 1 (Staged or Applied are blocking)
        # is_blocking = 1 if status in {0, 1}, else 0
        is_blocking = d.op(1, "-", d.op(status, ">", 1))

        # OR is_blocking into blocked trie (leaf := leaf | is_blocking)
        # This sets leaf to 1 if ANY entry has status <= 1
        blocked2 = d.call(or_blocked, t=blocked, k=key, L=L_fanout[0], P=is_blocking)

        return blocked2

    def ledger_fin(d, blocked):
        return blocked

    ledger_walker = P.stream("ledger_walk", ledger_step, ledger_fin,
        state=[("blocked", TRIE(NUM))],
        elem=WEDGE)

    # Initialize and run ledger walker
    blocked_init = d.call(zeros, L=L_fanout[1])
    blocked = d.call(ledger_walker, list=ledger, init=blocked_init)

    # ========== Phase 2: Filter proposals with dedup ==========
    # Walk proposals, checking both blocked and kept tries

    def proposals_step(d, blocked, kept, h_out, verb, target):
        """For each proposal, check if it should be kept."""
        # Fanout verb and target for use in both key packing and output
        verb1, verb2 = d.fanout(verb, 2)
        target1, target2 = d.fanout(target, 2)

        # Pack key and fanout for 3 uses (2 peeks + 1 or)
        packed_key = d.op(d.op(verb1, "<<", 18), "|", target1)
        key1, key2, key3 = d.fanout(packed_key, 3)

        # Check if (verb, target) is in blocked trie (peek without consuming)
        blocked_marker, blocked2 = d.call(peek_check, t=blocked, k=key1, L=L_fanout[2])

        # Check if (verb, target) is in kept trie (peek without consuming)
        kept_marker, kept2 = d.call(peek_check, t=kept, k=key2, L=L_fanout[3])

        # Keep if not blocked AND not already kept
        # is_free = !(blocked_marker | kept_marker) = 1 if both are 0
        is_blocked_or_kept = d.op(blocked_marker, "|", kept_marker)
        is_free_raw = d.op(1, "-", d.op(is_blocked_or_kept, "!", 0))

        # Fanout is_free for use in both or and select
        is_free1, is_free2 = d.fanout(is_free_raw, 2)

        # Mark as kept in kept trie if we're keeping it
        # Only OR 1 if is_free, else OR 0 (no change)
        kept3 = d.call(or_blocked, t=kept2, k=key3, L=L_fanout[4], P=is_free1)

        # Append to output list if keeping (use branch to avoid duplicating the hole)
        def skip_keeping(b, h_out, verb2, target2):
            b.erase(verb2, target2)
            return h_out

        def do_keep(b, dummy, h_out, verb2, target2):
            b.erase(dummy)
            return b.fill_cons(h_out, (verb2, target2))

        h_out2 = d.branch(is_free2, skip_keeping, do_keep, h_out, verb2, target2)

        return blocked2, kept3, h_out2

    def proposals_fin(d, blocked, kept, h_out):
        d.erase(blocked, kept)
        d.fill(h_out, d.nil())
        return 0  # Dummy return (not used; output is via hole)

    proposals_walker = P.stream("proposals_walk", proposals_step, proposals_fin,
        state=[("blocked", TRIE(NUM)), ("kept", TRIE(NUM)), ("h_out", HOLE(LIST(EDGE)))],
        elem=EDGE)

    # Initialize and run proposals walker
    kept_init = d.call(zeros, L=L_fanout[5])
    out_val, out_hole = d.hole(LIST(EDGE))

    fin_result = d.call(proposals_walker, list=proposals, init=(blocked, kept_init, out_hole))
    d.erase(fin_result)

    return out_val

P.prog("t5_decide_stage_idem", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("wrote net.hvm")
