#!/usr/bin/env python3
"""Wave-1 adder-latency candidate generator: single source of truth.

Each candidate spec -> candidates/<name>/{model.py, impl.c, rtl.v, meta.json}
with bit-identical semantics in Python/numpy, C, and Verilog.

Stage opcodes (x is the 64-bit state, ra..rg are rotl(x, r_i)):
  chi    : x ^= ((~ra) & rb) ^ rc
  and    : x ^= (ra & rb) ^ rc
  andxor : x ^= ra ^ (rb & rc)
  orand  : x ^= (ra & rb) ^ (rc | rd) ^ re
  triand : x ^= (ra & rb & rc) ^ (rd & re & rf) ^ rg
  arx2   : x=(x+k); x^=rotl(x,13)^rotl(x,29); x+=(rotl(x,7)); x^=rotl(x,17)^rotl(x,41); x^=rotl(x,23); x^=k
  feist_chi: 32-bit Feistel, 6 rounds, F(y,rk,a,b,c) = y ^ ((~ra)&rb) ^ rc ^ rk

Key schedule: pre-whiten x ^= k; optional per-stage rk_i = rotl(k,13*(i+1)) ^ RC[i]
folded into the stage XOR tree; post x ^= rotl(k,13) (al_cascad convention).
"""
import json, os, shutil, sys

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054,
      0x2545F4914F6CDD1D, 0x9E3779B97F4A7C15 ^ 0xDEADBEEF, 0x3C6EF372FE94F82A ^ 0x12345678,
      0xDAA66D2C7DDF743F ^ 0xABCDEF01, 0x78DDE6E5FD29F054 ^ 0x55AA55AA,
      0x2545F4914F6CDD1D ^ 0x0F0F0F0F, 0x9E3779B97F4A7C15 ^ 0xF0F0F0F0,
      0x3C6EF372FE94F82A ^ 0x00FF00FF]

