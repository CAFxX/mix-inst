#!/usr/bin/env python3
"""Minimal Verilog generator for SPN candidates (S0 delay testing).

Construction (4-round keyed SPN):
  Round i: x = LIN(P(SBOX(x ^ rk_i)))
  LIN(x) = x ^ rotl64(x,a) ^ rotl64(x,b)
  P(i) = (19*i+1) % 64  (pba19)
  SBOX = rasC2_0 (or specified)
  rk_i = rotl64(key, 13*(i+1)) ^ RC[i]
"""
import json

SBOX_RASC2_0 = [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14]
RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
      0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054,
      0x2545F4914F6CDD1D, 0x94D049BB133111EB]  # spare entries for 5r/6r

def resolve_ks(ks, nrounds):
    """Resolve the key-schedule spec to (rot_steps, rc_list).

    ks forms:
      None or "golden"              -> rotl64(key,13*(i+1)) ^ RC_GOLDEN[i]
      "norc"                        -> rotl64(key,13*(i+1)) (no constants)
      {"rot_step": s, "rc": ...}    -> s int, or [s1,s2] for a folded
                                       rotl(key,s1*(i+1))^rotl(key,s2*(i+1))
      rc: "golden" | "zero" | [c0..c_{n-1}]
    """
    if ks is None or ks == "golden":
        return [13], list(RC[:nrounds])
    if ks == "norc":
        return [13], [0] * nrounds
    assert isinstance(ks, dict), f"ks must be None/str/dict, got {ks!r}"
    rs = ks.get("rot_step", 13)
    rot_steps = list(rs) if isinstance(rs, (list, tuple)) else [rs]
    rc = ks.get("rc", "golden")
    if rc == "golden":
        rc_list = list(RC[:nrounds])
    elif rc == "zero":
        rc_list = [0] * nrounds
    else:
        rc_list = list(rc[:nrounds])
    assert len(rc_list) >= nrounds, f"ks rc too short for {nrounds} rounds"
    return rot_steps, rc_list

def rotl_expr(sig, r, width=64):
    """Verilog expression for rotate-left."""
    r = r % width
    if r == 0:
        return sig
    return f"({{{sig}[{width-1-r}:0], {sig}[{width-1}:{width-r}]}})"


def shift_expr(sig, n, kind, width=64):
    """Verilog expression for logical shift (free wiring, zero-fill)."""
    n = n % width
    if n == 0:
        return sig
    if kind == "shl":
        return f"({{{sig}[{width-1-n}:0], {{{n}{{1'b0}}}}}})"
    if kind == "shr":
        return f"({{{{{n}{{1'b0}}}}, {sig}[{width-1}:{n}]}})"
    raise ValueError(f"unknown shift kind {kind!r}")


def resolve_lin_terms(spec):
    """[(kind, n), ...] for the LIN layer. 'lin_terms' wins; legacy 'rots'
    is interpreted as a rotation pair (D10 batch-13 axis-1 extension)."""
    lt = spec.get("lin_terms")
    if lt is not None:
        terms = [(str(k), int(n)) for k, n in lt]
    else:
        terms = [("rotl", int(v)) for v in spec["rots"]]
    for kind, n in terms:
        assert kind in ("rotl", "shl", "shr"), f"bad lin term {kind!r}"
        assert 0 <= n < 64, f"bad lin amount {n!r}"
    assert 1 <= len(terms) <= 3, f"lin_terms len {len(terms)}"
    return terms


def lin_term_expr(sig, kind, n):
    if kind == "rotl":
        return rotl_expr(sig, n)
    return shift_expr(sig, n, kind)

def sbox_expr(x_sig, sbox, out_sig):
    """Generate assign statements for 4-bit S-box applied to 16 nibbles."""
    lines = []
    for nib in range(16):
        lo = nib * 4
        hi = lo + 3
        # Case statement for this nibble
        lines.append(f"  case ({x_sig}[{hi}:{lo}])")
        for vin in range(16):
            vout = sbox[vin]
            lines.append(f"    4'h{vin:x}: {out_sig}[{hi}:{lo}] = 4'h{vout:x};")
        lines.append(f"  endcase")
    return "\n".join(lines)

