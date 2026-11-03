# Registration of the A* research on the Bitcoin blockchain

OpenTimestamps proofs tie the SHA256 hash of a document to a Bitcoin block, so anyone can check the document existed by that block's date. No third party is trusted. Only hashes are published here.

| Record | What it covers | Proof | Bitcoin block |
|---|---|---|---|
| 13 July 2026, GPG-signed tag `provenance-2026-07-13` on this repository (then private), commit aa1a66c | the A* files as they stood that day | the signed tag, and the signer's record in P0P's own files | the day's record is anchored at block 957846 |
| `PROVENANCE_2026-11-03.txt` | the six files listed inside it, at commit b4a4f0d (tag v0.2.1): the three specifications, the bibliography, the README and the roadmap | `PROVENANCE_2026-11-03.txt.ots` | pending on 3 November 2026; upgraded once the calendar's Bitcoin transaction confirms |
| `A_STAR_v0_2.md` on its own | the frozen specification | `A_STAR_v0_2.md.ots` | pending, as above |

## How to check, without installing anything

1. Open https://opentimestamps.org.
2. Drag the proof file (the .ots) and the document into the page.
3. The page names the Bitcoin block that attests the document, and its date.

## How to check from a terminal

```
pip install opentimestamps-client
ots upgrade registration/PROVENANCE_2026-11-03.txt.ots
ots info registration/PROVENANCE_2026-11-03.txt.ots      # the block height appears once upgraded
shasum -a 256 A_STAR_v0_2.md                            # must equal the hash in the record
```

Registered by P0P (PnotP), Pranav Lakherwal. Method: OpenTimestamps and a GPG-signed git tag, first used on 13 July 2026.