# (name, op, stage rotation tuples, per_stage_key)
SPECS = [
    # chi cascade axis: 4 / 6 / 8 stages
    ("al_chi4", "chi", [(1,2,13),(7,19,5),(17,31,7),(29,43,11)], False,
     "4-stage chi cascade: x ^= ((~ra)&rb) ^ rc"),
    ("al_chi6", "chi", [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37),(19,41,23)], False,
     "6-stage chi cascade: x ^= ((~ra)&rb) ^ rc"),
    ("al_chi8", "chi", [(1,2,13),(7,19,5),(3,11,29),(13,5,17),(17,31,7),(11,23,37),(29,43,11),(19,41,23)], False,
     "8-stage chi cascade: x ^= ((~ra)&rb) ^ rc"),
    # 4-stage chi with per-stage key folded into XOR tree (no extra depth)
    ("al_chi4k", "chi", [(1,2,13),(7,19,5),(17,31,7),(29,43,11)], True,
     "4-stage chi cascade + per-stage key fold: x ^= ((~ra)&rb) ^ rc ^ rk"),
    # AND/OR mix: 6 stages
    ("al_orand6", "orand", [(1,8,3,11,2),(7,19,5,17,13),(2,9,13,29,4),(11,23,19,37,7),(5,17,29,43,13),(13,29,41,53,19)], False,
     "6-stage AND/OR mix: x ^= (ra&rb) ^ (rc|rd) ^ re"),
    # triple-AND (degree 3 per stage): 5 stages
    ("al_triand5", "triand", [(1,2,4,8,16,32,7),(3,9,27,5,15,45,11),(7,21,63-40,13,39,53,17),(11,33,35,19,57,43,23),(17,51,25,29,23,5,31)], False,
     "5-stage triple-AND: x ^= (ra&rb&rc) ^ (rd&re&rf) ^ rg"),
    # 2-addition ARX
    ("al_arx2", "arx2", [], False,
     "2-addition ARX: add/xor/add/xor"),
    # 32-bit Feistel with chi F, 6 rounds
    ("al_feist_chi6", "feist_chi", [(1,2,7),(3,11,5),(7,19,13),(2,9,17),(5,17,23),(11,23,29)], True,
     "6-round 32-bit Feistel, F(y)=y^((~ra)&rb)^rc^rk"),
    # 10 stages of 2u: x ^= ra ^ (rb & rc)
    ("al_andxor10", "andxor", [(1,8,2),(3,11,5),(7,19,13),(2,9,4),(5,17,11),(13,29,7),(11,23,17),(19,37,23),(23,41,29),(31,47,37)], False,
     "10-stage: x ^= ra ^ (rb & rc) (~2u/stage)"),
    # ---- wave 2 ----
    # 5-stage chi (phase transition for chi was 4->6)
    ("al_chi5", "chi", [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37)], False,
     "5-stage chi cascade: x ^= ((~ra)&rb) ^ rc"),
    # 4-stage AND/OR mix (orand6 passed triage; fewer stages?)
    ("al_orand4", "orand", [(1,8,3,11,2),(7,19,5,17,13),(2,9,13,29,4),(11,23,19,37,7)], False,
     "4-stage AND/OR mix: x ^= (ra&rb) ^ (rc|rd) ^ re"),
    # dense: 3 AND-pairs + 2 XOR terms per stage, 4 stages
    ("al_dense4", "dense", [(1,2,4,8,16,32),(3,7,13,19,29,5),(11,17,23,31,41,13),(5,15,25,37,47,7)], False,
     "4-stage dense: x ^= (ra&rb)^(rc&rd)^(re&rf)^rg^rh"),
    # trichi: 3 parallel chi-terms per stage (fan-in 7, keeps NOT nonlinearity)
    ("al_trichi3", "trichi", [(1,2,4,8,16,32,7),(3,9,13,19,29,5,11),(11,17,23,31,41,13,17)], False,
     "3-stage triple-chi: x ^= ((~ra)&rb)^((~rc)&rd)^((~re)&rf)^rg (fan-in 7)"),
    ("al_trichi4", "trichi", [(1,2,4,8,16,32,7),(3,9,13,19,29,5,11),(11,17,23,31,41,13,17),(5,15,25,37,47,7,23)], False,
     "4-stage triple-chi: x ^= ((~ra)&rb)^((~rc)&rd)^((~re)&rf)^rg (fan-in 7)"),
    ("al_trichi3b", "trichi", [(4,18,6,50,27,54,58),(56,25,35,22,11,9,45),(16,1,39,47,29,43,37)], False,
     "3-stage triple-chi, spread rotations: x ^= ((~ra)&rb)^((~rc)&rd)^((~re)&rf)^rg"),
    # nibble-chi SPN: per-nibble n ^= ((n rol 1)&(n rol 2)), then XOR-rotation spread
    ("al_nibchi3", "nibchi", [(13,29),(7,41),(17,5)], False,
     "3-round nibble-chi SPN: N(x)=x^((x rol1 4b)&(x rol2 4b)); L=^rot(c1)^rot(c2)"),
    ("al_nibchi4", "nibchi", [(13,29),(7,41),(17,5),(23,11)], False,
     "4-round nibble-chi SPN"),
    # dual-AND: exact al_cascad4 construction (2 AND-pairs + rotl term), 4 stages
    ("al_dualand4", "dualand", [(1,8,3,11,2),(7,19,5,17,13),(2,9,13,29,4),(11,23,19,37,7)], False,
     "4-stage dual-AND: x ^= (ra&rb) ^ (rc&rd) ^ re"),
    # ---- wave 3 ----
    ("al_andxor6", "andxor", [(1,8,2),(3,11,5),(7,19,13),(2,9,4),(5,17,11),(13,29,7)], False,
     "6-stage: x ^= ra ^ (rb & rc)"),
    ("al_andxor8", "andxor", [(1,8,2),(3,11,5),(7,19,13),(2,9,4),(5,17,11),(13,29,7),(11,23,17),(19,37,23)], False,
     "8-stage: x ^= ra ^ (rb & rc)"),
    ("al_ornot6", "ornot", [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37),(19,41,23)], False,
     "6-stage OR-NOT: x ^= ((~ra)|rb) ^ rc"),
    ("al_chi6k", "chi", [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37),(19,41,23)], True,
     "6-stage chi + per-stage key fold"),
    ("al_nibchi4b", "nibchib", [(13,29),(7,41),(17,5),(23,11)], False,
     "4-round nibble-OR SPN: N(x)=x^((x rol1 4b)|(x rol2 4b))"),
    # ---- wave 4 (2026-10-08): new axes ----
    # chi 8-stage, alternative rotation schedule (widen chi schedule axis;
    # al_chi8 is the track's only clean candidate)
    ("al_chi8b", "chi", [(3,5,17),(11,23,2),(7,13,31),(19,29,41),(5,17,23),(13,37,43),(23,47,53),(31,59,61)], False,
     "8-stage chi cascade, alternate rotation schedule"),
    # chi 6-stage, alternate schedule
    ("al_chi6b", "chi", [(5,9,23),(13,29,3),(7,17,41),(2,11,19),(23,37,47),(17,43,59)], False,
     "6-stage chi cascade, alternate rotation schedule"),
    # ornot 6-stage, alternate schedule (ornot6 @20.1u had systematic high-bit
    # diff bias O79 -- test whether the bias is schedule-dependent)
    ("al_ornot6b", "ornot", [(3,7,19),(13,27,5),(11,21,37),(23,41,11),(17,31,47),(29,53,59)], False,
     "6-stage OR-NOT, alternate rotation schedule"),
    # ornotand: NEW primitive -- x ^= ((~ra)|rb) ^ (rc&rd) ^ re (~2u/stage,
    # two nonlinear gates in parallel per stage)
    ("al_ornotand5", "ornotand", [(1,7,13,19,29),(3,11,23,31,41),(7,17,29,43,53),(11,23,37,47,59),(17,31,43,55,61)], False,
     "5-stage OR-NOT/AND: x ^= ((~ra)|rb) ^ (rc&rd) ^ re"),
    ("al_ornotand6", "ornotand", [(1,7,13,19,29),(3,11,23,31,41),(7,17,29,43,53),(11,23,37,47,59),(17,31,43,55,61),(23,41,53,59,2)], False,
     "6-stage OR-NOT/AND: x ^= ((~ra)|rb) ^ (rc&rd) ^ re"),
    # chiconst: chi + per-stage CONSTANT fold (constants free in hardware;
    # stage asymmetry without the per-stage KEY-fold differential pathology O83)
    ("al_chiconst8", "chiconst", [(1,2,13),(7,19,5),(3,11,29),(13,5,17),(17,31,7),(11,23,37),(29,43,11),(19,41,23)], False,
     "8-stage chi + per-stage constant fold: x ^= ((~ra)&rb) ^ rc ^ RC[i]"),
    # feistel chi-F, 8 rounds (6 rounds insufficient O: al_feist_chi6 KILL)
    ("al_feist_chi8", "feist_chi", [(1,2,7),(3,11,5),(7,19,13),(2,9,17),(5,17,23),(11,23,29),(13,29,31),(17,31,7)], True,
     "8-round 32-bit Feistel, F(y)=y^((~ra)&rb)^rc^rk"),
    # hybrid 8: heterogeneous chi/and/ornot alternation
    ("al_hybrid8", "hybrid", [("chi",(1,2,13)),("ornot",(7,19,5)),("and",(3,11,29)),("chi",(17,31,7)),("and",(11,23,37)),("ornot",(19,41,23)),("chi",(13,29,41)),("and",(23,47,53))], False,
     "8-stage heterogeneous cascade alternating chi/ornot/and"),
    # === WAVE-5 (2026-10-08): push below 19.8u ===
    # chi6 schedule widening: systematic rotation-schedule search for 6-stage chi
    ("al_chi6c", "chi", [(5,11,23),(13,29,7),(3,17,41),(19,37,11),(7,23,53),(29,47,13)], False,
     "6-stage chi cascade, schedule C"),
    ("al_chi6d", "chi", [(2,7,19),(11,23,43),(5,13,31),(17,29,7),(23,41,13),(37,53,19)], False,
     "6-stage chi cascade, schedule D"),
    # 5-stage mixed: 5 chi stages failed (O: al_chi5), but stronger per-stage ops might work
    ("al_mix5a", "hybrid", [("chi",(1,2,13)),("ornot",(3,11,23)),("chi",(7,19,5)),("ornot",(11,23,37)),("chi",(17,31,7))], False,
     "5-stage mixed chi/ornot cascade"),
    ("al_mix5b", "hybrid", [("ornot",(1,7,13)),("chi",(3,11,29)),("ornot",(7,17,29)),("chi",(13,5,17)),("ornot",(17,31,43))], False,
     "5-stage mixed ornot/chi cascade"),
    # ornot schedule widening (ornot6b 21.0u promising; O79 bias was schedule-dependent)
    ("al_ornot6c", "ornot", [(5,13,29),(7,23,41),(17,37,11),(3,19,47),(23,43,13),(31,59,7)], False,
     "6-stage ornot cascade, schedule C"),
    ("al_ornot6d", "ornot", [(2,11,23),(13,31,7),(5,19,43),(29,47,11),(7,17,37),(41,53,23)], False,
     "6-stage ornot cascade, schedule D"),
    # === WAVE-6 (2026-10-08): break the 19.8u barrier ===
    # 6-stage AND cascade: al_cascad (8-stage and) was 25.5u = 3.2u/stage.
    # 6 stages could hit ~19.2u if the per-stage cost holds.
    ("al_and6a", "and", [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37),(19,41,23)], False,
     "6-stage AND-rotation cascade: x ^= (ra & rb) ^ rc"),
    ("al_and6b", "and", [(5,11,23),(13,29,7),(3,17,41),(19,37,11),(7,23,53),(29,47,13)], False,
     "6-stage AND-rotation cascade, schedule B"),
    # === WAVE-7 (2026-10-08): avalanche-aware chi6 schedules ===
    # al_chi6b (19.8u) died at Q1 (sac_z5=30): rotation schedule not optimized
    # for avalanche uniformity. These schedules are designed for maximal
    # bit-lane mixing: 18 distinct rotations, within-stage min circular
    # distance >= 6, no arithmetic progressions (avoid linear structure).
    ("al_chi6e", "chi", [(20,28,35),(11,4,46),(56,43,16),(17,50,5),(44,29,62),(36,54,61)], False,
     "6-stage chi cascade, avalanche-aware schedule E (random well-separated)"),
    ("al_chi6f", "chi", [(10,45,35),(59,2,49),(34,20,42),(6,62,17),(57,24,11),(23,15,61)], False,
     "6-stage chi cascade, avalanche-aware schedule F (random well-separated)"),
    ("al_chi6g", "chi", [(31,1,44),(4,28,34),(5,63,40),(20,14,42),(8,39,55),(45,61,21)], False,
     "6-stage chi cascade, avalanche-aware schedule G (random well-separated)"),
]

