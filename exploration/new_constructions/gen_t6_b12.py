#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 12 (Feistel)."""
import inspect, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b12 as M
FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

def rotl32(x, r):
    r %= 32
    return x if r == 0 else f"{{{x}[{31-r}:0], {x}[31:{32-r}]}}"

RC32_HEX = ["32'h9e3779b9","32'h3c6ef372","32'hdaa66d2c","32'h78dde6e5"]

def gen_F(R, rk, sched, prefix):
    # 2-stage 32-bit AND-cascade, returns Verilog expr
    L = []
    cur = R
    for i,(a,b,c) in enumerate(sched):
        ra,rb,rc = rotl32(cur,a),rotl32(cur,b),rotl32(cur,c)
        L.append(f"  wire [31:0] {prefix}_s{i} = {cur} ^ ({ra} & {rb}) ^ {rc};")
        cur = f"{prefix}_s{i}"
    L.append(f"  wire [31:0] {prefix}_out = {cur} ^ {rk};")
    return L, f"{prefix}_out"

def gen_rtl(name, fsched):
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] x0 = val ^ key;",
         "  wire [31:0] L0 = x0[63:32];",
         "  wire [31:0] R0 = x0[31:0];",
         "  wire [31:0] kh = key[63:32];",
         "  wire [31:0] kl = key[31:0];"]
    L_cur, R_cur = "L0", "R0"
    for i in range(4):
        rk = f"({rotl32('kl', 7*(i+1))} ^ {RC32_HEX[i%4]})"
        L.append(f"  wire [31:0] rk{i} = {rk};")
        Flines, Fout = gen_F(R_cur, f"rk{i}", fsched, f"f{i}")
        L.extend(Flines)
        L.append(f"  wire [31:0] L{i+1} = {R_cur};")
        L.append(f"  wire [31:0] R{i+1} = {L_cur} ^ {Fout};")
        L_cur, R_cur = f"L{i+1}", f"R{i+1}"
    L.append(f"  wire [63:0] out_pre = {{{R_cur}, {L_cur}}};")
    L.append(f"  assign out = out_pre ^ key;")
    L.append("endmodule")
    return "\n".join(L)

def gen_c(name, desc, fsched):
    L = ["#include <stdint.h>",
         "static inline uint32_t rotl32(uint32_t x,int r){r&=31;return r?(x<<r)|(x>>(32-r)):x;}",
         f"// {name}: {desc}",
         "static inline uint32_t F_and2(uint32_t R, uint32_t rk, int s0a,int s0b,int s0c,int s1a,int s1b,int s1c){",
         "    uint32_t x=R;",
         "    x ^= (rotl32(x,s0a)&rotl32(x,s0b))^rotl32(x,s0c);",
         "    x ^= (rotl32(x,s1a)&rotl32(x,s1b))^rotl32(x,s1c);",
         "    return x ^ rk;}",
         "uint64_t mix_hash(uint64_t val,uint64_t key){",
         "    uint32_t L=(val^key)>>32, R=(uint32_t)(val^key);",
         "    uint32_t kh=key>>32, kl=(uint32_t)key;",
         "    static const uint32_t RC[4]={0x9E3779B9u,0x3C6EF372u,0xDAA66D2Cu,0x78DDE6E5u};"]
    (a0,b0,c0),(a1,b1,c1) = fsched
    for i in range(4):
        L.append(f"    {{uint32_t F=F_and2(R,(rotl32(kl,{7*(i+1)})^RC[{i%4}]),{a0},{b0},{c0},{a1},{b1},{c1});")
        L.append(f"     uint32_t nL=R, nR=L^F; L=nL; R=nR;}}")
    L.append("    return (((uint64_t)R)<<32 | L) ^ key;}")
    return "\n".join(L)+"\n"

BUNDLES = {"t6_feist4a": M.SCHED_FA, "t6_feist4b": M.SCHED_FB}

def sc_model(name, desc, sched):
    p=[f'"""Model {name} (batch 12)."""',"import numpy as np","","M64=np.uint64(0xFFFFFFFFFFFFFFFF)","M32=np.uint64(0xFFFFFFFF)"]
    p.append("RC32=[np.uint64(0x9E3779B9),np.uint64(0x3C6EF372),np.uint64(0xDAA66D2C),np.uint64(0x78DDE6E5)]")
    for n in ["_rotl32","_rotl64","_F_and2","_feistel4","_vec"]: p.append(inspect.getsource(getattr(M,n)))
    p.append(f"SCHED={sched!r}")
    p+=["","def _scalar(v,k):","    return _feistel4(v,k,SCHED)","_mix_np=_vec(_scalar)","",
        "def mix(v,k):","    return _scalar(int(v),int(k)) if np.ndim(v)==0 and np.ndim(k)==0 else _mix_np(v,k)",
        "def mix_np(V,K):","    return _mix_np(V,K)",f"meta={{'desc':{desc!r}}}"]
    return "\n".join(p)+"\n"

