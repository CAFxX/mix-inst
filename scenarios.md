# Input scenario catalog for `mix` evaluation

`mix rd, rs1(val), rs2(key)` is a keyed hash-map finalizer. `key` is a
per-map seed fixed for the map's lifetime; `val` is the incoming key
material (often an integer key or a weak upstream hash). The output is
reduced by one of: Lemire `(out*X)>>64`, mask `out & (2^m-1)`, `out % y`.

Finite testing cannot cover everything, so the battery is organized around
*why* a scenario matters: common real cases plus adversarial cases aimed at
known weak-mixer failure modes. Every finalist must pass all of these.

## A. Input families (fixed key, sequence I, I+j, ...)

| id | I | j | Rationale |
|---|---|---|---|
| SEQ | 0 | 1 | Canonical: ordered integer keys, counters. |
| STRIDE-ODD | 0 | 3 | Small odd stride. |
| STRIDE-FIB | 12345 | 0x9E3779B97F4A7C15 | Golden-ratio stride (Fibonacci hashing style). |
| STRIDE-POW2 | 0 | 2^k, k=0..63 | Aligned iteration; low k bits of input never change. |
| STRIDE-MPOW2 | 0 | c*2^k, c in {3,5,7,9}, k in {3,4,5,6} | Struct arrays: element size is a multiple of alignment. |
| PTR | arbitrary | 8 / 16 | **Aligned pointers as keys** — low 3-4 bits always zero. Very common. |
| PTR-RAND | low 3 bits zero, random rest | — | malloc-like pointer soup. |
| HIGH-ONLY | 0xFFFFFFFF00000000 | 2^32 | Only high bits vary (degenerate upstream hash). |
| SMALL-INT | 0 | 1, N small | Small integer keys; high bits constant zero. |
| DESC | 0 | 2^64-1 / 2^64-8 | Descending sequences (negative strides). |
| SINGLE-BIT | — | — | val = 1<<k, k=0..63 (Hamming weight 1; enums/flags). |
| GRAY | — | — | val = i ^ (i>>1) (consecutive values, 1-bit steps). |
| UPSTREAM | — | — | val = splitmix64(i): already-mixed input (sanity, should be easy). |
| BYTE-REP | — | — | val = i * 0x0101010101010101 (byte-repeated counter). |
| SPARSE-HD | — | — | input pairs at Hamming distance 1 (avalanche spot check). |

## B. Key families (fixed input sequence)

0, all-ones, 0xAAAAAAAAAAAAAAAA / 0x5555555555555555, golden-ratio constant,
small keys (1, 0x1234), 0xDEADBEEFDEADBEEF, 0x8000000000000000, plus >= 32
pseudorandom keys. Key schedule gets no related-key requirement, but every
key must independently pass family A.

## C. Key sweep (fixed input, many keys)

Fixed SEQ inputs hashed under 256 consecutive/random keys: outputs must look
independent across keys (per-bit monobit over the key axis). Models "many
hash maps, same key type".

## D. Reductions (applied to every A/B scenario)

- Lemire X in {2,3,5,7,10,16,100,1000,2^16,2^32,2^64-1}, exact nulls.
- Mask m in {1,2,4,8,12,16,20,24,32,48,64}.
- Mod y in {3,7,10,100,1000} (exact preimage nulls).

## E. Small-N

N=1024 chi-square on 8-bit projection for SEQ and PTR: real hash maps often
hold tens of entries, not 2^18.

## F. Adversarial (targeted at observed failure modes)

- Keys/strides that maximized deviation in weaker candidates (regression).
- Per-bit monobit on raw output for every (scenario, key): catches
  single-bit biases (the 10-round SPN failure mode; also present in
  SplitMix64) that pooled tests dilute.
- Fixed-bit check for the linear layer: no output bit may be a wire-through
  of an input bit (the 8-round PRESENT pLayer/MSB suspicion).

## Deliberately out of scope

- Related-key / differential cryptanalysis beyond the statistical screen
  (not required: `key` is a trusted per-map seed, and the schedule is
  intentionally non-related-key-resistant).
- Proving anything for *all* keys/strides/N: finite tests are evidence,
  not proof. The report states this.