PY_PREAMBLE = '''"""%s. Adder-latency wave-1 probe (generated by gen_wave1.py)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)
RC = np.array([%s], dtype=np.uint64)
def _rotl(x, r):
    r %%= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _rotl32(x, r):
    r %%= 32
    return ((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & M32 if r else x
def _nibchi(x):
    # per-nibble n ^= ((n rol 1) & (n rol 2)) within 4-bit nibbles
    r1 = (((x << np.uint64(1)) & np.uint64(0xEEEEEEEEEEEEEEEE)) |
          ((x >> np.uint64(3)) & np.uint64(0x1111111111111111)))
    r2 = (((x << np.uint64(2)) & np.uint64(0xCCCCCCCCCCCCCCCC)) |
          ((x >> np.uint64(2)) & np.uint64(0x3333333333333333)))
    return (x ^ (r1 & r2)) & M64
def _nibchi_or(x):
    # per-nibble n ^= ((n rol 1) | (n rol 2)) within 4-bit nibbles (OR variant)
    r1 = (((x << np.uint64(1)) & np.uint64(0xEEEEEEEEEEEEEEEE)) |
          ((x >> np.uint64(3)) & np.uint64(0x1111111111111111)))
    r2 = (((x << np.uint64(2)) & np.uint64(0xCCCCCCCCCCCCCCCC)) |
          ((x >> np.uint64(2)) & np.uint64(0x3333333333333333)))
    return (x ^ (r1 | r2)) & M64
'''

