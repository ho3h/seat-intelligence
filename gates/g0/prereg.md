# G0 pre-registration (frozen before any author ran)

Date: 2026-09-28. Question: can a frozen model write correct raw nets at all?

**Instrument, not progress.** G0 exists to find out whether the program should stop. It is not reported as
progress and its sizes are exempt from the 10x rule (swing discipline 3 and 4).

## What is being tested
- 20 programs drawn from T1-T2 (60 contracts) by a seeded draw, `gates/g0/selection.json`, fixed before authors ran.
- Author: a frozen Claude model, submitting nets in HVM2's textual IR. No tools, no repo access, no Bend, no other language in the artifact.
  It receives `PHYSICS.md` and the task contract and nothing else. Author private reasoning is unconstrained (PRD).
- Loop: up to **5 submissions** per program: 1 initial + 4 rounds of feedback (smallest failing input, expected, got; or runtime error).
- Verifier: `python -m genome.verify`, suite seed 0 (edge cases + 24 random at authoring sizes + 6 at 16x). One failure = wrong.
- Audit: every accepted program is re-run on fresh suite seeds 1 and 2. One failure voids the program. (PRD asks for 5%; every program is cheap to check.)

## Pass criterion (literal reading of the PRD)
**All 20 of 20** programs accepted within the attempt budget and surviving the audit.
Also reported, never gating: first-attempt pass count, attempts per program, interaction counts.

## Stop rule (PRD)
Miss -> one written design revision to the author loop (prompt, primer, feedback format; never the tasks) -> rerun the same 20.
Miss again -> the program stops and the result is written up.

## Declared trades (in advance)
1. Textual net IR is the interface (pillar 3 trade, until the pen).
2. Authors run as in-session Claude subagents with tools withheld by instruction, not through the API with a hard tool boundary
   (the headless CLI failed authentication: `OAuth session expired`). Nothing is fine-tuned.
3. `PHYSICS.md` is human-written documentation of the fixed physics and includes one worked net on a non-corpus function.
   Declared as primer material, not a teacher: it is one program, in the medium itself, and not in the corpus.
4. Executor is HVM2 `run` (Rust interpreter) for verification. The binary is x86_64 running under Rosetta on this M5 Max, so
   wall-clock is not yet meaningful; interaction counts are architecture independent. Parallel depth is not yet measured.
5. Spend cap for this phase: the attempt budget above (max 100 author submissions).

## Frozen artifacts
- Author prompts: `runs/g0/prompts/*.md`, sha256 over the 20 files in selection order = `792ac02c3ac621b8...` (first 16 hex).
- Declared trade 6: each author subagent is told to make exactly one read, of its own prompt file, then answer with no further tool use. Enforcement is by instruction, so the repo (including reference implementations) is technically reachable. Any sign of a subagent touching another file voids that program's result.
- Author model: Claude Opus (the `opus` subagent model), frozen, default settings.
