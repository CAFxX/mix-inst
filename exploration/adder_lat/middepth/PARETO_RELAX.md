# Pareto-Relax Track: Fisher Testing of Cost-Killed Designs

**Date**: 2026-10-12  
**Directive**: Carlo (2026-10-12): "<10u is a soft target, anything improving pareto would be valuable."  
**Task**: Three designs killed SOLELY on cost (>10u) without Fisher testing. All under 18.6u Pareto. Test Fisher.

## Results

| Design | S0 | Fisher LIN | Fisher DIFF | Verdict |
|--------|----|------------|-------------|---------|
| **V1** 3-stage SPN (PRESENT) | 13.0u | FLAG (D=4096/4096 both keys) | FLAG (worst\|z\|=1.48M both) | **DEAD** — O146 confirmed |
| **V2** 3-stage MUXD (compressed) | 11.8u | FLAG (D=4096/4096 both keys) | FLAG (worst\|z\|=740k/461k) | **DEAD** — O145 confirmed |
| **V4 Opt2** S-box→MUX2→4term→MUX2 | 12.5u (est.) | FLAG (D=4096/4096 both keys) | FLAG (worst\|z\|=118k/923k) | **DEAD** — O147 confirmed |

All three fail Fisher catastrophically (LIN D=4096/4096 is maximum possible failure).

## Details

### V1 (13.0u)
- **Verilog**: `v1_spn3/spn3_present_full.v`
- **Model**: `v1_spn3/v1_model.py::mix_spn3` (3 stages, PRESENT P-box)
- **Fisher log**: `v1_spn3/fisher_v1.json`
- **Mechanism**: 3-stage SPN with wiring-only linear cannot diffuse the 6-bit input cube. Same 8-bit bottleneck as O135.

### V2 (11.8u)
- **Verilog**: `v2_mux3/muxd3_nod.v` (stages (7,41,23), (11,53,29), (3,47,61))
- **Model**: Custom `mix_v2_vec` (compressed y=x^g, no d-term)
- **Fisher log**: `v2_mux3/fisher_v2.json`
- **Mechanism**: 3-stage MUXD insufficient depth for Fisher. Consistent with 5-stage requirement (18.6u frontier).

### V4 Option 2 (12.5u)
- **Status**: Was never built (killed on cost before building). Constructed for this track.
- **Model**: `/tmp/model_v4opt2.py::mix_v4opt2_vec` (S-box→MUX2→4-term→MUX2)
- **Bijectivity**: 10k/10k unique (spot check PASS)
- **Fisher log**: `v4_hybrid4/fisher_v4opt2.json`
- **Mechanism**: Despite degree 12 (3×2×2) and 4 stages, the XOR-heavy structure cancels on sequential inputs. Same as R1/O157.

## Conclusion

No Pareto improvement. The cost-kills (O145, O146, O147) are **confirmed** by empirical Fisher failure. The 11.8u–13.0u range contains no Fisher-passing designs among the tested constructions.

**Pareto frontier unchanged**: t6_b59_47 at 18.6u.