def gen_model(name, op, stages, psk, desc):
    rc = ", ".join(hex(v) for v in RC[:12])
    s = PY_PREAMBLE % (desc, rc)
    if op in ("chi", "and", "andxor", "orand", "triand", "dense", "dualand", "ornot", "ornotand", "chiconst", "trichi"):
        s += "STAGES = %s\n" % (stages,)
        s += "def mix_np(V, K):\n"
        s += "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)\n"
        s += "    x = (x ^ k) & M64\n"
        if op == "chi":
            s += "    for i,(a,b,c) in enumerate(STAGES):\n"
            s += "        t = (x ^ ((_rotl(x,a) ^ M64) & _rotl(x,b)) ^ _rotl(x,c)) & M64\n"
        elif op == "dense":
            s += "    for i,(a,b,c,d,e,f) in enumerate(STAGES):\n"
            s += "        t = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ (_rotl(x,c) & _rotl(x,d)) ^ (_rotl(x,e) & _rotl(x,f))) & M64\n"
        elif op == "dualand":
            s += "    for i,(a,b,c,d,e) in enumerate(STAGES):\n"
            s += "        t = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ (_rotl(x,c) & _rotl(x,d)) ^ _rotl(x,e)) & M64\n"
        elif op == "trichi":
            s += "    for i,(a,b,c,d,e,f,g) in enumerate(STAGES):\n"
            s += "        t = (x ^ (((_rotl(x,a) ^ M64) & _rotl(x,b))) ^ (((_rotl(x,c) ^ M64) & _rotl(x,d))) ^ (((_rotl(x,e) ^ M64) & _rotl(x,f))) ^ _rotl(x,g)) & M64\n"
        elif op == "ornot":
            s += "    for i,(a,b,c) in enumerate(STAGES):\n"
            s += "        t = (x ^ ((_rotl(x,a) ^ M64) | _rotl(x,b)) ^ _rotl(x,c)) & M64\n"
        elif op == "and":
            s += "    for i,(a,b,c) in enumerate(STAGES):\n"
            s += "        t = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64\n"
        elif op == "andxor":
            s += "    for i,(a,b,c) in enumerate(STAGES):\n"
            s += "        t = (x ^ _rotl(x,a) ^ (_rotl(x,b) & _rotl(x,c))) & M64\n"
        elif op == "orand":
            s += "    for i,(a,b,c,d,e) in enumerate(STAGES):\n"
            s += "        t = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ (_rotl(x,c) | _rotl(x,d)) ^ _rotl(x,e)) & M64\n"
        elif op == "ornotand":
            s += "    for i,(a,b,c,d,e) in enumerate(STAGES):\n"
            s += "        t = (x ^ ((_rotl(x,a) ^ M64) | _rotl(x,b)) ^ (_rotl(x,c) & _rotl(x,d)) ^ _rotl(x,e)) & M64\n"
        elif op == "chiconst":
            s += "    for i,(a,b,c) in enumerate(STAGES):\n"
            s += "        t = (x ^ ((_rotl(x,a) ^ M64) & _rotl(x,b)) ^ _rotl(x,c) ^ RC[i % len(RC)]) & M64\n"
        elif op == "triand":
            s += "    for i,(a,b,c,d,e,f,g) in enumerate(STAGES):\n"
            s += "        t = (x ^ (_rotl(x,a) & _rotl(x,b) & _rotl(x,c)) ^ (_rotl(x,d) & _rotl(x,e) & _rotl(x,f)) ^ _rotl(x,g)) & M64\n"
        if psk:
            s += "        t = (t ^ _rotl(k, 13*(i+1)) ^ RC[i % len(RC)]) & M64\n"
        s += "        x = t\n"
        s += "    x = (x ^ _rotl(k, 13)) & M64\n"
        s += "    return x & M64\n"
    elif op == "nibchi":
        s += "STAGES = %s\n" % (stages,)
        s += "def mix_np(V, K):\n"
        s += "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)\n"
        s += "    x = (x ^ k) & M64\n"
        s += "    for i,(c1,c2) in enumerate(STAGES):\n"
        s += "        y = _nibchi(x)\n"
        s += "        x = (y ^ _rotl(y,c1) ^ _rotl(y,c2)) & M64\n"
        s += "    x = (x ^ _rotl(k, 13)) & M64\n"
        s += "    return x & M64\n"
    elif op == "nibchib":
        s += "STAGES = %s\n" % (stages,)
        s += "def mix_np(V, K):\n"
        s += "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)\n"
        s += "    x = (x ^ k) & M64\n"
        s += "    for i,(c1,c2) in enumerate(STAGES):\n"
        s += "        y = _nibchi_or(x)\n"
        s += "        x = (y ^ _rotl(y,c1) ^ _rotl(y,c2)) & M64\n"
        s += "    x = (x ^ _rotl(k, 13)) & M64\n"
        s += "    return x & M64\n"
    elif op == "hybrid":
        # stages: list of (subop, (a,b,c)) with subop in {"chi","and"}
        s += "STAGES = %s\n" % (stages,)
        s += "def mix_np(V, K):\n"
        s += "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)\n"
        s += "    x = (x ^ k) & M64\n"
        s += "    for i,(sop,(a,b,c)) in enumerate(STAGES):\n"
        s += "        ra, rb, rc = _rotl(x,a), _rotl(x,b), _rotl(x,c)\n"
        s += "        if sop == 'chi':\n"
        s += "            t = (x ^ ((~ra) & rb) ^ rc) & M64\n"
        s += "        elif sop == 'ornot':\n"
        s += "            t = (x ^ ((~ra) | rb) ^ rc) & M64\n"
        s += "        elif sop == 'or':\n"
        s += "            t = (x ^ (ra | rb) ^ rc) & M64\n"
        s += "        else:\n"
        s += "            t = (x ^ (ra & rb) ^ rc) & M64\n"
        s += "        x = t\n"
        s += "    x = (x ^ _rotl(k, 13)) & M64\n"
        s += "    return x & M64\n"
    elif op == "arx2":
        s += "def mix_np(V, K):\n"
        s += "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)\n"
        s += "    x = (x + k) & M64\n"
        s += "    x = (x ^ _rotl(x,13) ^ _rotl(x,29)) & M64\n"
        s += "    x = (x + _rotl(x,7)) & M64\n"
        s += "    x = (x ^ _rotl(x,17) ^ _rotl(x,41) ^ _rotl(x,23)) & M64\n"
        s += "    x = (x ^ k) & M64\n"
        s += "    return x & M64\n"
    elif op == "feist_chi":
        s += "STAGES = %s\n" % (stages,)
        s += "def mix_np(V, K):\n"
        s += "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)\n"
        s += "    L = (x >> np.uint64(32)) & M32; R = x & M32\n"
        s += "    for i,(a,b,c) in enumerate(STAGES):\n"
        s += "        rk = ((_rotl(k, 13*(i+1)) ^ RC[i % len(RC)])) & M32\n"
        s += "        F = (R ^ ((_rotl32(R,a) ^ M32) & _rotl32(R,b)) ^ _rotl32(R,c) ^ rk) & M32\n"
        s += "        L, R = R, (L ^ F) & M32\n"
        s += "    return (((L << np.uint64(32)) | R)) & M64\n"
    s += "def mix(v, k):\n    return int(mix_np(np.uint64(v), np.uint64(k)))\n"
    return s

