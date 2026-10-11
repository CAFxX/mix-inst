"""Model-vs-RTL equivalence check for exploration candidates.
Usage: python3 check_rtl.py <dotted.model.fn> <rtl.v> <top> <workdir> [nvec=200]
Writes vectors.txt from the numpy model, substitutes TOP into the TB
template, compiles with iverilog, runs, and requires RTLCHECK PASS.
"""
import importlib, os, subprocess, sys

MIX = "/home/hatch/workspace/mix"
EXP = os.path.join(MIX, "exploration")


def main():
    dotted, rtl, top, workdir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    nvec = int(sys.argv[5]) if len(sys.argv) > 5 else 64
    workdir = os.path.abspath(workdir)
    os.makedirs(workdir, exist_ok=True)
    sys.path.insert(0, EXP)
    modname, fnname = dotted.rsplit(".", 1)
    fn = getattr(importlib.import_module(modname), fnname)
    import numpy as np
    rng = np.random.default_rng(0xBEEF)
    V = rng.integers(0, 2**64, size=nvec, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=nvec, dtype=np.uint64)
    E = np.asarray(fn(V, K), dtype=np.uint64)
    with open(os.path.join(workdir, "vectors.txt"), "w") as f:
        for i in range(nvec):
            f.write(f"{int(V[i]):016x} {int(K[i]):016x} {int(E[i]):016x}\n")
    tmpl = open(os.path.join(EXP, "tb_check_template.v")).read()
    tb = tmpl.replace("TOP_PLACEHOLDER", top)
    tb_path = os.path.join(workdir, "tb_check.v")
    open(tb_path, "w").write(tb)
    exe = os.path.join(workdir, "tb_check")
    r = subprocess.run(["iverilog", "-o", exe, tb_path, os.path.abspath(rtl)],
                       capture_output=True, text=True, cwd=workdir, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"iverilog failed for {top}:\n{r.stderr[-2000:]}")
    r = subprocess.run(["vvp", exe], capture_output=True, text=True,
                       cwd=workdir, timeout=300)
    out = r.stdout + r.stderr
    print(out.strip().splitlines()[-1] if out.strip() else "(no output)")
    if "RTLCHECK" not in out or "PASS" not in out:
        raise RuntimeError(f"RTL check FAILED for {top}:\n{out[-3000:]}")


if __name__ == "__main__":
    main()
