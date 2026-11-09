# Architecture as a function: A*

Run one command on a repository and read seven numbers, each ranked against repositories we have measured, with the three fixes to make first.

```
git clone https://github.com/pranavlakherwal/architecture-as-function
cd architecture-as-function
PYTHONPATH=impl python3 -m a_star measure /path/to/your/repo
PYTHONPATH=impl python3 -m a_star measure /path/to/your/repo --json
```

The first line prints the plain report, the second the same content as JSON. From inside `impl/` the prefix drops: `python3 -m a_star measure PATH`. Python 3.9 or later, standard library only, nothing to install.

Here is what we got on [smt-router](https://github.com/pranavlakherwal/smt-router), our public routing repository, on 7 November 2026:

```
A* measure: /Users/pranavlakherwal/Core/Neural/PnotP/smt-router
Read 7 November 2026, against 58 repos measured 7 November 2026. Lower is better on every line.

How deep a reader digs to find a file             1.131 weighted folder levels  higher than 6 of 58 measured repos  fine
How often a changed file changes again in a year  2.025 touches per file        higher than 48 of 58 measured repos  act
How much the repository stores                    2,458,418 bytes (2.3 MB)      higher than 19 of 58 measured repos  fine
What the system costs to run each month           0 USD per month               higher than 0 of 58 measured repos  fine
How many kinds of file the repository mixes       0.757 of 1                    higher than 43 of 58 measured repos  fine
How many links inside the docs point nowhere      0.000 of 1                    higher than 0 of 58 measured repos  fine
How much of what is tracked is a build output     0.000 of 1                    higher than 0 of 58 measured repos  fine

Top three fixes (1 reading sits above three quarters of the measured repos; the rest are the next by rank)
1. Split the files that take most of the changes.
   The 5 most touched files take 28 of 160 touches (18%): README.md (7), CHANGELOG.md (6), paper/main.pdf (6), paper/main.tex (5), router/config.py (4). Split the ones that change for more than one reason.
2. Cut the odd file types.
   13 file types across 69 files. The rarest: .bak (1, e.g. registration/SMT_Router_Paper_v1.4.pdf.ots.bak), .bib (1, e.g. paper/bibliography.bib), .example (1, e.g. .env.example), .lock (1, e.g. uv.lock), .yml (1, e.g. .github/workflows/ci.yml). Each odd type is a tool a new reader has to learn; drop or consolidate the ones nobody runs.
3. Move the largest files out.
   The 5 largest files hold 1.6 MB of 2.3 MB (69%): uv.lock (784.4 KB), SMT_Router_Paper_v1.5.pdf (249.5 KB), paper/main.pdf (249.5 KB), SMT_Router_Paper_v1.4.pdf (239.5 KB), SMT_Scoring_AI_Endpoints.pdf (125.4 KB). Move the ones that are outputs, not sources, out of the repository.
```

The command took 0.17 seconds on that run, measured with `time` on 7 November 2026.

## What the seven readings are

Each reading is a cost, so lower is better. "Act" means the repository is higher than at least three quarters of the 58 repositories we measured on 7 November 2026. Those sit in `impl/a_star/measurement/fleet_reference.json` as numbers only.

1. **How deep a reader digs to find a file.** Mean folder depth, times a penalty we add when sibling files share their first four letters. Unit: weighted folder levels.
2. **How often a changed file changes again in a year.** Commits in the last 365 days, divided by the files they touched. Unit: touches per file.
3. **How much the repository stores.** Bytes on disk. We skip `.git`, `node_modules` and build folders. Unit: bytes.
4. **What the system costs to run each month.** You supply it with the --monthly-usd flag. Without it the reading is 0 and we call it a stand-in. Unit: USD per month.
5. **How many kinds of file the repository mixes.** The spread of file extensions, as a share of the most mixed it could be. Unit: 0 to 1.
6. **How many links inside the docs point nowhere.** Relative links in markdown files that we could not resolve to a file. Unit: share of links, 0 to 1.
7. **How much of what is tracked is a build output.** Tracked files under `build`, `dist`, `generated` or cache folders. A stand-in until we have a lineage graph. Unit: share of tracked files, 0 to 1.

Each fix is built from the reading's own internals. Depth names the deep paths and the look-alike files. Change names the most touched files. Storage names the largest files. Links names the ones that point nowhere. Mix names the odd file types. The two stand-ins (money, build outputs) say so and get no invented fix.

The fleet reference is 58 repositories measured on 7 November 2026, numbers only: one sorted list per reading, the count and the date. No path and no name leaves the machine that builds it. `impl/a_star/measurement/build_fleet_reference.py` rebuilds it from any folder of repositories you point it at.

## Work with us

The first three readings we do with a team are free, in return for permission to quote the before and after.

## The function

A* derives an AI system from the job it has to do. The architecture is the intelligence. The model is one input, and a swappable one.

Public since June 2026. Rewritten 3 November 2026: the status below is current, one June result is marked retracted, and the research notes carry no client names.

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
4. Measure before you optimise. `PYTHONPATH=impl python3 -m a_star measure .` reads the seven readings from a repository without changing it, and names the three fixes.
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
impl/a_star/          the measure command, profiles, manifest schema and validator, solver, tests
impl/examples/        one derived plan, client terms removed
impl/tests/           tests for the tools
protocols/            the launch records of the four research waves
research/             the research notes per wave, client names removed
thinking/             the first-principles notes behind the spec
```

## Citing and provenance

Cite as: Lakherwal, P. (2026). Architecture as a function: A*, version 0.2. github.com/pranavlakherwal/architecture-as-function.

The specification's hash is registered on the Bitcoin blockchain through OpenTimestamps, the way the S(M,T) router paper was. The record of 3 November 2026 sits in block 974395 and attests the files as they stood that day. On 5 November 2026 one private label was replaced by a neutral one, and a new record was made for the files as published now; its proof sits in block 974600. Both records, the proofs and the verification steps are in `registration/REGISTRATION.md`.

## License

See `LICENSE`.

## Changelog

- 7 November 2026: `python -m a_star measure PATH` added. Seven readings ranked against 58 repositories, with the three fixes to make first. README opens with the command.
- 3 November 2026: README rewritten to the current status. The June modification-law headline marked retracted. Client names removed from the research notes and the example plan. Lint and test workflow added.
- 11 June 2026: the storage law held under jackknife and bootstrap; roadmap updated.
- 1 June 2026: first public release.
