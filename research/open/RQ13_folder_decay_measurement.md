# RQ13 — What is the folder decay rate?

## Question

A_STAR_v0 §Honest-Limits flags "folder decay rate unknown". c_drift in `core_vector.py` ships with a low-confidence proxy. We need the real number.

## Approach

- Source: git history across the 8 Neural seed repos.
- Signal: per-folder commit cadence, file-add/delete ratio, rename rate, manifest staleness vs content age.
- Output: a decay coefficient λ_K per K class. Feeds c_drift normalization in `AXIS_SPECS`.

## Sub-questions

- Q13.1: Is decay K-dependent (outbound vs research-memory differ) or universal?
- Q13.2: Half-life form: exponential, power-law, step-function-at-archival?
- Q13.3: Does the manifest schema need a `last_reviewed_at` field for cadence enforcement?

## Stakes

Unblocks c_drift confidence promotion from "low" to "measured".

## Not yet answered

Skeletal placeholder.
