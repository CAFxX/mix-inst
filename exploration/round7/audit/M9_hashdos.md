# M9: multi-key hash-DoS chaining analysis — r7_feist8_s1_1sbox (2026-10-02)

Threat model: `mix(val,key)` is a hash-table finalizer. Attacker may control
`val`, observe outputs, and in some deployments influence/learn `key`.

Structural facts used throughout:
- For fixed key, the cipher is a **permutation** of 2^64 (Feistel round is
  bijective for any F; whitening is bijective). Exact collisions are
  *impossible*, not merely hard. Verified: 0 collisions on 2^24 sequential
  inputs × 3 keys, 0 on 4M sequential (audit), bijective by construction.
- F (sans key xor) is itself bijective: S1 is a permutation, lin32 is a
  permutation. The round-key xor does not affect differential/linear
  properties of F.
- F consumes only the **low 32 bits** of each 64-bit round key; high 32 bits
  of rk_i are dead. (Design note, not a vulnerability per se.)
- Key schedule is affine: rk_i(k^δ)^rk_i(k) = rotl64(δ,13(i+1)) (key-independent).

## 1. Single-key collision resistance (measured)

Method: C program, N=2^24 sequential vals, sort-based exact collision count,
3 keys. Birthday expectation ≈ N²/2^65 ≈ 2^-17.

| key | collisions |
|---|---|
| 0x0000000000000000 | 0 |
| 0x123456789ABCDEF0 | 0 |
| 0x9E3779B97F4A7C15 | 0 |

Verdict: as expected for a permutation. No finding. (A hash-DoS attacker
cannot manufacture exact 64-bit collisions for a fixed key by *any* method —
they do not exist. Bucket collisions mod nbuckets are governed by the secret
key; see §5.)

## 2. Weak keys (measured + structural)

Method: solved the affine constraints low32(rk_i)=0 per round (each constrains
a 32-bit window of the 64-bit key); intersected pairs/triples.

- Single round zeroable: yes (2^32 keys per round).
- **Worst key found: `k=a1fa53e0a803eefb` zeroes low32(rk) in rounds 5 AND 7**
  simultaneously (58 constrained bits → 64 such keys). No third round can join
  (all triples inconsistent). So at most 2 of 8 F-instances are key-independent.
- No key makes any low32(rk_i) repeat across rounds in a slide-useful way;
  explicit slide-pair search (rk_i(k1)=rk_{i+1}(k2) ∀i) is inconsistent —
  **no slide pairs exist**.
- Every one of the 64 key bits reaches the low32 of ≥1 round key (no dead bits).

Empirical: full S2-style differential profiler on the weak key
(N=2^20, 74 deltas): **PASS** — max_repeats=0, max|z|=4.0.
Fixed-point/2-cycle scan (2M random vals): 0 for weak key and key=0.

Note: because the round key enters F only as a final xor, zeroing it does not
change F's differential profile at all — the "weakness" is only that 2/8
rounds are key-independent, and the cipher remains a keyed permutation via
whitening + the other 6 rounds. Rating: INFO.

## 3. Related keys (measured)

Method: for key pairs (k, k^δ), N=2^20 random vals, d = mix(v,k)^mix(v,k^δ);
count zero-d, full-64-bit repeats of d, max per-bit |z|.

| δ | zero_d | repeat d values | max|z| |
|---|---|---|---|
| 0x0000000000000001 | 0 | 0 | 1.97 |
| 0x8000000000000000 | 0 | 0 | 2.84 |
| 0x9E3779B97F4A7C15 (schedule constant) | 0 | 0 | 2.27 |

All consistent with random. Additionally proven: no nonzero δ avoids all
eight F key-inputs (union of low32 windows covers all 64 bit positions), so
every related-key pair perturbs at least one round function. Rating: INFO
(no structure found).

## 4. Chaining / multi-key observations (analysis)

Question: do observations under k1,k2 help attack k3?

- The only secret is the 64-bit key k; S-box, linear layer, schedule structure
  are public. Round keys are an affine (rotated) function of k, so observations
  under k1 constrain k1 only — rk_i(k3) is computationally unrelated to
  rk_i(k1) for independent k3 (rotation by 13(i+1) bits is a strong
  decorrelator; related-key tests in §3 show no exploitable relation).
- A known-key attacker gets a chosen-input oracle on the 8-round Feistel
  (whitening is invertible given k), but 8 rounds with a bijective,
  differentially-strong F (max 2^-2/S-box, fast diffusion — see §5) is not
  practically breakable; no key-recovery shortcut was found.
