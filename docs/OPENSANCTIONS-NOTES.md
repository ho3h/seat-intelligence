# OpenSanctions Pairs as the G4 real-data source (chosen 2026-09-29)

Source: `data.opensanctions.org/contrib/training/pairs-20251209.json.gz` (409 MB, 755,540 lines, CC BY-NC 4.0, research use only;
the commercial "grouped pairs" need a paid token). Stored under `data/` (gitignored). Analysis: `python -m genome.os_stats`.

Measured structure:
- 1,002,093 entities; 581,149 positive and 174,391 negative analyst judgements; no `unsure` rows in this file.
- Pair types: Person 285k, Occupancy 213k, Company 71k, Organization 35k, Succession 34k, Position 26k.
- Positive closure gives 459,763 clusters: 399k pairs, 20k triples, 4k of size 4... 4,071 of size 10 or more, largest 81.
- Transitive closure implies 1,030,122 pairs against 581,149 explicit positives (x1.77): about 450k merges no analyst judged directly.
- 27 negative judgements fall inside a positive-closure cluster: conflicts in the analysts' own decisions, which a reconciler must detect.

Consequences for the swing: clears the 100,000-node floor by 10x; the negatives are real must-not-link constraints; the transitive-closure
gap is exactly what the reconciliation core does. Gold conflicts are sparse (27), so heavier conflict load comes from scores of a real matcher
(nomenklatura's regression matcher, or an LLM) run over candidate pairs. Subject matter is sanctions and public-record entities; kept out of demos by choice.
Licence blocks commercial use: fine for research and the G4 result, not for a product built on this file.