def pbox_expr(x_sig, out_sig):
    """P-box: out[(19*i+1)%64] = in[i]"""
    lines = []
    for i in range(64):
        j = (19 * i + 1) % 64
        lines.append(f"  assign {out_sig}[{j}] = {x_sig}[{i}];")
    return "\n".join(lines)

def gen_spn_verilog(name, sbox, rots_a, rots_b, nrounds=4, pbox=None, sbox_rounds=None, ks=None, rots_rounds=None):
    """Generate Verilog for SPN with given rotation pair, P-box, and S-boxes.

    pbox: list of 64 ints, pbox[i] = output position for input bit i.
          If None, uses P(i) = (19*i+1) % 64.
    sbox: 16-list (homogeneous) or list of 16-lists per round (heterogeneous).
          If sbox_rounds is provided, it takes precedence.
    sbox_rounds: list of nrounds 16-lists, one S-box per round.
    rots_rounds: list of nrounds (a,b) pairs, one LIN rotation pair per round.
          If provided, takes precedence over (rots_a, rots_b).
    ks: key-schedule spec, see resolve_ks(). None/"golden" = historical default.
    """
    if pbox is None:
        pbox = [(19*i+1) % 64 for i in range(64)]
    # Normalize sbox to per-round list
    if sbox_rounds is not None:
        sbox_per_round = sbox_rounds
    elif isinstance(sbox[0], (list, tuple)):
        sbox_per_round = sbox
    else:
        sbox_per_round = [sbox] * nrounds
    # Normalize rots to per-round list
    if rots_rounds is not None:
        assert len(rots_rounds) == nrounds, f"rots_rounds len {len(rots_rounds)} != nrounds {nrounds}"
        rots_per_round = [(int(a), int(b)) for a, b in rots_rounds]
        lin_desc = "vlin" + str(rots_per_round)
    else:
        rots_per_round = [(rots_a, rots_b)] * nrounds
        lin_desc = f"lin({rots_a},{rots_b})"
    lines = []
    lines.append(f"// {name}: {nrounds}r SPN, rasC2_0, pba19, LIN={lin_desc}")
    lines.append(f"// GENERATED by directed_design/gen_verilog.py")
    lines.append(f"module {name}(")
    lines.append(f"  input [63:0] val,")
    lines.append(f"  input [63:0] key,")
    lines.append(f"  output [63:0] out")
    lines.append(f");")
    lines.append(f"")
    
    # Round keys (parameterized key schedule)
    rot_steps, rc_list = resolve_ks(ks, nrounds)
    ks_desc = "+".join(f"rotl(key,{s}*(i+1))" for s in rot_steps)
    lines.append(f"  // Key schedule: rk_i = {' ^ '.join([ks_desc, 'RC[i]'])}")
    for i in range(nrounds):
        parts = [rotl_expr('key', s * (i + 1)) for s in rot_steps]
        rc = rc_list[i]
        if rc:
            parts.append(f"64'h{rc:016x}")
        # dedupe identical terms (e.g. rot_step 0 twice, or rotl by 0 == key)
        seen, uniq = set(), []
        for p in parts:
            if p not in seen:
                seen.add(p); uniq.append(p)
        lines.append(f"  wire [63:0] rk{i} = {' ^ '.join(uniq)};")
    lines.append(f"")
    
    # Round logic
    prev = "val"
    for r in range(nrounds):
        sbox_r = sbox_per_round[r]
        x_xor = f"x{r}_xor"
        x_sbox = f"x{r}_sbox"
        x_pbox = f"x{r}_pbox"
        x_lin = f"x{r+1}" if r < nrounds - 1 else "out_internal"
        
        lines.append(f"  // Round {r}")
        lines.append(f"  wire [63:0] {x_xor} = {prev} ^ rk{r};")
        lines.append(f"")
        
        # S-box (combinational via case)
        lines.append(f"  reg [63:0] {x_sbox}_r;")
        lines.append(f"  always @(*) begin")
        # Initialize to avoid latches
        lines.append(f"    {x_sbox}_r = 64'h0;")
        for nib in range(16):
            lo = nib * 4
            hi = lo + 3
            lines.append(f"    case ({x_xor}[{hi}:{lo}])")
            for vin in range(16):
                vout = sbox_r[vin]
                lines.append(f"      4'h{vin:x}: {x_sbox}_r[{hi}:{lo}] = 4'h{vout:x};")
            lines.append(f"    endcase")
        lines.append(f"  end")
        lines.append(f"  wire [63:0] {x_sbox} = {x_sbox}_r;")
        lines.append(f"")
        
        # P-box
        lines.append(f"  wire [63:0] {x_pbox};")
        for i in range(64):
            j = pbox[i]
            lines.append(f"  assign {x_pbox}[{j}] = {x_sbox}[{i}];")
        lines.append(f"")
        
        # Linear layer (per-round rotations)
        a_r, b_r = rots_per_round[r]
        a_expr = rotl_expr(x_pbox, a_r)
        b_expr = rotl_expr(x_pbox, b_r)
        lines.append(f"  wire [63:0] {x_lin} = {x_pbox} ^ {a_expr} ^ {b_expr};")
        lines.append(f"")
        
        prev = x_lin
    
    lines.append(f"  assign out = out_internal;")
    lines.append(f"")
    lines.append(f"endmodule")
    
    return "\n".join(lines)

