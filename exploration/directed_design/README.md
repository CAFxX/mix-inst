# Directed Design Track — New Combinations/Constructions

**Started:** 2026-10-07
**Directive:** "continue designing/testing/tweaking new combinations/constructions/configurations until I say otherwise"

## Design Axes

1. **Linear layers**: rotation pairs, 3-rotation variants, per-round varying, non-circulant
2. **P-boxes**: affine parameters beyond (19,1), non-affine permutations
3. **S-box arrangements**: heterogeneous rounds, per-round S-boxes
4. **Key schedules**: rotations, constants, mixing strategies
5. **Round structures**: 3r/5r/6r SPN, unbalanced, truncated variants
6. **F functions**: beyond current SPN F

## Method

- S0 (unit delay) first — fast kill if too slow
- S1 (statistical) — must be CAL_PASS
- S2 (differential) — must PASS
- S3/S4 for survivors; Q1 sac_z5=0 mandatory for frontier claims
- Record EVERYTHING including kills with exact signals
- Open-ended: do not narrow, do not stop. Dead end → try different approach.
- Never stop silently.

## Batches

### Batch 1 (2026-10-07): Linear layer exploration
- Rotation pairs from the branch≥4 set (1,431 pairs identified 2026-10-06)
- Focus on pairs with good S0 (small rotations = less delay)
- Per-round varying rotations

### Batch 2: P-box variants
### Batch 3: Heterogeneous S-box rounds
### Batch 4: Key schedule variants
### Batch 5: Round structure variants