def rotl_c(var, r):
    return f"rotl64({var},{r})"

def gen_impl(name, op, stages, psk, desc):
    s = "#include <stdint.h>\n"
    s += "static inline uint64_t rotl64(uint64_t x, int r) {\n    r &= 63;\n    return r ? (x << r) | (x >> (64 - r)) : x;\n}\n"
    s += "static inline uint32_t rotl32(uint32_t x, int r) {\n    r &= 31;\n    return r ? (x << r) | (x >> (32 - r)) : x;\n}\n"
    s += f"// {desc}\n"
    if op in ("nibchi", "nibchib"):
        s += ("static inline uint64_t nibchi64(uint64_t x) {\n"
              "    uint64_t r1 = ((x << 1) & 0xEEEEEEEEEEEEEEEEULL) | ((x >> 3) & 0x1111111111111111ULL);\n"
              "    uint64_t r2 = ((x << 2) & 0xCCCCCCCCCCCCCCCCULL) | ((x >> 2) & 0x3333333333333333ULL);\n"
              "    return x ^ (r1 & r2);\n}\n"
              "static inline uint64_t nibchi_or64(uint64_t x) {\n"
              "    uint64_t r1 = ((x << 1) & 0xEEEEEEEEEEEEEEEEULL) | ((x >> 3) & 0x1111111111111111ULL);\n"
              "    uint64_t r2 = ((x << 2) & 0xCCCCCCCCCCCCCCCCULL) | ((x >> 2) & 0x3333333333333333ULL);\n"
              "    return x ^ (r1 | r2);\n}\n")
    s += "uint64_t mix_hash(uint64_t val, uint64_t key) {\n"
    if op in ("chi","and","andxor","orand","triand","dense","dualand","ornot","ornotand","chiconst","trichi"):
        s += "    uint64_t x = val ^ key;\n"
        for i, st in enumerate(stages):
            nms = "abcdefg"[:len(st)]
            terms = ", ".join(f"rotl64(x,{r})" for r in st)
            s += f"    {{ uint64_t r[{len(st)}] = {{{terms}}};\n"
            if op == "chi":
                a,b,c = nms[0],nms[1],nms[2]
                s += f"      x ^= ((~r[0]) & r[1]) ^ r[2]; }}\n"
            elif op == "dense":
                s += f"      x ^= (r[0] & r[1]) ^ (r[2] & r[3]) ^ (r[4] & r[5]); }}\n"
            elif op == "dualand":
                s += f"      x ^= (r[0] & r[1]) ^ (r[2] & r[3]) ^ r[4]; }}\n"
            elif op == "trichi":
                s += f"      x ^= ((~r[0]) & r[1]) ^ ((~r[2]) & r[3]) ^ ((~r[4]) & r[5]) ^ r[6]; }}\n"
            elif op == "ornot":
                s += f"      x ^= ((~r[0]) | r[1]) ^ r[2]; }}\n"
            elif op == "ornotand":
                s += f"      x ^= ((~r[0]) | r[1]) ^ (r[2] & r[3]) ^ r[4]; }}\n"
            elif op == "chiconst":
                s += f"      x ^= ((~r[0]) & r[1]) ^ r[2] ^ 0x{RC[i]:016X}ULL; }}\n"
            elif op == "and":
                s += f"      x ^= (r[0] & r[1]) ^ r[2]; }}\n"
            elif op == "andxor":
                s += f"      x ^= r[0] ^ (r[1] & r[2]); }}\n"
            elif op == "orand":
                s += f"      x ^= (r[0] & r[1]) ^ (r[2] | r[3]) ^ r[4]; }}\n"
            elif op == "triand":
                s += f"      x ^= (r[0] & r[1] & r[2]) ^ (r[3] & r[4] & r[5]) ^ r[6]; }}\n"
            if psk:
                s += f"    x ^= rotl64(key,{13*(i+1)} % 64) ^ 0x{RC[i]:016X}ULL;\n"
        s += "    x ^= rotl64(key, 13);\n    return x;\n}"
    elif op == "nibchi":
        s += "    uint64_t x = val ^ key;\n"
        for i,(c1,c2) in enumerate(stages):
            s += (f"    {{ uint64_t y = nibchi64(x);\n"
                  f"      x = y ^ rotl64(y,{c1}) ^ rotl64(y,{c2}); }}\n")
        s += "    x ^= rotl64(key, 13);\n    return x;\n}"
    elif op == "nibchib":
        s += "    uint64_t x = val ^ key;\n"
        for i,(c1,c2) in enumerate(stages):
            s += (f"    {{ uint64_t y = nibchi_or64(x);\n"
                  f"      x = y ^ rotl64(y,{c1}) ^ rotl64(y,{c2}); }}\n")
        s += "    x ^= rotl64(key, 13);\n    return x;\n}"
    elif op == "hybrid":
        # stages: list of (subop, (a,b,c))
        s += "    uint64_t x = val ^ key;\n"
        for i,(sop,(a,b,c)) in enumerate(stages):
            s += (f"    {{ uint64_t ra = rotl64(x,{a}), rb = rotl64(x,{b}), rc = rotl64(x,{c});\n")
            if sop == "chi":
                s += "      x ^= ((~ra) & rb) ^ rc; }\n"
            elif sop == "ornot":
                s += "      x ^= ((~ra) | rb) ^ rc; }\n"
            elif sop == "or":
                s += "      x ^= (ra | rb) ^ rc; }\n"
            else:
                s += "      x ^= (ra & rb) ^ rc; }\n"
        s += "    x ^= rotl64(key, 13);\n    return x;\n}"
    elif op == "arx2":
        s += ("    uint64_t x = val + key;\n"
              "    x ^= rotl64(x,13) ^ rotl64(x,29);\n"
              "    x += rotl64(x,7);\n"
              "    x ^= rotl64(x,17) ^ rotl64(x,41) ^ rotl64(x,23);\n"
              "    x ^= key;\n    return x;\n}")
    elif op == "feist_chi":
        s += ("    uint32_t L = (uint32_t)(val >> 32), R = (uint32_t)val;\n")
        for i,(a,b,c) in enumerate(stages):
            s += (f"    {{ uint32_t rk = (uint32_t)(rotl64(key,{13*(i+1)} % 64) ^ 0x{RC[i]:016X}ULL);\n"
                  f"      uint32_t F = R ^ ((~rotl32(R,{a})) & rotl32(R,{b})) ^ rotl32(R,{c}) ^ rk;\n"
                  f"      L ^= F; uint32_t t = L; L = R; R = t; }}\n")
        s += "    return ((uint64_t)L << 32) | R;\n}"
    return s

