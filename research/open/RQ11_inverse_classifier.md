# RQ11 — Can we infer K from folder contents?

## Question

Today the user declares K when invoking the solver (`--k outbound-pipeline`). Can we invert this: given a folder, infer the most likely K from its observable facts (file types, names, git history, presence of PII/secret/derived hints)?

## Why it matters

- Lets A* bootstrap on legacy repos with zero human labels.
- Validates the K taxonomy (RQ9): if the 7 classes are real, an inference model should recover them.
- Enables drift detection: if a folder's inferred K drifts from its declared K over time, the manifest is becoming a lie.

## Sub-questions

- Q11.1: Features? File-extension histograms, depth, fan-out, secret/PII hit-rate, commit cadence.
- Q11.2: Model? Simple decision tree, embedding similarity to the 7 prototypes, or LLM-as-classifier?
- Q11.3: Validation: hand-label the 8 known Neural repos, measure recall.

## Not yet answered

Skeletal placeholder.
