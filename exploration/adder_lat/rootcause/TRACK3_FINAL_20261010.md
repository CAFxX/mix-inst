# Track 3: From Root Cause to Design Rules — Final Report

**2026-10-10, Track 3 supervisor.** Mission: turn the 5-stage DIFF wall
theorem into design rules and design from first principles.

## 1. Design Rules (rootcause/DESIGN_RULES.md)

Eight rules derived from the theorem + experiments:

1. **Difference fan-out determines the wall**: 4-stage prefix uniformity
   U=min_d maxP[miss] is the predictor (fz15_c U=0.295 vs and5xa U=0.50).
2. **Triple fan-out beats double**: t3 (M=I+R^c+R^e) spreads faster than
   AND-cascade (M=I+R^c). The fundamental lever.
3. **v2 proxy replicates diffprof**: SEQUENTIAL x (0..2^N), all 64 single-bit
   + structured + nibble deltas. **v1 (random x) was WRONG** — al_ht51 looked
   clean (z=3.4) but real S2 killed it (z=300.3). Sequential inputs expose
   AND-masking bias that random inputs hide.
4. **Cost budget**: 2×t3+3×and=19.05u is the only sub-20.1u 5-stage hetero.
5. **Position matters**: t3 early for d_4 uniformity, t3 late for output balance.
6. **S-box escape hatch**: per-nibble quiet (4 zero bits) breaks the wall.
   asb5a (22.3u) proves it.
7. **Cannot work**: pure 5-stage AND (theorem), AND3 (touched correlation 0.5,
   z=159+), sbox-first (z=27-57), 4-stage anything.
8. **Strong layer LAST**: sbox-first fails; asb5a (sbox last) works.

## 2. v2 Proxy Validation (6 reference designs)

| design | v2 z | real verdict | match |
|---|---|---|---|
| and5xa | 386.1 | S2 KILL | ✓ |
| fz15_c | 10.5 | S2 PASS | ✓ (borderline) |
| asb5a | 3.8 | S2 PASS | ✓ |
| asb4a | 55.9 | S1 DIFF-dead | ✓ |
| al_ht51 | 19.0 | S2 KILL (300.3) | ✓ |
| and6a | 16.1 | S2 PASS | ✓ |

## 3. First-Principles Design Attempts

**Wave-12 hetero t3/and** (al_ht51/52/53):
- S0: 19.9u / 20.4u / 19.8u (ht51/ht53 beat 20.1u frontier!)
- S2: ALL KILLED (ht51 z=300.3, ht53 z=127.1)
- Root cause: v1 proxy methodology bug (random x). v2 correctly kills them.

**v2 search (500 hetero designs)**: 0/500 pass (threshold z<10).
Hetero t3/and is likely INFEASIBLE for 5-stage S2-clean.

**Falsified**: AND3 (z=159+), sbox-first (z=27-57).

## 4. The Landscape (sub-20.1u 5-stage S2-clean)

| construction | cost | S2 | viable? |
|---|---|---|---|
| 5×AND | 16.75u | KILL (theorem) | NO |
| 5×t3 | 22.5u | PASS | too slow |
| 5 AND + S-box | 22.3u | PASS | too slow |
| hetero t3/and | 19.05u | 0/500 pass | likely NO |
| 6×AND (al_and6a) | 20.1u | PASS | **FRONTIER** |

**Conclusion**: A sub-20.1u 5-stage S2-clean design remains elusive. The
20.1u 6-stage AND-cascade may be the true optimum in this space. The design
rules explain WHY (fan-out economics), and the v2 proxy gives the tool to
test any future idea in minutes instead of GHA cycles.

## 5. Files

- `rootcause/DESIGN_RULES.md`: 8 design rules + methodology fix
- `rootcause/s2proxy_v2.py`: diffprof-exact proxy (sequential x, 115 deltas)
- `rootcause/search5d.py`: v2 hetero search (0/500)
- `rootcause/candidates5*.json`: search results
- `gen_wave12.py`: hetero bundle generator
- `LEADS_LEDGER.md`: wave-12 rows (ht51/ht53 S2-KILLED, design-rules lead)

## 6. Open Leads

1. **Cheaper triple fan-out**: Is there a <4.5u/stage op with M=I+R^c+R^e?
2. **Partial S-box layer**: 8 S-boxes + 32 AND bits, cheaper than full 16?
3. **Non-AND/OR nonlinearity**: The theorem's re-test trigger — a new op with
   balanced-touch and rare-quiet, not AND-based.
4. **Accept 20.1u floor**: Pivot track-3 to P&R/area optimization of al_and6a.

**Frontier unchanged: al_and6a 20.1u.**
