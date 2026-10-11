#!/usr/bin/env python3
"""Create minimal fast_battery candidate bundle from a Python model.
Usage: mk_candidate.py <name> <model_py_path> <description>
Creates: candidates/<name>/{model.py, meta.json, impl.c (stub), rtl.v (stub)}
Note: impl.c and rtl.v are stubs; S0 requires real RTL (generate separately).
For S1/S2 (Python-only), the stubs are fine.
"""
import json, os, sys, shutil

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

def main():
    name, model_src, desc = sys.argv[1], sys.argv[2], sys.argv[3]
    cdir = os.path.join(FB, name)
    os.makedirs(cdir, exist_ok=True)
    
    # Copy model.py
    shutil.copy(model_src, os.path.join(cdir, "model.py"))
    
    # Minimal meta.json (goldens computed from model)
    sys.path.insert(0, os.path.dirname(model_src))
    import importlib.util
    spec = importlib.util.spec_from_file_location("m", os.path.join(cdir, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    
    g1 = m.mix(0x0, 0x123456789ABCDEF0)
    g2 = m.mix(0x123456789ABCDEF0, 0x0)
    
    meta = {
        "name": name,
        "description": desc,
        "screen_keys": ["0x123456789abcdef0", "0x0"],
        "practrand_keys": ["0x123456789abcdef0", "0x0"],
        "rtl_top": name,  # REQUIRED: s0_delay.py reads meta["rtl_top"]; bundles without it S0 INFRA_FAIL (dd7 batch-7 incident, run 37942134112, 2026-10-09)
        "goldens": [
            {"val": "0x0", "key": "0x123456789abcdef0", "out": hex(g1)},
            {"val": "0x123456789abcdef0", "key": "0x0", "out": hex(g2)},
        ],
    }
    with open(os.path.join(cdir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    
    # Stub impl.c and rtl.v (for S1/S2 Python-only testing)
    with open(os.path.join(cdir, "impl.c"), "w") as f:
        f.write("// Stub - real impl needed for S3/S4\n")
        f.write("#include <stdint.h>\nuint64_t mix_hash(uint64_t v, uint64_t k) { return 0; }\n")
    with open(os.path.join(cdir, "rtl.v"), "w") as f:
        f.write(f"// Stub - real RTL needed for S0\nmodule {name}(input [63:0] v, input [63:0] k, output [63:0] o);\nassign o = 64'h0;\nendmodule\n")
    
    print(f"Created {cdir}")

if __name__ == "__main__":
    main()
