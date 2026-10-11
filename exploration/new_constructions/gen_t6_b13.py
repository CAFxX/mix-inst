#!/usr/bin/env python3
"""Generate batch 13 (5-stage AND + per-stage rk)."""
import inspect, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b13 as M
FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
def rotl(x,r):
    r%=64; return x if r==0 else f"{{{x}[{63-r}:0],{x}[63:{64-r}]}}"
RC_HEX=["64'h9e3779b97f4a7c15","64'h3c6ef372fe94f82a","64'hdaa66d2c7ddf743f","64'h78dde6e5fd29f054","64'h2545f4914f6cdd1d"]
def gen_rtl(name,stages):
    L=[f"module {name}(input [63:0] val,input [63:0] key,output [63:0] out);","  wire [63:0] x0=val^key;"]
    cur="x0"
    for i,(a,b,c) in enumerate(stages):
        rk=f"({rotl('key',13*(i+1))} ^ {RC_HEX[i%5]})"
        L.append(f"  wire [63:0] x{i+1}={cur}^({rotl(cur,a)}&{rotl(cur,b)})^{rotl(cur,c)}^{rk};")
        cur=f"x{i+1}"
    L.append(f"  wire [63:0] kr13={rotl('key',13)};")
    L.append(f"  assign out={cur}^{{32'h0,kr13[63:32]}};")
    L.append("endmodule")
    return "\n".join(L)
def gen_c(name,desc,stages):
    L=["#include <stdint.h>","static inline uint64_t r64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}",
       f"// {name}: {desc}","uint64_t mix_hash(uint64_t v,uint64_t k){",
       "    static const uint64_t RC[5]={0x9E3779B97F4A7C15ull,0x3C6EF372FE94F82Aull,0xDAA66D2C7DDF743Full,0x78DDE6E5FD29F054ull,0x2545F4914F6CDD1Dull};",
       "    uint64_t x=v^k;"]
    for i,(a,b,c) in enumerate(stages):
        L.append(f"    x^=(r64(x,{a})&r64(x,{b}))^r64(x,{c})^(r64(k,{13*(i+1)})^RC[{i%5}]);")
    L.append("    x^=r64(k,13)>>32;")
    L.append("    return x;}")
    return "\n".join(L)+"\n"
BUNDLES={"t6_and5ka":M.STAGES_A,"t6_and5kb":M.STAGES_B}
def sc(name,desc,stages):
    p=[f'"""Model {name}."""',"import numpy as np","","M64=np.uint64(0xFFFFFFFFFFFFFFFF)",
       "RC64=[np.uint64(0x9E3779B97F4A7C15),np.uint64(0x3C6EF372FE94F82A),np.uint64(0xDAA66D2C7DDF743F),np.uint64(0x78DDE6E5FD29F054),np.uint64(0x2545F4914F6CDD1D)]"]
    p.append(inspect.getsource(M._rotl64)); p.append(inspect.getsource(M._and5k_cascade)); p.append(inspect.getsource(M._vec))
    p.append(f"STAGES={stages!r}")
    p+=["","def _s(v,k):","    return _and5k_cascade(v,k,STAGES)","_mn=_vec(_s)","",
        "def mix(v,k):","    return _s(int(v),int(k)) if np.ndim(v)==0 and np.ndim(k)==0 else _mn(v,k)",
        "def mix_np(V,K):","    return _mn(V,K)",f"meta={{'desc':{desc!r}}}"]
    return "\n".join(p)+"\n"
def main():
    import numpy as np
    for name,stages in BUNDLES.items():
        desc=M.CANDIDATES_B13[name][1]; d=os.path.join(FB,name); os.makedirs(d,exist_ok=True)
        open(f"{d}/rtl.v","w").write(gen_rtl(name,stages)+"\n")
        open(f"{d}/model.py","w").write(sc(name,desc,stages))
        json.dump({"name":name,"rtl_top":name,"description":desc,"screen_keys":["0x123456789abcdef0","0x0"],"practrand_keys":["0x123456789abcdef0","0x0"]},open(f"{d}/meta.json","w"),indent=1)
        open(f"{d}/impl.c","w").write(gen_c(name,desc,stages))
        print(f"{name}: written")
    print("=== checks ==="); ok=True; IVL='/home/hatch/tools/ivl-env/bin/iverilog'
    for name,stages in BUNDLES.items():
        d=os.path.join(FB,name); mu=__import__("importlib.util",fromlist=["util"])
        sp=mu.spec_from_file_location("m_"+name,f"{d}/model.py"); m=mu.module_from_spec(sp); sp.loader.exec_module(m)
        ref=M.CANDIDATES_B13[name][0]; rng=np.random.default_rng(42)
        for _ in range(200):
            v=int(rng.integers(0,2**64,dtype=np.uint64)); k=int(rng.integers(0,2**64,dtype=np.uint64))
            if int(m.mix(np.uint64(v),np.uint64(k)))!=int(ref(np.uint64(v),np.uint64(k))): print(f"{name}: MODEL FAIL"); ok=False; break
        else: print(f"{name}: model OK")
        open('/tmp/b13.c','w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r=subprocess.run(["gcc","-O2","-o","/tmp/b13","/tmp/b13.c",f"{d}/impl.c"],capture_output=True,text=True)
        if r.returncode!=0: print(f"{name}: GCC FAIL"); ok=False; continue
        vecs=[(int(rng.integers(0,2**64,dtype=np.uint64)),int(rng.integers(0,2**64,dtype=np.uint64))) for _ in range(200)]
        r=subprocess.run(["/tmp/b13"],input="\n".join(f"{v:x} {k:x}" for v,k in vecs),capture_output=True,text=True)
        for (v,k),o in zip(vecs,r.stdout.strip().split("\n")):
            if int(o,16)!=int(ref(np.uint64(v),np.uint64(k))): print(f"{name}: C FAIL"); ok=False; break
        else: print(f"{name}: impl.c OK")
        fn=ref; vecs=[(int(rng.integers(0,2**64,dtype=np.uint64)),int(rng.integers(0,2**64,dtype=np.uint64))) for _ in range(20)]
        tb=['`timescale 1ns/1ps','module tb;','  reg [63:0] val,key;','  wire [63:0] out;',f'  {name} dut(.val(val),.key(key),.out(out));','  initial begin']
        for v,k in vecs:
            e=int(fn(np.uint64(v),np.uint64(k))); tb.append(f"    val=64'h{v:016x};key=64'h{k:016x};#10;"); tb.append(f'    if(out!==64\'h{e:016x})$display("MISMATCH");')
        tb+=['    $display("TB DONE");','    $finish;','  end','endmodule']
        open('/tmp/b13tb.v','w').write('\n'.join(tb))
        r=subprocess.run([IVL,'-o','/tmp/b13tb',f'{d}/rtl.v','/tmp/b13tb.v'],capture_output=True,text=True)
        if r.returncode!=0: print(f"{name}: IVL FAIL"); ok=False; continue
        r=subprocess.run(['/tmp/b13tb'],capture_output=True,text=True,timeout=60)
        good="TB DONE" in r.stdout and "MISMATCH" not in r.stdout
        print(f"{name}: RTL {'OK' if good else 'FAIL'}")
        if not good: ok=False
    print("ALL OK" if ok else "FAILURES"); return 0 if ok else 1
if __name__=="__main__": sys.exit(main())