def chi_expr(x_sig, triple, flavor):
    """Verilog expression for a full-width chi/AND-cascade layer.

    flavor "and":    x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)   (al_and6a style)
    flavor "keccak": x ^ (rotl(x,a) & ~rotl(x,b)) ^ rotl(x,c)  (Keccak-chi style)
    """
    a, b, c = (int(v) for v in triple)
    ra = rotl_expr(x_sig, a)
    rb = rotl_expr(x_sig, b)
    rc = rotl_expr(x_sig, c)
    if flavor == "and":
        return f"{x_sig} ^ (({ra}) & ({rb})) ^ ({rc})"
    if flavor == "keccak":
        return f"{x_sig} ^ (({ra}) & ~({rb})) ^ ({rc})"
    raise ValueError(f"unknown chi flavor {flavor!r}")


def gen_mixed_verilog(spec):
    """Generate Verilog for a mixed-function-type candidate (batch-9+).

    spec fields:
      name, nrounds,
      layers: list of nrounds dicts:
        {"type": "sbox", "sbox": <16-list>}  (inline table; gen_batch9 resolves names)
        {"type": "chi", "chi": [a,b,c], "flavor": "and"|"keccak"}
      pbox: 64-list permutation
      rots: [a,b] LIN rotation pair, or [a] for single-rotation LIN
            x ^ rotl64(x,a) (used where lin enabled)
      lin: "all" | "sbox" | "chi" | "none" — which layer types get LIN after P-box
      ks: key-schedule spec (see resolve_ks)
    Round i: x = LIN?(P(NL_i(x ^ rk_i)))
    """
    name = spec["name"]
    nrounds = spec["nrounds"]
    layers = spec["layers"]
    assert len(layers) == nrounds, f"layers len {len(layers)} != nrounds {nrounds}"
    pbox = spec["pbox"]
    assert len(pbox) == 64 and sorted(pbox) == list(range(64)), "pbox must be a permutation"
    terms = resolve_lin_terms(spec)
    lin_mode = spec.get("lin", "all")
    assert lin_mode in ("all", "sbox", "chi", "none"), f"bad lin mode {lin_mode!r}"

    lines = []
    pat = "".join("S" if L["type"] == "sbox" else "C" for L in layers)
    lin_desc = " ^ ".join(["x"] + [f"{k}{n}" for k, n in terms])
    lines.append(f"// {name}: {nrounds}r mixed NL ({pat}), pba19, LIN={lin_desc} mode={lin_mode}")
    lines.append(f"// GENERATED by directed_design/gen_verilog.py (gen_mixed_verilog)")
    lines.append(f"module {name}(")
    lines.append(f"  input [63:0] val,")
    lines.append(f"  input [63:0] key,")
    lines.append(f"  output [63:0] out")
    lines.append(f");")
    lines.append(f"")

    rot_steps, rc_list = resolve_ks(spec.get("ks"), nrounds)
    ks_desc = "+".join(f"rotl(key,{s}*(i+1))" for s in rot_steps)
    lines.append(f"  // Key schedule: rk_i = {' ^ '.join([ks_desc, 'RC[i]'])}")
    for i in range(nrounds):
        parts = [rotl_expr('key', s * (i + 1)) for s in rot_steps]
        rc = rc_list[i]
        if rc:
            parts.append(f"64'h{rc:016x}")
        seen, uniq = set(), []
        for p in parts:
            if p not in seen:
                seen.add(p); uniq.append(p)
        lines.append(f"  wire [63:0] rk{i} = {' ^ '.join(uniq)};")
    lines.append(f"")

    prev = "val"
    for r in range(nrounds):
        L = layers[r]
        ltype = L["type"]
        x_xor = f"x{r}_xor"
        x_nl = f"x{r}_nl"
        x_pbox = f"x{r}_pbox"
        x_lin = f"x{r+1}" if r < nrounds - 1 else "out_internal"

        lines.append(f"  // Round {r} ({ltype})")
        lines.append(f"  wire [63:0] {x_xor} = {prev} ^ rk{r};")
        lines.append(f"")

        if ltype == "sbox":
            sb = L["sbox"]
            assert len(sb) == 16
            lines.append(f"  reg [63:0] {x_nl}_r;")
            lines.append(f"  always @(*) begin")
            lines.append(f"    {x_nl}_r = 64'h0;")
            for nib in range(16):
                lo = nib * 4
                hi = lo + 3
                lines.append(f"    case ({x_xor}[{hi}:{lo}])")
                for vin in range(16):
                    vout = sb[vin]
                    lines.append(f"      4'h{vin:x}: {x_nl}_r[{hi}:{lo}] = 4'h{vout:x};")
                lines.append(f"    endcase")
            lines.append(f"  end")
            lines.append(f"  wire [63:0] {x_nl} = {x_nl}_r;")
        elif ltype == "chi":
            lines.append(f"  wire [63:0] {x_nl} = {chi_expr(x_xor, L['chi'], L['flavor'])};")
        else:
            raise ValueError(f"unknown layer type {ltype!r}")
        lines.append(f"")

        lines.append(f"  wire [63:0] {x_pbox};")
        for i in range(64):
            j = pbox[i]
            lines.append(f"  assign {x_pbox}[{j}] = {x_nl}[{i}];")
        lines.append(f"")

        do_lin = (lin_mode == "all"
                  or (lin_mode == "sbox" and ltype == "sbox")
                  or (lin_mode == "chi" and ltype == "chi"))
        if do_lin:
            term_exprs = [x_pbox] + [lin_term_expr(x_pbox, k, n)
                                    for k, n in terms]
            lines.append(f"  wire [63:0] {x_lin} = {' ^ '.join(term_exprs)};")
        else:
            lines.append(f"  wire [63:0] {x_lin} = {x_pbox};")
        lines.append(f"")

        prev = x_lin

    lines.append(f"  assign out = out_internal;")
    lines.append(f"")
    lines.append(f"endmodule")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    specs = json.load(open(sys.argv[1]))
    outdir = sys.argv[2]
    import os
    os.makedirs(outdir, exist_ok=True)
    for s in specs:
        if "layers" in s:
            # mixed-function-type spec (batch-9+): layers list drives generation
            v = gen_mixed_verilog(s)
            with open(os.path.join(outdir, s["name"] + ".v"), "w") as f:
                f.write(v)
            print(f"Generated {s['name']}.v (mixed)")
            continue
        rr = s["rots"]
        if isinstance(rr[0], (list, tuple)):
            # per-round LIN: rots = [[a0,b0],[a1,b1],...]
            rots_rounds = [list(p) for p in rr]
            a, b = rots_rounds[0][0], rots_rounds[0][1]
        else:
            rots_rounds = None
            a, b = rr[0], rr[1]
        v = gen_spn_verilog(s["name"], s["sbox"], a, b, s["nrounds"],
                            pbox=s.get("pbox"),
                            sbox_rounds=s.get("sbox_rounds"),
                            ks=s.get("ks"),
                            rots_rounds=rots_rounds)
        with open(os.path.join(outdir, s["name"] + ".v"), "w") as f:
            f.write(v)
        print(f"Generated {s['name']}.v")