- Cross-key collision transfer is impossible: collisions under k1 are not
  collisions under k2 (different permutations), and universal collisions
  cannot exist (§1).
- Slide attacks: ruled out structurally (no slide pairs, §2).

Rating: INFO. No practical transfer demonstrated or plausibly constructed.

## 5. Hash-DoS practicality / differential bounds (measured + estimated)

S1 S-box (exact): max DDT entry 4/16 = **2^-2** per active S-box; max linear
correlation 1/2.

Measured 1-round F differential (120 single-nibble input diffs × 2^24 samples)
and best 2-round Feistel trail ([trail.log](m9/trail.log)):

## CORRECTION (2026-10-02, independent cryptanalysis peer review)

The differential bounds below are WRONG and superseded. The peer reviewer found:
- The true best 2-round Feistel trail is **2^-2**, not 2^-9.99 — via the Feistel
  skip pattern: input difference (a,0) activates ZERO S-boxes in round 1 (the
  difference passes through the untouched half). The "measured 2^-9.99" only
  covered trails that activate F in both rounds.
- Independent beam search (width 4000 and 8000, stable): best 8-round trail =
  **2^-61, 25 active S-boxes** — not the extrapolated 2^-58.
- Margin: 2^-61 is 8x above the 2^-64 ideal. Adequate for a mixer (2^61 queries
  utterly impractical; differentials give a hash-DoS attacker nothing beyond
  direct computation), not cipher-grade generous.
- Related-key differential **2^-37** beats single-key 2^-61 (affine key
  schedule: rk(k^d,i) = rk(k,i)^rotl64(d,13(i+1))). Certificational weakness;
  NOT in the fixed-key hash-DoS threat model; recorded, not a blocker.
- The structural conclusions below (permutation => no exact collisions,
  no weak/related-key *practical* structure, no slide pairs) still hold.
  Only the quantitative trail bounds are corrected.
- Full detail: [exploration/round7/audit/REVIEWS_SUMMARY.md](REVIEWS_SUMMARY.md) (MAJOR-1..3).

---

- 1-round F: best din=0x05000000 → dout=0x02000041, p ≈ **2^-2.00**
  (single active S-box; matches S-box DDT maximum exactly)
- 2nd-round F on the spread diff 0x02000041: best p ≈ **2^-7.99**
  (~4 active S-boxes after the linear layer spreads the nibble)
- Best measured 2-round Feistel trail: p ≈ **2^-9.99**

Extrapolation (honest, attacker-optimistic): after the first F call,
diffusion saturates at ~4+ active S-boxes per F (≈2^-8 per round). An
idealized 8-round trail chaining the best differential at every step gives
≈ 2^-2 × (2^-8)^7 ≈ **2^-58** — i.e. ~64× above the 2^-64 ideal, but still
2^58 work, utterly infeasible. Moreover this is not a collision trail
(zero output difference); exact collisions cannot exist (§1). A differential
does not help bucket-flooding without the key.

Reasoning for the attacker: exact collisions do not exist (permutation), so
hash-DoS must work via (a) key recovery (2^64 brute force; no shortcut found),
or (b) a distinguisher predicting bucket assignment without the key. The
measured trail bounds show (b) requires ≈2^58 work even under optimistic
chaining assumptions — not a practical attack.

Honest statement: full 8-round trail search was not performed (infeasible
exhaustively); the bound is an extrapolation from measured 1–2 round
differentials plus the per-S-box maximum. No trail with probability
meaningfully above 2^-64 was found or is plausibly constructible.

## Findings

- INFO-1: F uses only low32 of each 64-bit round key; high 32 bits are dead.
  Not exploitable (verified: every key bit still reaches ≥1 F), but wastes
  key-schedule entropy. Considered harmless; noted for the design record.
- INFO-2: worst weak key zeroes 2/8 F key-inputs; no measurable weakness
  (S2-style profiler passes, no fixed points). Not a vulnerability.
- No BLOCKER, no MAJOR, no MINOR findings.

## Verdict: SAFE

No hash-DoS-relevant weakness found: no collisions exist by construction,
no weak/related-key structure measured, no slide pairs, no cross-key
transfer, differential bounds comfortable. The attacker's realistic cost
remains ≈2^64 (key recovery) for a fixed unknown key, and bucket-flooding
without the key is infeasible.
