import importlib.util, os, subprocess, random
FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
WD = "/home/hatch/workspace/mix/exploration/hybrid/batch21/b21b_verify"
os.makedirs(WD, exist_ok=True)
random.seed(0xB21B)
drv = ('#include <stdio.h>\n#include <stdint.h>\n'
       'uint64_t mix_hash(uint64_t,uint64_t);\n'
       'int main(void){uint64_t v,k;'
       'while(scanf("%llx %llx",(unsigned long long*)&v,(unsigned long long*)&k)==2)'
       'printf("%016llx\\n",(unsigned long long)mix_hash(v,k));return 0;}\n')
open(os.path.join(WD, "drv.c"), "w").write(drv)
allok = True
for name in ["hyb21_fat5a", "hyb21_fat5b", "hyb21_fat5c"]:
    d = os.path.join(FB, name)
    spec = importlib.util.spec_from_file_location("m_" + name, os.path.join(d, "model.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    vecs = [(random.getrandbits(64), random.getrandbits(64)) for _ in range(300)]
    # check mix_np vectorized matches scalar mix too (battery interface)
    import numpy as np
    V = np.array([v for v, k in vecs], dtype=np.uint64); K = np.array([k for v, k in vecs], dtype=np.uint64)
    assert all(int(x) == mm for x, mm in zip(m.mix_np(V, K), [m.mix(v, k) for v, k in vecs])), "mix_np != mix"
    py = [m.mix(v, k) for v, k in vecs]
    binp = os.path.join(WD, "drv_" + name)
    subprocess.run(["gcc", "-O2", "-o", binp, os.path.join(WD, "drv.c"), os.path.join(d, "impl.c")], check=True)
    inp = "".join("%016x %016x\n" % (v, k) for v, k in vecs)
    c = subprocess.run([binp], input=inp.encode(), capture_output=True).stdout.decode().split()
    ok = all(int(x, 16) == p for x, p in zip(c, py))
    print(name, "bit-exact 300/300 (mix==mix_np OK)" if ok else "MISMATCH", flush=True)
    allok &= ok
print("ALL OK" if allok else "FAILURES PRESENT")
