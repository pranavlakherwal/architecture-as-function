# A* Research Roadmap

Closed: Waves 1-3 (RQ1..RQ8). Synthesis at `/A_STAR_v0.md`.
v0.1 reference impl: `/impl/a_star/` (40/40 tests).
v0.1 consolidation: `/Core/Neural/neural-gtm/` (Layer A) + `/Core/Neural/AgencyA/` (Layer B). 111 → 71 primitives.

## Open questions

| ID | Question | Why it matters | Status |
|---|---|---|---|
| RQ9 | Is K a fixed taxonomy, an inheritance lattice, or a free constraint-bag? | Engine layer (`neural-gtm`) doesn't fit any of the 7 v0 classes. | open |
| RQ10 | Is the layer-seam (engine ⇄ tenant) a primitive of A*, or derivable from existing IC3 + the 9 ops? | Currently only enforced in QA, not in the synthesis. | open |
| RQ11 | Can the stub-manifest generator be inverted, i.e. infer `K` from a folder's contents instead of declaring it? | Would let A* bootstrap on legacy repos with zero human labels. | open |
| RQ12 | What is the *cost* of the seam? c_modify rises (two repos) but c_drift falls. Net? | Decides whether two-layer is the default or an optimization. | open |
| RQ13 | Folder decay rate (v0 honest-limit). Measure on Neural repos with git history. | Unblocks c_drift calibration. | open |

## Working files

- `open/RQ9_k_class_form.md` — placeholder, expand when picked up
- `open/RQ10_seam_as_primitive.md` — placeholder
- `open/RQ11_inverse_classifier.md` — placeholder
- `open/RQ12_seam_cost.md` — placeholder
- `open/RQ13_folder_decay_measurement.md` — placeholder

Move into `wave4/` when launched.

## Adjacent threads (not yet RQs)

- Stub-manifest generator: impl task, not research. Tracks under `/impl/a_star/` once specced.
- 8th K class vs lattice: subsumed by RQ9.
- FastSMT migration (v0 → v1 solver path): impl, parked.
