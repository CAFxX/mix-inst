# Round 4 — Design-Space Search Results

## Gates
- Delay bar: ≤44.3 absolute unit-delays (0.9× remeasured 64×64 multiplier ref 50.8)
- Bijective per fixed key (proven + spot-checked)
- Calibrated statistical screen: Fisher-combined p + Holm-Bonferroni α=0.01, zero rejections = CAL_PASS
- Hardware efficiency: area/power ≤1–2× multiplier

## Candidates

| name | family | structure | delay | ×mult | cells | gate | notes |
|------|--------|-----------|-------|-------|-------|------|-------|
<!-- to be filled from batch3 -->

## Delay-passers (≤44.3)
<!-- to be filled -->

## Statistically clean (CAL_PASS)
<!-- to be filled -->

## Pareto frontier
<!-- to be filled -->

## Family notes

### M family (sparse constant multiply + shifts) — REJECTED
xsm_c8 (42.0, 0.827×) and xsm_sa (42.4, 0.835×) passed the delay bar but
FAILED the calibrated screen catastrophically (114/133 perbit cell
rejections, 20/20 reduction rejections; raw max|z| 96–512). Root cause: the
structure is linear except for a single sparse constant multiplication;
insufficient nonlinearity. xsm_c3 (50.0) missed the delay bar.

### H family (keyed 32-bit Murmur-fmix halves) — REJECTED
fmix32h_a (82.8, 1.63×), fmix32h_b (87.8, 1.73×). The sequential 32-bit
multiplies are too slow. Structural, not tunable.

### X family (AND-Feistel: Simeck/Simon/double-AND)
...

### G family (Goldreich 5-local F Feistel)
...

### B family (Blink/Midori SPN: S1 + Midori M + ShuffleCell)
...

### S family (SPEEDY 6-bit S-box SPN)
...

### V family (SKINNY S-box in xorlin skeleton)
...

## Tooling lessons
- [analyze2.py](../analyze2.py) cannot parse yosys escaped identifiers (`\u.val`, `\R[5]`,
  `\rnd[0].rk`) from hierarchy flattening, unpacked arrays, or generate
  blocks. Fix: generate fully-flat, unrolled Verilog (no arrays/generate/
  hierarchy) via Python generators into [`rtl/flat2/`](rtl/flat2/).
- Never hand-derive RTL constants; always compute (skinny 3C/4C/5C lesson).
- Variable part-select on function return values breaks yosys; use explicit
  concatenation.

## SOTA survey transfers (applied)
- Blink/Midori SPN (B family): depth-3.5 S-box + Midori M + free nibble perm
- SPEEDY 6-bit S-box (S family): Table 3 verified vs paper DNF (64/64)
- THF S1 S-box: `0,1,2,4,3,8,f,c,9,5,b,6,7,e,d,a`