def main():
    import numpy as np
    for name, sched in BUNDLES.items():
        desc=M.CANDIDATES_B12[name][1]; d=os.path.join(FB,name); os.makedirs(d,exist_ok=True)
        open(f"{d}/rtl.v","w").write(gen_rtl(name,sched)+"\n")
        open(f"{d}/model.py","w").write(sc_model(name,desc,sched))
        json.dump({"name":name,"rtl_top":name,"description":desc,"screen_keys":["0x123456789abcdef0","0x0"],"practrand_keys":["0x123456789abcdef0","0x0"]},open(f"{d}/meta.json","w"),indent=1)
        open(f"{d}/impl.c","w").write(gen_c(name,desc,sched))
        print(f"{name}: written")
    print("\n=== checks ==="); ok=True; IVL='/home/hatch/tools/ivl-env/bin/iverilog'
    for name, sched in BUNDLES.items():
        d=os.path.join(FB,name); mu=__import__("importlib.util",fromlist=["util"])
        spec=mu.spec_from_file_location("m_"+name,f"{d}/model.py"); m=mu.module_from_spec(spec); spec.loader.exec_module(m)
        ref=M.CANDIDATES_B12[name][0]; rng=np.random.default_rng(42)
        for _ in range(200):
            v=int(rng.integers(0,2**64,dtype=np.uint64)); k=int(rng.integers(0,2**64,dtype=np.uint64))
            if int(m.mix(np.uint64(v),np.uint64(k)))!=int(ref(np.uint64(v),np.uint64(k))): print(f"{name}: MODEL FAIL"); ok=False; break
        else: print(f"{name}: model OK")
        open('/tmp/b12.c','w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r=subprocess.run(["gcc","-O2","-o","/tmp/b12","/tmp/b12.c",f"{d}/impl.c"],capture_output=True,text=True)
        if r.returncode!=0: print(f"{name}: GCC FAIL {r.stderr[:200]}"); ok=False; continue
        vecs=[(int(rng.integers(0,2**64,dtype=np.uint64)),int(rng.integers(0,2**64,dtype=np.uint64))) for _ in range(200)]
        r=subprocess.run(["/tmp/b12"],input="\n".join(f"{v:x} {k:x}" for v,k in vecs),capture_output=True,text=True)
        for (v,k),o in zip(vecs,r.stdout.strip().split("\n")):
            if int(o,16)!=int(ref(np.uint64(v),np.uint64(k))): print(f"{name}: C FAIL"); ok=False; break
        else: print(f"{name}: impl.c OK")
        fn=ref; vecs=[(int(rng.integers(0,2**64,dtype=np.uint64)),int(rng.integers(0,2**64,dtype=np.uint64))) for _ in range(20)]
        tb=['`timescale 1ns/1ps','module tb;','  reg [63:0] val,key;','  wire [63:0] out;',f'  {name} dut(.val(val),.key(key),.out(out));','  initial begin']
        for v,k in vecs:
            e=int(fn(np.uint64(v),np.uint64(k))); tb.append(f"    val=64'h{v:016x};key=64'h{k:016x};#10;"); tb.append(f'    if(out!==64\'h{e:016x})$display("MISMATCH");')
        tb+=['    $display("TB DONE");','    $finish;','  end','endmodule']
        open('/tmp/b12tb.v','w').write('\n'.join(tb))
        r=subprocess.run([IVL,'-o','/tmp/b12tb',f'{d}/rtl.v','/tmp/b12tb.v'],capture_output=True,text=True)
        if r.returncode!=0: print(f"{name}: IVL FAIL {r.stderr[:200]}"); ok=False; continue
        r=subprocess.run(['/tmp/b12tb'],capture_output=True,text=True,timeout=60)
        good="TB DONE" in r.stdout and "MISMATCH" not in r.stdout
        print(f"{name}: RTL {'OK' if good else 'FAIL'}")
        if not good: ok=False; print(r.stdout[:500])
    print("ALL OK" if ok else "FAILURES"); return 0 if ok else 1
if __name__=="__main__": sys.exit(main())
