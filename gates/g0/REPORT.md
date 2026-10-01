# G0 report: can a frozen model write correct raw nets at all?

Date: 2026-09-28. **Outcome: PASS on the pre-registered criterion (20 of 20), with the caveats below. G0 is an instrument, not progress.**

## Charter first

| Pillar | Status | Evidence |
| --- | --- | --- |
| 1. The graph is the program | held | Every answer is HVM2's normal form of the net; the decoder only parses the printed result to compare with the reference. |
| 2. Free of human understanding | **held with a flagged risk** | No Bend or other language was compiled into a net. But the primer's worked example is human-written and the authors' nets reuse its skeleton (`@x = ((?((@x_nil @x_cons) ...`). That is anchoring on a human-authored template, not on Bend. Measured properly at G1 (B3). |
| 3. Not serialized | held, trade declared | Textual net IR at the interface only. |
| 4. Foundational | held | Frozen Claude Opus, no fine-tuning, no bespoke model. |
| 5. Bare metal, simple | held | HVM2 v2.0.22 pinned at `6542760`, unmodified. |
| 6. Graphs all the way down | held | Program, input and execution state are one net; no side tables. |

| Swing rule | Status |
| --- | --- |
| 1. Swing fixed | held. The 200-program end state is unchanged. |
| 2. No smaller targets | held. Nothing shrank. Two corrections were to the test suite (below), not the problem. |
| 3. 10x per phase | n/a. G0 is exempt (rule 4). Not reported as progress. |
| 4. Instruments are not milestones | held. This report does not count toward G1. |
| 5. No "promising" | held. Pass, on the literal criterion. |
| 6. Lanes in parallel | **broken for now.** Lane D (Orbweaver reference) not started; see blockers. Lane C not started. |
| 7. Fixed calendar | held; this is week 1. |
| 8. Rigor in the verifier | held; the suite was made stricter, never smaller. |
| 9. Charter first | held. |

## Result

- 20 programs, 12 from T2 and 8 from T1, drawn by seed before any author ran (`selection.json`).
- **19 of 20 correct on the first submission.** The one miss, `t1_bignum_mul`, was fixed on the second (its author diagnosed that a REF handed straight to an output wire never expands).
- 21 submissions total against a budget of 100.
- All 20 pass the fresh-seed audit (seeds 1 and 2) on the stricter suite v2.
- Transcript audit: every author made exactly one tool call before answering, the read of its own prompt file, plus the harness return channel. No other file was touched.

| Program | Submissions | Median interactions, authoring sizes | Median interactions, largest |
| --- | --- | --- | --- |
| t1_bignum_mul | 2 | 433 | 320677 |
| t1_max | 1 | 304 | 6678 |
| t1_nth | 1 | 117 | 2984 |
| t1_popcount | 1 | 33 | 33 |
| t1_powmod | 1 | 340 | 828 |
| t1_prefix_sums | 1 | 134 | 4367 |
| t1_range | 1 | 109 | 2314 |
| t1_zip_add | 1 | 142 | 3943 |
| t2_argmax | 1 | 226 | 8476 |
| t2_dedup_sorted | 1 | 219 | 6393 |
| t2_distinct_count | 1 | 536 | 37339 |
| t2_inversions | 1 | 1243 | 825235 |
| t2_lis | 1 | 420 | 66432 |
| t2_lower_bound | 1 | 242 | 3246 |
| t2_merge | 1 | 180 | 9606 |
| t2_mode | 1 | 762 | 39266 |
| t2_partition | 1 | 226 | 7202 |
| t2_search | 1 | 165 | 3455 |
| t2_second_largest | 1 | 381 | 10739 |
| t2_top_k | 1 | 743 | 466499 |

## Things that went wrong in my own harness (all corrected, all disclosed)

1. **Bad edge case.** `t2_dedup_sorted` listed the unsorted input `[3,1,2]`, violating its own contract. Two "failures" from one author were against an invalid test and are voided; the author's net passed once the suite was fixed. Added `genome/corpus/check.py` to check preconditions on every generated and edge input across 15 constrained programs.
2. **Suite too loose.** A mutation test (69 random one-token edits to accepted nets) let 6 survive. I added an exhaustive small-input sweep (suite v2: every list up to length 3 over {0,1,2}, filtered by preconditions). Re-checked all accepted nets: all still pass. Re-run: 64 of 69 mutants killed; the 5 survivors are equivalent mutants (four change an internal tag from 1 to 2, which a switch treats identically; one mirrors a BST consistently). This is a change made after seeing results, disclosed here. It only tightens the check.
3. **Collector bug.** My first collector mis-read the agents' return channel, flagged legitimate calls as violations and dropped one reply. Fixed; everything re-collected from transcripts.

## What G0 does and does not show

It shows a frozen model, given the physics and one worked net, writes correct raw nets for a contract-defined function on the first try most of the time, including a bignum multiply and a longest-increasing-subsequence. It does **not** show speed, scale (sizes are 16x authoring at most, tiny by design), the vocabulary, the pen, or that this beats the human route. Those are G1 onward.

## Blockers and open items for Theo

- **Xcode license not accepted** (needs `sudo xcodebuild -license`). I worked around it with `DEVELOPER_DIR=/Library/Developer/CommandLineTools`, which builds fine.
- **Rust toolchain is x86_64 (Intel Homebrew), so HVM2 runs under Rosetta.** Interaction counts are unaffected; wall-clock is not meaningful until there is a native arm64 build. No CUDA here; G1's wall-clock and G4 need rented GPUs.
- **Parallel depth is not measured.** HVM2 does not report it. Needs a separate lockstep oracle before G1.
- **Large outputs overflow HVM2's recursive readback** (about 30,000 deep). At G1 scale the harness must fold outputs to a digest inside the net and subtract its fixed cost. Inputs already scale to 1,000,000 elements via chunked refs.
- **Bend encodes lists differently** from this interface, so B1 needs an adapter. Bend 0.2.38 is built (`physics/bend`) and compiles to HVM2.
- **Lane D week 1 not done.** The `neo4j-orbweaver` MCP server failed to connect (`CONNECTION_CLOSED`) and no Orbweaver reference or replayed graphs are in this directory. I can't build the reconciliation reference or the real-graph replays without them.
- **Author channel.** Headless `claude -p` failed authentication, so authors ran as in-session subagents; scale-up (3 seeds x 200 programs x swarm) needs an API key or a working CLI login.
- **Corpus:** T1 and T2 (60 programs) are written and self-checked. T3, T4 and T5 (140 programs) must be fixed before Phase 1; T5 needs Orbweaver's real logic.
- Answers to your six open questions are still needed; I proceeded on the PRD's defaults (Qwen3 vs a frontier API for G2, spend caps, the name).
