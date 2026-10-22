# Benchmark: v1-original vs v2-lean

| Task | v1-original | v2-lean | Cost | Tokens | Time | Routing (v1-original → v2-lean) |
|---|---|---|---|---|---|---|
| find | pass | pass | $0.305 → $0.2407 | 128,025 → 105,179 | 15s → 16s | main thread → main thread |
| one-line-fix | pass | pass | $0.35 → $0.2791 | 220,504 → 178,152 | 27s → 18s | main thread → main thread |
| multi-file-feature | pass | pass | $0.3771 → $0.3393 | 226,045 → 268,126 | 25s → 48s | main thread → main thread |
| unclear-bug | pass | pass | $0.3405 → $0.3023 | 178,102 → 220,513 | 33s → 27s | main thread → main thread |
| docs | pass | pass | $0.3667 → $0.3139 | 263,299 → 259,980 | 23s → 42s | main thread → main thread |
| review | pass | pass | $0.3466 → $0.2817 | 216,542 → 178,517 | 17s → 18s | main thread → main thread |
| cli-flag | pass | pass | $0.3574 → $0.2805 | 222,274 → 146,365 | 19s → 17s | main thread → main thread |
| run-tests | pass | pass | $0.3432 → $0.276 | 215,422 → 177,544 | 16s → 17s | main thread → main thread |
| git-commit | pass | pass | $0.3098 → $0.2444 | 130,965 → 106,021 | 24s → 18s | main thread → main thread |
| new-project | pass | pass | $0.3177 → $0.2635 | 87,828 → 107,709 | 21s → 19s | main thread → /new-project |

**Passed:** 10 → 10  
**Total cost:** $3.41 → $2.82  
**Total tokens:** 1,889,006 → 1,748,106
