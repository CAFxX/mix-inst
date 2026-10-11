import importlib.util
import os
import subprocess
import random

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
WD = "/home/hatch/workspace/mix/exploration/new_constructions/b33_verify"
os.makedirs(WD, exist_ok=True)
random.seed(11)
drv = ('#include <stdio.h>\n#include <stdint.h>\n'
       'uint64_t mix_hash(uint64_t,uint64_t);\n'
       'int main(void){uint64_t v,k;'
       'while(scanf("%llx %llx",(unsigned long long*)&v,(unsigned long long*)&k)==2)'
       'printf("%016llx\\n",(unsigned long long)mix_hash(v,k));return 0;}\n')
open(os.path.join(WD, "drv.c"), "w").write(drv)
for name in ["t6_b33a", "t6_b33b", "t6_b33c", "t6_b33d", "t6_b33e", "t6_b33f", "t6_b33g"]:
    d = os.path.join(FB, name)
    spec = importlib.util.spec_from_file_location("m_" + name, os.path.join(d, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    vecs = [(random.getrandbits(64), random.getrandbits(64)) for _ in range(300)]
    py = [m.mix(v, k) for v, k in vecs]
    binp = os.path.join(WD, "drv_" + name)
    subprocess.run(["gcc", "-O2", "-o", binp, os.path.join(WD, "drv.c"),
                    os.path.join(d, "impl.c")], check=True)
    inp = "".join("%016x %016x\n" % (v, k) for v, k in vecs)
    c = subprocess.run([binp], input=inp.encode(), capture_output=True).stdout.decode().split()
    ok = all(int(x, 16) == p for x, p in zip(c, py))
    print(name, "bit-exact 300/300" if ok else "MISMATCH", flush=True)
