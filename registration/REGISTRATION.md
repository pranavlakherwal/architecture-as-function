# Registration of the A* research on the Bitcoin blockchain

OpenTimestamps proofs tie the SHA256 hash of a document to a Bitcoin block, so anyone can check the document existed by that block's date. No third party is trusted. Only hashes are published here.

| Record | What it covers | Proof | Bitcoin block |
|---|---|---|---|
| 13 July 2026, GPG-signed tag `provenance-2026-07-13` on this repository (then private), commit aa1a66c | the A* files as they stood that day | the signed tag, and the signer's record in P0P's own files | the day's record is anchored at block 957846 |
| `PROVENANCE_2026-11-03.txt` | the six files as they stood on 3 November 2026, before the change of 5 November described below | `PROVENANCE_2026-11-03.txt.ots` | 974395 |
| `A_STAR_v0_2.md` as it stood on 3 November 2026 | the frozen specification, earlier bytes | `A_STAR_v0_2.md.2026-11-03.ots` | 974395, 974423, 974430 |
| `PROVENANCE_2026-11-05.txt` | the six files as published now, at commit 83c0758 (tag v0.2.2) | `PROVENANCE_2026-11-05.txt.ots` | pending on 5 November 2026; upgraded once the calendar's Bitcoin transaction confirms |
| `A_STAR_v0_2.md` as published now | the frozen specification, current bytes | `A_STAR_v0_2.md.ots` | pending, as above |

## What changed on 5 November 2026

One private label was replaced by a neutral one. The internal name of a deployment's repository appeared in one table row of `A_STAR_v0.md`, one table row of `A_STAR_v0_2.md`, and in research notes. Our client work is confidential by default. So the label was replaced, and the history of this repository was rewritten to remove it. Nothing else in the specifications changed.

What this means for the proofs:

- The proofs of 3 November attest the earlier bytes. Those bytes are not published. P0P holds them, with the commit and the signed tag the 3 November record names, and can show them under confidentiality.
- The hashes in `PROVENANCE_2026-11-03.txt` therefore differ from the files here for `A_STAR_v0.md`, `A_STAR_v0_2.md` and `README.md`.
- The record of 5 November lists the hashes of the files as published now and carries its own proof.
- The priority date of the content is the earlier one. The 5 November record lets anyone check the current files.

Commit hashes: a rewrite changes every commit hash. The 3 November record names commit b4a4f0d. The same content, with the label replaced, is now commit f715402, and tag `v0.2.1` points there.

Signed tag: `provenance-2026-11-03` was signed with GPG key E3A76EA3104DCD86 (Pranav Lakherwal) on 4 November 2026 and pointed at the earlier commit. It left this repository with that commit; the signed original is in P0P's files. A new signed tag on `v0.2.2` is to follow.

## How to check, without installing anything

1. Open https://opentimestamps.org.
2. Drag the proof file (the .ots) and the document into the page.
3. The page names the Bitcoin block that attests the document, and its date.

## How to check from a terminal

```
pip install opentimestamps-client
ots upgrade registration/PROVENANCE_2026-11-05.txt.ots
ots info registration/PROVENANCE_2026-11-05.txt.ots      # the block height appears once upgraded
shasum -a 256 A_STAR_v0_2.md                            # must equal the hash in the 5 November record
```

**Attested 4 November 2026 (IST).** The 3 November record's proof sits in Bitcoin block 974395; the earlier specification's proof in blocks 974395, 974423 and 974430. `ots info` on `PROVENANCE_2026-11-03.txt.ots` or `A_STAR_v0_2.md.2026-11-03.ots` prints the block.

Registered by P0P (PnotP), Pranav Lakherwal. Method: OpenTimestamps and a GPG-signed git tag, first used on 13 July 2026.
