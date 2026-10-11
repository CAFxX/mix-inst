#!/usr/bin/env python3
"""Rewrite the 15 broad S-box model.py files as self-contained (no VM paths)."""
import importlib.util
import json
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
CAND_DIR = os.path.expanduser(
    "~/workspace/fanout/projects/mix-sbox-search/battery/candidates")
RANKED = os.path.join(R25, "sbox_screen_broad", "ranked.json")

PBOX = [(19 * i + 1) % 64 for i in range(64)]
RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
      0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054]


def make_model(name, sbox):
    lines = []
    lines.append('"""Self-contained numpy model for %s (no VM paths).' % name)
    lines.append('')
    lines.append('Construction:')
    lines.append('  SBOX = %s (per nibble)' % (sbox,))
    lines.append('  P(i) = (19*i+1) mod 64   (out[P[i]] = in[i])')
    lines.append('  LIN(x) = x ^ rotl64(x,5) ^ rotl64(x,13)')
    lines.append('  round i (0-based): x = LIN(P(SBOX(x ^ rk_i)))')
    lines.append('  rk_i = rotl64(key, 13*(i+1)) ^ RC[i]')
    lines.append('"""')
    lines.append('import numpy as np')
    lines.append('')
    lines.append('SBOX = np.array(%s, dtype=np.uint64)' % (sbox,))
    lines.append('PBOX = np.array(%s, dtype=np.uint64)' % (PBOX,))
    lines.append('RC = np.array(%s, dtype=np.uint64)' % (RC,))
    lines.append('M64 = np.uint64(0xFFFFFFFFFFFFFFFF)')
    lines.append('ROUNDS = 4')
    lines.append('ROTA = 5')
    lines.append('ROTB = 13')
    lines.append('')
    lines.append('def _rotl(x, r):')
    lines.append('    r %= 64')
    lines.append('    if r == 0:')
    lines.append('        return x')
    lines.append('    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64')
    lines.append('')
    lines.append('def _sbox64(x):')
    lines.append('    y = np.zeros_like(x)')
    lines.append('    for i in range(16):')
    lines.append('        y |= SBOX[((x >> np.uint64(4 * i)) & np.uint64(0xF))] \\')
    lines.append('            << np.uint64(4 * i)')
    lines.append('    return y & M64')
    lines.append('')
    lines.append('def _pbox64(x):')
    lines.append('    y = np.zeros_like(x)')
    lines.append('    for i in range(64):')
    lines.append('        y |= ((x >> np.uint64(i)) & np.uint64(1)) << PBOX[i]')
    lines.append('    return y & M64')
    lines.append('')
    lines.append('def _lin(x):')
    lines.append('    return (x ^ _rotl(x, ROTA) ^ _rotl(x, ROTB)) & M64')
    lines.append('')
    lines.append('def _rk(key, i):')
    lines.append('    return _rotl(key, 13 * (i + 1)) ^ RC[i]')
    lines.append('')
    lines.append('def mix(v, k):')
    lines.append('    v = np.uint64(v)')
    lines.append('    k = np.uint64(k)')
    lines.append('    x = v')
    lines.append('    for i in range(ROUNDS):')
    lines.append('        x = _lin(_pbox64(_sbox64(x ^ _rk(k, i))))')
    lines.append('    return int(x & M64)')
    lines.append('')
    lines.append('def mix_np(v, k):')
    lines.append('    v = np.asarray(v, dtype=np.uint64)')
    lines.append('    k = np.uint64(k)')
    lines.append('    x = v.copy()')
    lines.append('    for i in range(ROUNDS):')
    lines.append('        x = _lin(_pbox64(_sbox64(x ^ _rk(k, i))))')
    lines.append('    return x & M64')
    lines.append('')
    lines.append('mix64 = mix_np')
    lines.append('')
    return "\n".join(lines)


def main():
    ranked = json.load(open(RANKED))
    boxes = {b["name"]: b["table"] for b in ranked["all"] if "table" in b}

    for name, table_hex in boxes.items():
        sbox = [int(c, 16) for c in table_hex.strip()]
        cand_name = "r25_spn_pba19_sb_%s_513_nw" % name
        d = os.path.join(CAND_DIR, cand_name)
        if not os.path.isdir(d):
            print("SKIP (no dir): %s" % cand_name)
            continue
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(make_model(cand_name, sbox))
        print("Rewrote %s/model.py" % cand_name)

    # Verify midori_sb0
    mp = os.path.join(CAND_DIR,
                      "r25_spn_pba19_sb_lit_midori_sb0_513_nw/model.py")
    spec = importlib.util.spec_from_file_location("test_model", mp)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    meta = json.load(open(os.path.join(
        CAND_DIR, "r25_spn_pba19_sb_lit_midori_sb0_513_nw/meta.json")))
    for g in meta["goldens"]:
        out = m.mix(int(g["val"], 16), int(g["key"], 16))
        assert hex(out) == g["out"], "MISMATCH %s != %s" % (hex(out), g["out"])
    print("Self-contained model goldens OK")


if __name__ == "__main__":
    main()
