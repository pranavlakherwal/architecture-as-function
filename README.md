# Architecture as a function: A*

A* derives an AI system from the job it has to do. The architecture is the intelligence. The model is one input, and a swappable one.

Public since June 2026. Rewritten 3 November 2026: the status below is current, one June result is marked retracted, and the research notes carry no client names.

## The function

In practice we write the function with six inputs:

```
architecture = f(purpose, knowledge, pipeline, people, models, constraints)
```

The research form in this repository is the same function with its inputs typed:

```
A*(I, L, K, T) -> (A, D)
```

I is what the system observes, L is what it can change, K is what it knows (seven bootstrap classes and four operators, depth three), T is the work decomposed. A is what it does. D is how it decides, and D reduces to S(M,T), the routing score, which lives in [smt-router](https://github.com/pranavlakherwal/smt-router). Purpose and people sit in I and T; models and constraints sit in L and K.

The specification is `A_STAR_v0_2.md` (frozen 22 May 2026), built on `A_STAR_v0.md` and the interim note `A_STAR_v0_1_1.md`. Read v0.2 first.

## Status, November 2026

- **Spec:** version 0.2, frozen. The next close, version 0.3, waits on the measurements below.
- **Empirical phase:** directional. Four of five stopping rules pass. Nothing here is called validated.
- **The storage law** (how much a system should keep): beta = +0.209, R squared 0.871. It held under jackknife and bootstrap on 11 June 2026. Caveat: the full-data fit at n = 10 reads 0.152 with R squared 0.58.
- **The modification law** (how the cost of a change grows with the number of client systems): the June headline, alpha = +8438 with R squared 0.617, is **retracted as a headline**. Re-read on 2 October 2026, the regressor was the length of the commit list the miner had been allowed to read, so the fit was a sampling identity. Against a recounted throughput the R squared is 0.018. The functional form (square root, linear or quadratic) is undetermined by the data. We demoted it ourselves; that is the standard here.
- **What stands:** the function, the seven K classes and four operators, and the three information conditions. Also the twelve primitive operations, the Z3 solver, the manifest schema with its validator, and the seven-axis measurement tool. And 88 labelled rows with Cohen's kappa 0.881.

The running record is `ROADMAP.md`.

## How it is deployed

Three systems run on the function today. They are described, not named; our client work is confidential by default.

**A deal desk for an M&A advisory.** Purpose: buyers for each live mandate, and fewer evenings on lookup. Knowledge: the desk's own records and what each buyer said last time. Pipeline: find, verify, score, brief. People: the advisor, every morning, with the evidence beside each name. Models: routed by S(M,T), a cheap one for extraction and a strong one for judgement. Constraints: evidence attached before a name is shown, geography screened first, an unmeasured number reported as unknown. Measured on our system, with dates. Companies visible went from 8,938 to 37,116 between 24 June and 22 August 2026, while the paid database stayed at 3,595. One run on 31 May 2026 found 179 deals, and 94 percent of them were absent from the paid export. 22 of 25 valuation databooks were certified on 10 June 2026.

**A clinical answer layer for a diagnostics chain.** Purpose: answer a clinician's question with evidence. Knowledge: the patient's record and the literature the provider trusts. Pipeline: retrieve, draft, verify, cite. People: the clinician signs off, every time. Models: open weight, swappable. Constraints: fail closed, and the data stays inside the provider's walls. Measured: 330 test cases run before a model sees a patient, as of October 2026.

**A publication.** Purpose: a longevity article that clears a clinical-grade bar. Knowledge: sources verified against the live web. Pipeline: draft, then four gates in sequence, each defaulting to block. People: an editor reads what passed. Models: any model may draft. Constraints: a citation that does not match its source blocks the piece. Measured: 48 articles and the first paid guides sold, October 2026.

## How deployment feeds the research

Every deployment is a measurement. The storage law came from counting what two systems kept and what they threw away. The retraction above came from a deployment's own commit history, read again with a real import resolver. The cross-cutting counts that bound the two-layer split (engine and client, version 0.2 section 4) were taken on live systems. The research moves when a system in production disagrees with the spec, and the spec is corrected in the open.

## How to build on it

1. Write your system as the function. Fill all six inputs in one page before you build. If an input is empty, the system is not derived yet.
2. Type the knowledge. Pick the bootstrap class, then derive with the four operators (`A_STAR_v0_2.md`, section 2). Depth three is the cap.
3. Declare the manifest. `impl/a_star/manifest` holds the schema and the validator for the two information conditions it checks.
4. Measure before you optimise. `impl/a_star/measurement` reads the seven axes from a repository without changing it.
5. Let the solver propose. `impl/a_star/solver` runs Z3 Optimize over a declared system and emits primitive operations, never actions.
6. Run the tests: `python3 -m pytest impl -q`.
7. Open an issue with your derivation. A derivation that disagrees with the spec is the most useful thing you can send.

Papers the framework rests on are in `BIBLIOGRAPHY.md`, with what each gave and what we changed.

## What is in this repository

```
A_STAR_v0.md          the v0 specification, 21 May 2026
A_STAR_v0_1_1.md      the interim note from the first application
A_STAR_v0_2.md        the frozen specification, 22 May 2026: read this first
BIBLIOGRAPHY.md       the papers, with what each gave
ROADMAP.md            status and the open questions, with every correction dated
impl/a_star/          profiles, manifest schema and validator, measurement, solver, tests
impl/examples/        one derived plan, client terms removed
impl/tests/           tests for the tools
protocols/            the launch records of the four research waves
research/             the research notes per wave, client names removed
thinking/             the first-principles notes behind the spec
```

## Citing and provenance

Cite as: Lakherwal, P. (2026). Architecture as a function: A*, version 0.2. github.com/pranavlakherwal/architecture-as-function.

The specification's hash is registered on the Bitcoin blockchain through OpenTimestamps, the way the S(M,T) router paper was: the record of 3 November 2026 sits in block 974395, the specification's own proof in blocks 974395, 974423 and 974430, and the signed tag `provenance-2026-11-03` marks the commit. The record, the proofs and the verification steps are in `registration/REGISTRATION.md`.

## License

See `LICENSE`.

## Changelog

- 3 November 2026: README rewritten to the current status. The June modification-law headline marked retracted. Client names removed from the research notes and the example plan. Lint and test workflow added.
- 11 June 2026: the storage law held under jackknife and bootstrap; roadmap updated.
- 1 June 2026: first public release.