def vl_rotl(xw, r, w=64):
    if r % w == 0:
        return xw
    r %= w
    return "{%s[%d:0], %s[%d:%d]}" % (xw, w-1-r, xw, w-1, w-r)

def gen_rtl(name, op, stages, psk, desc):
    s = f"// {name}: {desc} (generated by gen_wave1.py)\n"
    s += f"module {name}(\n    input [63:0] v,\n    input [63:0] k,\n    output [63:0] o\n);\n"
    if op in ("chi","and","andxor","orand","triand","dense","dualand","ornot","ornotand","chiconst","trichi"):
        s += "    wire [63:0] x0 = v ^ k;\n"
        for i, st in enumerate(stages):
            nms = "abcdefg"[:len(st)]
            for j, r in enumerate(st):
                s += f"    wire [63:0] s{i}{nms[j]} = {vl_rotl('x%d' % i, r)};\n"
            if op == "chi":
                e = f"x{i} ^ ((~s{i}a) & s{i}b) ^ s{i}c"
            elif op == "and":
                e = f"x{i} ^ (s{i}a & s{i}b) ^ s{i}c"
            elif op == "andxor":
                e = f"x{i} ^ s{i}a ^ (s{i}b & s{i}c)"
            elif op == "orand":
                e = f"x{i} ^ (s{i}a & s{i}b) ^ (s{i}c | s{i}d) ^ s{i}e"
            elif op == "triand":
                e = f"x{i} ^ (s{i}a & s{i}b & s{i}c) ^ (s{i}d & s{i}e & s{i}f) ^ s{i}g"
            elif op == "dense":
                e = f"x{i} ^ (s{i}a & s{i}b) ^ (s{i}c & s{i}d) ^ (s{i}e & s{i}f)"
            elif op == "dualand":
                e = f"x{i} ^ (s{i}a & s{i}b) ^ (s{i}c & s{i}d) ^ s{i}e"
            elif op == "trichi":
                e = f"x{i} ^ ((~s{i}a) & s{i}b) ^ ((~s{i}c) & s{i}d) ^ ((~s{i}e) & s{i}f) ^ s{i}g"
            elif op == "ornot":
                e = f"x{i} ^ ((~s{i}a) | s{i}b) ^ s{i}c"
            elif op == "ornotand":
                e = f"x{i} ^ ((~s{i}a) | s{i}b) ^ (s{i}c & s{i}d) ^ s{i}e"
            elif op == "chiconst":
                e = f"x{i} ^ ((~s{i}a) & s{i}b) ^ s{i}c ^ 64'h{RC[i]:016x}"
            if psk:
                rr = (13*(i+1)) % 64
                e += f" ^ {vl_rotl('k', rr)} ^ 64'h{RC[i]:016x}"
            s += f"    wire [63:0] x{i+1} = {e};\n"
        s += f"    wire [63:0] kr = {vl_rotl('k', 13)};\n"
        s += f"    assign o = x{len(stages)} ^ kr;\n"
    elif op in ("nibchi", "nibchib"):
        s += "    wire [63:0] x0 = v ^ k;\n"
        for i,(c1,c2) in enumerate(stages):
            # per-nibble: y[4j+3:4j] = n ^ ((n rol 1) &/| (n rol 2))
            # build per-nibble wires then concat
            nibs = []
            for j in range(16):
                lo = 4*j
                s += f"    wire [3:0] n{i}_{j} = x{i}[{lo+3}:{lo}];\n"
                s += f"    wire [3:0] n{i}_{j}_r1 = {{n{i}_{j}[2:0], n{i}_{j}[3]}};\n"
                s += f"    wire [3:0] n{i}_{j}_r2 = {{n{i}_{j}[1:0], n{i}_{j}[3:2]}};\n"
                if op == "nibchi":
                    s += f"    wire [3:0] n{i}_{j}_y = n{i}_{j} ^ (n{i}_{j}_r1 & n{i}_{j}_r2);\n"
                else:
                    s += f"    wire [3:0] n{i}_{j}_y = n{i}_{j} ^ (n{i}_{j}_r1 | n{i}_{j}_r2);\n"
                nibs.append(f"n{i}_{j}_y")
            s += f"    wire [63:0] y{i} = {{{', '.join(reversed(nibs))}}};\n"
            s += f"    wire [63:0] x{i+1} = y{i} ^ {vl_rotl('y%d' % i, c1)} ^ {vl_rotl('y%d' % i, c2)};\n"
        s += f"    wire [63:0] kr = {vl_rotl('k', 13)};\n"
        s += f"    assign o = x{len(stages)} ^ kr;\n"
    elif op == "hybrid":
        # stages: list of (subop, (a,b,c))
        s += "    wire [63:0] x0 = v ^ k;\n"
        for i,(sop,(a,b,c)) in enumerate(stages):
            s += f"    wire [63:0] s{i}a = {vl_rotl('x%d' % i, a)};\n"
            s += f"    wire [63:0] s{i}b = {vl_rotl('x%d' % i, b)};\n"
            s += f"    wire [63:0] s{i}c = {vl_rotl('x%d' % i, c)};\n"
            if sop == "chi":
                e = f"x{i} ^ ((~s{i}a) & s{i}b) ^ s{i}c"
            elif sop == "ornot":
                e = f"x{i} ^ ((~s{i}a) | s{i}b) ^ s{i}c"
            elif sop == "or":
                e = f"x{i} ^ (s{i}a | s{i}b) ^ s{i}c"
            else:
                e = f"x{i} ^ (s{i}a & s{i}b) ^ s{i}c"
            s += f"    wire [63:0] x{i+1} = {e};\n"
        s += f"    wire [63:0] kr = {vl_rotl('k', 13)};\n"
        s += f"    assign o = x{len(stages)} ^ kr;\n"
    elif op == "arx2":
        s += ("    wire [63:0] a0 = v + k;\n"
              f"    wire [63:0] a1 = a0 ^ {vl_rotl('a0',13)} ^ {vl_rotl('a0',29)};\n"
              f"    wire [63:0] a2 = a1 + {vl_rotl('a1',7)};\n"
              f"    wire [63:0] a3 = a2 ^ {vl_rotl('a2',17)} ^ {vl_rotl('a2',41)} ^ {vl_rotl('a2',23)};\n"
              "    assign o = a3 ^ k;\n")
    elif op == "feist_chi":
        s += ("    wire [31:0] L0 = v[63:32];\n    wire [31:0] R0 = v[31:0];\n")
        for i,(a,b,c) in enumerate(stages):
            rr = (13*(i+1)) % 64
            # NB: part-select on a concatenation is Verilog-2005-illegal;
            # route through an intermediate wire first.
            s += (f"    wire [63:0] kk{i} = {vl_rotl('k', rr)};\n"
                  f"    wire [31:0] rk{i} = kk{i}[31:0] ^ 32'h{RC[i] & 0xFFFFFFFF:08x};\n"
                  f"    wire [31:0] F{i} = R{i} ^ ((~{vl_rotl('R%d' % i, a, 32)}) & {vl_rotl('R%d' % i, b, 32)}) ^ {vl_rotl('R%d' % i, c, 32)} ^ rk{i};\n"
                  f"    wire [31:0] L{i+1} = R{i};\n"
                  f"    wire [31:0] R{i+1} = L{i} ^ F{i};\n")
        n = len(stages)
        s += f"    assign o = {{L{n}, R{n}}};\n"
    s += "endmodule\n"
    # Port-name normalization: CANDIDATE_BRIEF.md mandates
    #   module <name>(input [63:0] val, input [63:0] key, output [63:0] out)
    # (check_rtl.py's testbench and the GHA S0 stage bind to val/key/out).
    # The generator body uses short v/k/o internally; rename whole-word
    # occurrences only (x0, s0a, rk, kr, kk0 etc. are untouched by \b).
    import re as _re
    s = _re.sub(r"\bv\b", "val", s)
    s = _re.sub(r"\bk\b", "key", s)
    s = _re.sub(r"\bo\b", "out", s)
    return s

