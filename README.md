# Eliminative-evidence experiment — data

Raw data for the fault-localization experiment: an editor model is shown an issue, a list
of candidate function signatures, and one of several *evidence blocks*, then commits to a
single function on a `FAULT:` line. The committed function is scored against the gold
function derived from the reference patch.

This repository is **data only** — no analysis code, no results, no manuscript. It is
deliberately shipped without a verification script so that anyone checking these numbers
derives them independently, using their own parsing and scoring decisions.

## Layout

```
cohort/
  paper_cohort.csv         848 rows = 106 instances x 2 original editors x 4 arms.
                           Carries model response text, gold keys, repo, stratum, tokens,
                           and the outcome columns produced by the analysis pipeline.
  cohort_68.csv            the byte-exact tier as a flat table.

raw_runs/
  tier_byte_exact_68/      five additional editors, 68-instance tier (2,108 JSON cells)
  tier_reconstructed_38/   the same editors, 38-instance tier (1,140 JSON cells)
      <model>/<arm>/<instance>.json
      each cell holds the full model response, the extracted commitment, token counts,
      latency, finish reason, and a key fingerprint.

ledgers/
  localizer_records/       106 markdown records of the localizer's deliberation, one per
                           instance: candidate-by-candidate verdicts and causal reasons.

prompts/
  stored_68/               the exact prompt text served, per instance and arm (68 tier)
  reconstructed_38/        regenerated prompts for the 38 tier
  template.py              prompt template and the forged-rejection line
  make_new_arms.py         how the audit and naturalistic arms were derived
```

`upstream_exports/` holds the original per-batch exports that `cohort/paper_cohort.csv`
was assembled from. They overlap and are partially redundant; they are included so the
cohort file's own provenance can be checked rather than taken on trust.

## Conditions (arms)

| Arm | Evidence block |
|---|---|
| `POS` | positive localization note only |
| `NEG_true` | + the localizer's genuine rejections and reasons |
| `NEG_false` | + one **forged** rejection of the gold function |
| `NEG_shuf` | + rejections drawn from a *different* instance (length-matched control) |
| `NEG_false_audit` | `NEG_false` + one instruction to verify ruled-out entries |
| `NEG_false_natural` | forged rejection phrased naturally, without the fixed template |
| `NEG_false_natural_v1` | an earlier version of the naturalistic arm, superseded |

## Design facts you may need

- The two tiers are disjoint; their union is the 106-instance cohort.
- Each instance was run under every arm, so all contrasts are paired.
- `runs/_quarantine/` from the source tree is **not** included here.
- `key_suffix` in each JSON cell is a six-character fragment identifying which API key
  served the call. It is a provenance marker, not a credential.
- Some responses hit the output cap without ever committing to a function.

## If you are verifying this data

Decisions that materially affect the result — how to extract a commitment from a response,
how to normalize a function name before comparing it against gold, which column to treat
as authoritative, which cells to exclude, and how to handle repeated or ambiguous records
— are **left to you deliberately**. Please make and state your own, rather than inferring
them from the artifact's structure.

Two things worth doing explicitly:

1. Derive outcomes from the model's raw response text and compare against the outcome
   columns already present, rather than taking those columns as given.
2. Read the paper's stated matching and exclusion rules, then check by hand whether the
   recorded outcomes actually follow them on a sample of records you pick yourself.

Disagreements of any size are worth reporting, including ones that favour the paper's
claims.
