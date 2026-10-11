#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 11 (wide 4-stage AND-cascade)."""
import inspect, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b11 as M
FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

def rotl(x, r):
    r %= 64
    return x if r == 0 else f"{{{x}[{63-r}:0], {x}[63:{64-r}]}}"

def gen_rtl(name, sched):
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] x0 = val ^ key;"]
    cur = "x0"
    for i, (a,b,c,d,e) in enumerate(sched):
        ra,rb,rc,rd,re = rotl(cur,a),rotl(cur,b),rotl(cur,c),rotl(cur,d),rotl(cur,e)
        L.append(f"  wire [63:0] x{i+1} = {cur} ^ ({ra} & {rb}) ^ ({rc} & {rd}) ^ {re};")
        cur = f"x{i+1}"
    L.append(f"  assign out = {cur} ^ {rotl('key',13)};")
    L.append("endmodule")
    return "\n".join(L)

def gen_c(name, desc, sched):
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}",
         f"// {name}: {desc}", "uint64_t mix_hash(uint64_t val,uint64_t key){",
         "    uint64_t x = val ^ key;"]
    for (a,b,c,d,e) in sched:
        L.append(f"    x ^= (rotl64(x,{a})&rotl64(x,{b}))^(rotl64(x,{c})&rotl64(x,{d}))^rotl64(x,{e});")
    L.append("    x ^= rotl64(key,13);")
    L.append("    return x;}")
    return "\n".join(L)+"\n"

BUNDLES = {"t6_wide4a": M.SCHED_WA, "t6_wide4b": M.SCHED_WB}

def sc_model(name, desc, sched):
    p = [f'"""Model {name} (batch 11)."""',"import numpy as np","","M64 = np.uint64(0xFFFFFFFFFFFFFFFF)"]
    p.append(inspect.getsource(M._rotl64)); p.append(inspect.getsource(M._wide4_cascade))
    p.append(inspect.getsource(M._vec)); p.append(f"SCHED = {sched!r}")
    p += ["","def _scalar(v,k):","    return _wide4_cascade(v,k,SCHED)","_mix_np=_vec(_scalar)","",
          "def mix(v,k):","    return _scalar(int(v),int(k)) if np.ndim(v)==0 and np.ndim(k)==0 else _mix_np(v,k)",
          "def mix_np(V,K):","    return _mix_np(V,K)",f"meta={{'desc':{desc!r}}}"]
    return "\n".join(p)+"\n"

def main():
    import numpy as np
    for name, sched in BUNDLES.items():
        desc = M.CANDIDATES_B11[name][1]
        d = os.path.join(FB, name); os.makedirs(d, exist_ok=True)
        open(f"{d}/rtl.v","w").write(gen_rtl(name,sched)+"\n")
        open(f"{d}/model.py","w").write(sc_model(name,desc,sched))
        json.dump({"name":name,"rtl_top":name,"description":desc,
                   "screen_keys":["0x123456789abcdef0","0x0"],
                   "practrand_keys":["0x123456789abcdef0","0x0"]},
                  open(f"{d}/meta.json","w"),indent=1)
        open(f"{d}/impl.c","w").write(gen_c(name,desc,sched))
        print(f"{name}: written")
    print("\n=== checks ==="); ok=True; IVL='/home/hatch/tools/ivl-env/bin/iverilog'
    for name, sched in BUNDLES.items():
        d=os.path.join(FB,name); mu=__import__("importlib.util",fromlist=["util"])
        spec=mu.spec_from_file_location("m_"+name,f"{d}/model.py"); m=mu.module_from_spec(spec); spec.loader.exec_module(m)
        ref=M.CANDIDATES_B11[name][0]; rng=np.random.default_rng(42)
        for _ in range(200):
            v=int(rng.integers(0,2**64,dtype=np.uint64)); k=int(rng.integers(0,2**64,dtype=np.uint64))
            if int(m.mix(np.uint64(v),np.uint64(k)))!=int(ref(np.uint64(v),np.uint64(k))): print(f"{name}: MODEL FAIL"); ok=False; break
        else: print(f"{name}: model OK")
        open('/tmp/b11.c','w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r=subprocess.run(["gcc","-O2","-o","/tmp/b11","/tmp/b11.c",f"{d}/impl.c"],capture_output=True,text=True)
        if r.returncode!=0: print(f"{name}: GCC FAIL"); ok=False; continue
        vecs=[(int(rng.integers(0,2**64,dtype=np.uint64)),int(rng.integers(0,2**64,dtype=np.uint64))) for _ in range(200)]
        r=subprocess.run(["/tmp/b11"],input="\n".join(f"{v:x} {k:x}" for v,k in vecs),capture_output=True,text=True)
        for (v,k),o in zip(vecs,r.stdout.strip().split("\n")):
            if int(o,16)!=int(ref(np.uint64(v),np.uint64(k))): print(f"{name}: C FAIL"); ok=False; break
        else: print(f"{name}: impl.c OK")
        fn=ref; vecs=[(int(rng.integers(0,2**64,dtype=np.uint64)),int(rng.integers(0,2**64,dtype=np.uint64))) for _ in range(20)]
        tb=['`timescale 1ns/1ps','module tb;','  reg [63:0] val,key;','  wire [63:0] out;',f'  {name} dut(.val(val),.key(key),.out(out));','  initial begin']
        for v,k in vecs:
            e=int(fn(np.uint64(v),np.uint64(k))); tb.append(f"    val=64'h{v:016x};key=64'h{k:016x};#10;"); tb.append(f'    if(out!==64\'h{e:016x})$display("MISMATCH");')
        tb+=['    $display("TB DONE");','    $finish;','  end','endmodule']
        open('/tmp/b11tb.v','w').write('\n'.join(tb))
        r=subprocess.run([IVL,'-o','/tmp/b11tb',f'{d}/rtl.v','/tmp/b11tb.v'],capture_output=True,text=True)
        if r.returncode!=0: print(f"{name}: IVL FAIL"); ok=False; continue
        r=subprocess.run(['/tmp/b11tb'],capture_output=True,text=True,timeout=60)
        good="TB DONE" in r.stdout and "MISMATCH" not in r.stdout
        print(f"{name}: RTL {'OK' if good else 'FAIL'}")
        if not good: ok=False
    print("ALL OK" if ok else "FAILURES"); return 0 if ok else 1
if __name__=="__main__": sys.exit(main())