def main():
    only = sys.argv[1:] or None
    for (name, op, stages, psk, desc) in SPECS:
        if only and name not in only:
            continue
        cdir = os.path.join(FB, name)
        os.makedirs(cdir, exist_ok=True)
        model_src = gen_model(name, op, stages, psk, desc)
        with open(os.path.join(cdir, "model.py"), "w") as f:
            f.write(model_src)
        with open(os.path.join(cdir, "impl.c"), "w") as f:
            f.write(gen_impl(name, op, stages, psk, desc))
        with open(os.path.join(cdir, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, op, stages, psk, desc))
        # meta.json with goldens from the model
        sys.path.insert(0, cdir)
        import importlib.util
        for mod in list(sys.modules):
            if mod.startswith("model_"):
                del sys.modules[mod]
        spec = importlib.util.spec_from_file_location("model_" + name, os.path.join(cdir, "model.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        g1 = m.mix(0x0, 0x123456789ABCDEF0)
        g2 = m.mix(0x123456789ABCDEF0, 0x0)
        meta = {
            "name": name, "description": desc,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": [
                {"val": "0x0", "key": "0x123456789abcdef0", "out": hex(g1)},
                {"val": "0x123456789abcdef0", "key": "0x0", "out": hex(g2)},
            ],
        }
        with open(os.path.join(cdir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        sys.path.remove(cdir)
        print(f"generated {name}")
    print("done")

if __name__ == "__main__":
    main()
