#!/usr/bin/env python3
"""Hill-climb from S374 tour: try 2-swaps, keep Pareto improvements in (S, W2d).
Niced background task. Checkpoints best to improve_S374.json."""
import json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import place2d as P2
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "improve_S374.json")
def tour_to_P(c):
    P=[0]*64
    for k in range(64): P[c[k]]=c[(k+1)%64]
    return P
def main():
    P0=json.load(open('/tmp/rnd_S374.json'))
    # recover a tour from P0 (find cycle)
    c=[0]; seen={0}
    while len(c)<64:
        nxt=P0[c[-1]]
        c.append(nxt); seen.add(nxt)
    assert len(c)==64 and P0[c[-1]]==0
    rng=random.Random(7)
    m0=P2.index_metrics(P0); w0=P2.placeability(P0,seeds=(1,),iters=8000)
    best=[(m0['S'],w0,list(c))]
    print(f"start: S={m0['S']} W2d={w0}",flush=True)
    t0=time.time(); it=0
    cur=list(c)
    while time.time()-t0 < 2400:  # 40 min budget
        it+=1
        a,b=rng.sample(range(64),2)
        nxt=list(cur); nxt[a],nxt[b]=nxt[b],nxt[a]
        P=tour_to_P(nxt)
        if not P2._o34_ok(P): continue
        m=P2.index_metrics(P)
        # cheap filter: only place if S is competitive
        if m['S'] < 365: continue
        w=P2.placeability(P,seeds=(1,),iters=8000)
        # pareto: keep if not dominated
        if not any(s>=m['S'] and ww<=w and (s>m['S'] or ww<w) for s,ww,_ in best):
            best=[e for e in best if not (m['S']>=e[0] and w<=e[1] and (m['S']>e[0] or w<e[1]))]
            best.append((m['S'],w,nxt))
            print(f"[{it}] NEW: S={m['S']} W2d={w} (pareto size {len(best)})",flush=True)
            json.dump([{"S":s,"W2d":ww,"tour":t} for s,ww,t in best], open(OUT,"w"))
            cur=nxt
        elif rng.random()<0.02:
            cur=nxt  # random restart kick
    print("done")
if __name__=="__main__": main()
