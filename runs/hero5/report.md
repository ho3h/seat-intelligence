### Class counts, all 100 decisions (denominator 100; hero 50 + synthetic 50)

| method | exact | over-inclusive | incomplete | wrong | exact, hero /50 | exact, synthetic /50 | exact but F not required (S,N,M only) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-D | 0 | 0 | 100 | 0 | 0 | 0 | 0 |
| T-F | 0 | 100 | 0 | 0 | 0 | 0 | 0 |
| T-F+G | 100 | 0 | 0 | 0 | 50 | 50 | 100 |
| T-F+DD | 99 | 0 | 0 | 1 | 49 | 50 | 100 |
| T-F+DDc | 100 | 0 | 0 | 0 | 50 | 50 | 100 |
| DD | 99 | 0 | 0 | 1 | 49 | 50 | 100 |
| DDc | 100 | 0 | 0 | 0 | 50 | 50 | 100 |
| LOO | 60 | 1 | 39 | 0 | 20 | 40 | 60 |
| G-full | 100 | 0 | 0 | 0 | 50 | 50 | 100 |

### Exact per decision type (exact / decisions of that type)

| method | MERGE | MNL | CAP | ORDER |
| --- | --- | --- | --- | --- |
| T-D | 0/28 (0%) | 0/26 (0%) | 0/23 (0%) | 0/23 (0%) |
| T-F | 0/28 (0%) | 0/26 (0%) | 0/23 (0%) | 0/23 (0%) |
| T-F+G | 28/28 (100%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| T-F+DD | 27/28 (96%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| T-F+DDc | 28/28 (100%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| DD | 27/28 (96%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| DDc | 28/28 (100%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| LOO | 18/28 (64%) | 24/26 (92%) | 7/23 (30%) | 11/23 (48%) |
| G-full | 28/28 (100%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |

### Full class breakdown per decision type

**T-D**: MERGE 0/0/28/0; MNL 0/0/26/0; CAP 0/0/23/0; ORDER 0/0/23/0   (order: exact/over-inclusive/incomplete/wrong)

**T-F**: MERGE 0/28/0/0; MNL 0/26/0/0; CAP 0/23/0/0; ORDER 0/23/0/0   (order: exact/over-inclusive/incomplete/wrong)

**T-F+G**: MERGE 28/0/0/0; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**T-F+DD**: MERGE 27/0/0/1; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**T-F+DDc**: MERGE 28/0/0/0; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**DD**: MERGE 27/0/0/1; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**DDc**: MERGE 28/0/0/0; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**LOO**: MERGE 18/1/9/0; MNL 24/0/2/0; CAP 7/0/16/0; ORDER 11/0/12/0   (order: exact/over-inclusive/incomplete/wrong)

**G-full**: MERGE 28/0/0/0; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

### Explanation size (facts named, subject excluded): median [min, max]

| method | hero | synthetic |
| --- | --- | --- |
| T-D | 0 [0, 0] | 0 [0, 0] |
| T-F | 70 [16, 79] | 438 [409, 475] |
| T-F+G | 2 [1, 6] | 2 [2, 7] |
| T-F+DD | 2 [1, 6] | 2 [2, 7] |
| T-F+DDc | 2 [1, 6] | 2 [2, 7] |
| DD | 2 [1, 6] | 2 [2, 7] |
| DDc | 2 [1, 6] | 2 [2, 7] |
| LOO | 1 [0, 6] | 2 [0, 7] |
| G-full | 2 [1, 6] | 2 [2, 7] |

### Full-input necessity diagnostic (facts of E that flip D when deleted from the untouched input)

| method | exact explanations with every fact necessary in the full input | share of facts necessary in the full input (exact explanations) |
| --- | --- | --- |
| T-D | - | - |
| T-F | - | - |
| T-F+G | 61/100 (61%) | 202/265 (76%) |
| T-F+DD | 53/99 (54%) | 169/269 (63%) |
| T-F+DDc | 55/100 (55%) | 173/269 (64%) |
| DD | 53/99 (54%) | 169/269 (63%) |
| DDc | 55/100 (55%) | 173/269 (64%) |
| LOO | 60/60 (100%) | 135/135 (100%) |
| G-full | 61/100 (61%) | 202/265 (76%) |

### Cost of producing the explanation (executor calls and wall clock; classification checks excluded)

| method | net runs per decision, hero median [max] | net runs per decision, synthetic median [max] | executor wall s (replayed sample of every 5th decision), hero median | same, synthetic median |
| --- | --- | --- | --- | --- |
| T-D | 0 [0] | 0 [0] | 0.0 | 0.0 |
| T-F | 0 [0] | 0 [0] | 0.0 | 0.0 |
| T-F+G | 0 [0] | 0 [0] | 0.0 | 0.0 |
| T-F+DD | 20 [174] | 70 [296] | 1.9 | 17.5 |
| T-F+DDc | 25 [174] | 70 [296] | 3.2 | 19.0 |
| DD | 20 [174] | 70 [296] | 1.9 | 17.5 |
| DDc | 25 [174] | 70 [296] | 3.2 | 19.0 |
| LOO | 71 [80] | 439 [476] | 0.0 | 0.0 |
| G-full | 0 [0] | 0 [0] | 0.0 | 0.0 |

Executor runs used to classify the explanations (sufficiency, every single-fact deletion, faithfulness): 3255; each decoded and compared with the reference implementation: 0 disagreements. Executor runs used to replay the search sequences of the timing sample: 5674. Search queries answered by the reference implementation: 53096.

### Order sensitivity of exact explanations of refusals (swap the subject with one edge of E in the E-alone world)

* G-full, MNL: 14/26 (54%) of the exact explanations flip when the subject swaps priority with one of their edges.
* G-full, CAP: 23/23 (100%) of the exact explanations flip when the subject swaps priority with one of their edges.
* G-full, ORDER: 23/23 (100%) of the exact explanations flip when the subject swaps priority with one of their edges.
* DDc, MNL: 14/26 (54%) of the exact explanations flip when the subject swaps priority with one of their edges.
* DDc, CAP: 23/23 (100%) of the exact explanations flip when the subject swaps priority with one of their edges.
* DDc, ORDER: 23/23 (100%) of the exact explanations flip when the subject swaps priority with one of their edges.

### Explanations that were sufficient but unfaithful (class wrong because F failed)

* DD on decision 13 (hero3 MERGE, records 20 and 29): returned facts [0, 1, 2, 3] ([(11, 19, 800), (4, 29, 800), (4, 11, 800), (19, 20, 800)]); D holds with only these rows, but not once the must-not-link rows and the cap that really exist are put back. Context-preserving DD returned [1, 4].
* T-F+DD on decision 13 (hero3 MERGE, records 20 and 29): returned facts [0, 1, 2, 3] ([(11, 19, 800), (4, 29, 800), (4, 11, 800), (19, 20, 800)]); D holds with only these rows, but not once the must-not-link rows and the cap that really exist are put back. Context-preserving DD returned [1, 4].

### Tracing overhead (depth oracle vs the traced copy; same annotated book)

| problem | facts | untraced itrs / depth | traced itrs / depth | untraced oracle s | traced F s | traced D s | ratio F | ratio D | distinct sets F | unions F (memo hit %) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hero1 | 61 | 574,145 / 2,919 | 574,145 / 2,919 | 0.6 | 0.9 | 0.5 | 1.54 | 0.86 | 230 | 212,246 (99.7) |
| hero2 | 63 | 611,857 / 3,128 | 611,857 / 3,128 | 0.5 | 0.6 | 0.8 | 1.24 | 1.57 | 242 | 240,014 (99.7) |
| hero3 | 17 | 194,572 / 947 | 194,572 / 947 | 0.4 | 0.3 | 0.1 | 0.70 | 0.41 | 58 | 57,066 (99.7) |
| hero4 | 71 | 772,765 / 3,357 | 772,765 / 3,357 | 0.7 | 0.9 | 1.2 | 1.37 | 1.75 | 272 | 348,627 (99.8) |
| hero5 | 79 | 884,253 / 2,419 | 884,253 / 2,419 | 0.9 | 1.1 | 0.9 | 1.21 | 1.00 | 389 | 438,576 (99.7) |
| syn9100 | 414 | 84,047,147 / 14,894 | 84,047,147 / 14,894 | 48.0 | 67.4 | 68.6 | 1.40 | 1.43 | 2,798 | 37,216,959 (100.0) |
| syn9101 | 447 | 92,764,088 / 16,352 | 92,764,088 / 16,352 | 59.3 | 75.3 | 76.4 | 1.27 | 1.29 | 3,138 | 41,108,482 (100.0) |
| syn9102 | 458 | 95,044,975 / 16,807 | 95,044,975 / 16,807 | 61.1 | 77.9 | 76.7 | 1.28 | 1.26 | 3,223 | 42,128,707 (100.0) |
| syn9103 | 451 | 92,992,984 / 16,549 | 92,992,984 / 16,549 | 68.1 | 66.2 | 60.7 | 0.97 | 0.89 | 3,131 | 41,210,485 (100.0) |
| syn9104 | 475 | 98,261,057 / 17,364 | 98,261,057 / 17,364 | 48.0 | 72.8 | 58.6 | 1.52 | 1.22 | 3,337 | 43,563,676 (100.0) |
| syn9105 | 439 | 89,097,756 / 15,837 | 89,097,756 / 15,837 | 43.0 | 67.7 | 57.3 | 1.57 | 1.33 | 3,060 | 39,470,657 (100.0) |
| syn9106 | 410 | 83,369,527 / 14,787 | 83,369,527 / 14,787 | 25.4 | 45.4 | 47.2 | 1.79 | 1.86 | 2,792 | 36,909,281 (100.0) |
| syn9107 | 433 | 88,401,043 / 15,607 | 88,401,043 / 15,607 | 29.6 | 54.8 | 54.1 | 1.85 | 1.83 | 2,883 | 39,160,818 (100.0) |
| syn9108 | 465 | 95,054,123 / 16,863 | 95,054,123 / 16,863 | 41.9 | 60.2 | 53.1 | 1.43 | 1.27 | 3,201 | 42,128,424 (100.0) |
| syn9109 | 461 | 95,280,727 / 17,079 | 95,280,727 / 17,079 | 47.8 | 63.1 | 53.7 | 1.32 | 1.12 | 3,137 | 42,232,738 (100.0) |
| syn9110 | 469 | 97,119,012 / 17,100 | 97,119,012 / 17,100 | 49.6 | 61.4 | 54.1 | 1.24 | 1.09 | 3,201 | 43,051,567 (100.0) |
| syn9111 | 463 | 96,199,636 / 17,063 | 96,199,636 / 17,063 | 49.6 | 59.1 | 50.8 | 1.19 | 1.02 | 3,181 | 42,642,010 (100.0) |
| syn9112 | 420 | 85,667,114 / 15,275 | 85,667,114 / 15,275 | 37.8 | 45.5 | 39.0 | 1.20 | 1.03 | 2,805 | 37,933,871 (100.0) |
| syn9113 | 428 | 88,412,389 / 15,781 | 88,412,389 / 15,781 | 35.8 | 45.5 | 42.8 | 1.27 | 1.20 | 3,017 | 39,163,344 (100.0) |
| syn9114 | 432 | 89,097,464 / 15,869 | 89,097,464 / 15,869 | 33.5 | 45.1 | 44.3 | 1.35 | 1.32 | 2,949 | 39,471,297 (100.0) |
| syn9115 | 436 | 89,790,075 / 15,911 | 89,790,075 / 15,911 | 35.9 | 40.7 | 37.8 | 1.13 | 1.05 | 2,966 | 39,777,756 (100.0) |
| syn9116 | 417 | 85,190,838 / 15,153 | 85,190,838 / 15,153 | 30.2 | 39.0 | 34.9 | 1.29 | 1.16 | 2,922 | 37,727,541 (100.0) |
| syn9117 | 474 | 98,034,410 / 17,347 | 98,034,410 / 17,347 | 36.7 | 44.6 | 38.0 | 1.22 | 1.04 | 2,982 | 43,462,003 (100.0) |
| syn9118 | 437 | 89,554,808 / 15,837 | 89,554,808 / 15,837 | 30.5 | 40.1 | 36.4 | 1.31 | 1.19 | 2,883 | 39,674,552 (100.0) |
| syn9119 | 437 | 89,999,050 / 15,914 | 89,999,050 / 15,914 | 30.5 | 41.0 | 36.1 | 1.34 | 1.18 | 3,036 | 39,875,989 (100.0) |
| syn9120 | 424 | 86,338,170 / 15,403 | 86,338,170 / 15,403 | 29.3 | 39.7 | 16.3 | 1.35 | 0.56 | 2,969 | 38,239,239 (100.0) |
| syn9121 | 445 | 92,518,441 / 16,478 | 92,518,441 / 16,478 | 16.4 | 38.6 | 34.7 | 2.35 | 2.11 | 2,920 | 41,004,256 (100.0) |
| syn9122 | 441 | 90,699,224 / 16,033 | 90,699,224 / 16,033 | 27.8 | 37.7 | 35.0 | 1.36 | 1.26 | 3,087 | 40,184,676 (100.0) |
| syn9123 | 415 | 84,045,090 / 14,886 | 84,045,090 / 14,886 | 26.4 | 35.4 | 31.4 | 1.34 | 1.19 | 2,854 | 37,214,893 (100.0) |
| syn9124 | 443 | 91,153,280 / 16,098 | 91,153,280 / 16,098 | 27.9 | 35.9 | 28.6 | 1.29 | 1.02 | 3,076 | 40,390,747 (100.0) |

Wall-clock ratio traced/untraced: policy F median 1.32 (range 0.70-2.35); policy D median 1.19 (range 0.41-2.11).

### What the trace says (causal set sizes)

* policy F: the causal set equals the whole input (every fact) for 100 of 100 decisions; median share of the input 1.00.
* policy D: empty for 100 of 100 decisions; largest 0.

### Example sentences (T-F+G, all exact; these are outputs of a game with the host's rules, not claims about the guests)

* [hero5 MERGE, 2 facts] Chamath Palihapitiya sits with David Sacks because each link in the chain was accepted and merged in priority order: Chamath Palihapitiya-Greg Brockman (score 750), Greg Brockman-David Sacks (score 750).
* [hero4 MERGE, 1 facts] Shyam Sankar sits with Alex Karp because each link in the chain was accepted and merged in priority order: Shyam Sankar-Alex Karp (score 1000).
* [hero2 MNL, 2 facts] Greg Brockman was kept out of Dario Amodei's section because the must-not-link rule forbids Greg Brockman with Dario Amodei: Greg Brockman is itself one end of that rule, and Dario Amodei is itself one end of that rule.
* [hero4 MNL, 2 facts] Satya Nadella was kept out of Elon Musk's section because the must-not-link rule forbids Satya Nadella with Elon Musk: Satya Nadella is itself one end of that rule, and Elon Musk is itself one end of that rule.
* [hero5 CAP, 7 facts] VPOTUS was kept out of Jared Isaacman's section because the size limit of 6 would be exceeded: 6 guests already with VPOTUS plus 1 already with Jared Isaacman is more than 6.
* [hero2 CAP, 7 facts] Speaker Johnson was kept out of Director Clayton's section because the size limit of 6 would be exceeded: 6 guests already with Speaker Johnson plus 1 already with Director Clayton is more than 6.
* [hero5 ORDER, 3 facts] Tom Brown was kept out of Brad Gerstner's section because the must-not-link rule forbids Tom Brown with Greg Brockman: Tom Brown is itself one end of that rule, and Greg Brockman was already seated with Brad Gerstner via Greg Brockman-Brad Gerstner (score 750). Those links were settled first (scores 750 against this pair's 750; equal scores go by id order).
* [hero3 ORDER, 3 facts] Dario Amodei was kept out of Sanjay Mehrotra's section because the must-not-link rule forbids Dario Amodei with Greg Brockman: Dario Amodei is itself one end of that rule, and Greg Brockman was already seated with Sanjay Mehrotra via Greg Brockman-Sanjay Mehrotra (score 800). Those links were settled first (scores 800 against this pair's 800; equal scores go by id order).
* [syn9100 MNL, 3 facts] record 544 was kept out of record 578's section because the must-not-link rule forbids record 544 with record 116: record 544 is itself one end of that rule, and record 116 was already seated with record 578 via record 116-record 578 (score 700). Those links were settled first (scores 700 against this pair's 700; equal scores go by id order).
* [syn9100 MERGE, 2 facts] record 1299 sits with record 1712 because each link in the chain was accepted and merged in priority order: record 281-record 1299 (score 850), record 281-record 1712 (score 1000).
* [syn9101 CAP, 6 facts] record 1337 was kept out of record 1700's section because the size limit of 5 would be exceeded: 2 records already with record 1337 plus 4 already with record 1700 is more than 5.
* [syn9102 ORDER, 3 facts] record 887 was kept out of record 1220's section because the must-not-link rule forbids record 887 with record 764: record 887 is itself one end of that rule, and record 764 was already seated with record 1220 via record 764-record 1220 (score 850). Those links were settled first (scores 850 against this pair's 700; equal scores go by id order).
