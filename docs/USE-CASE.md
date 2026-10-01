# Use case to work back from: a self-maintaining agent memory graph, on a laptop

Status: proposed 2026-09-29, pending Theo's confirmation. Purpose: give every lane (author, vocabulary, pen, swing) one target, so
that a result is judged by whether it moves this, not by whether it beats a strawman.

## The user story (one sentence)
An assistant that lives on your machine keeps a graph of the people, places and things in your life, and keeps it *clean* as facts
arrive: it merges duplicates, refuses merges it should not make, and can show that each change followed a stated rule.

## Why this needs something new
- Today the assistant either calls a hosted model to write a database query (tokens, latency, a cloud round trip, nothing that proves
  the query was right) or runs hand-written merge code that nobody adapts to the user's own data.
- The hard part of memory hygiene is no longer deciding whether two records match (pairwise matchers are near 99% F1 on the largest public
  corpus). It is applying thousands of such decisions consistently: transitive chains, must-not-link conflicts, canonical choice.
- A small local model that *writes* the reconciliation rule as a verified program, checked against real human decisions, addresses that gap.
  The program is exact and parallel; the model only authors it.

## What must be true (each is a testable requirement)
1. **Authorship:** a small model (target 4B parameters or below) writes a correct reconciliation program from a plain-language policy.
   Measured as: fraction of policies for which the program agrees with the reference on a hidden suite (the G1 verifier, extended).
2. **Fidelity to humans:** the resulting policy reproduces real analyst outcomes. Measured on OpenSanctions Pairs: agreement of resulting
   clusters with analyst-final clusters, and the rate of must-not-link violations, at 1,000,000 entities.
3. **Cost of change:** editing a policy costs one authoring call, not a redeploy. Measured as tokens and seconds per policy change.
4. **Exactness under updates:** streaming new pairs, the graph after N updates equals the graph rebuilt from scratch, always.
5. **Verifiability:** every merge is traceable to a rule and its inputs.
6. **Not slower than reasonable:** wall-clock within an order of magnitude of a hand-written union-find on the same machine. We are
   not claiming speed over Rust; we are bounding the price paid for programmability and verification.

## Baselines that would make the result honest
- B-Rust: hand-written union-find with must-not-link checks (speed and correctness reference).
- B-Cypher: an LLM writes a graph-database query per update (cost and latency reference, what agents do today).
- B1: the same author writing Bend.
- Human policy: the nomenklatura rule-based resolver.

## How this changes the plan
- G4 is reframed: not "faster than Bend" alone, but requirements 2, 4 and 6 on 1M entities, with 3 and 5 reported.
- The pen and the fine-tune both have a concrete job: shrink the author while requirement 1 keeps holding.
- The vocabulary (G2) is judged by whether it lowers the size of the author needed for requirement 1.
- Nothing above shrinks the PRD's corpus or swing; it sharpens what the swing is for.
