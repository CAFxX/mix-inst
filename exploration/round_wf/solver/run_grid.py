
import itertools, json, multiprocessing as mp, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wf_sa import anneal, full_metrics

def one(args):
    lam, Dreq, seed, iters = args
    W, S, c = anneal(seed, lam, Dreq, iters)
    m = full_metrics(c)
    assert m["cycles"] == 1 and m["fixed"] == 0 and m["Dmin"] >= Dreq
    return {"lam": lam, "Dreq": Dreq, "seed": seed, "W": W, "S": S,
            "Dmin": m["Dmin"], "maxstretch": m["maxstretch"], "tour": c}

if __name__ == "__main__":
    t0 = time.time()
    grid = [(lam, D, s, 120000)
            for D in (4, 3, 2)
            for lam in (0, 1, 2, 4, 8, 16, 32)
            for s in (11, 22, 33)]
    with mp.Pool(4) as pool:
        results = pool.map(one, grid)
    # pareto per Dreq
    pareto = {}
    for D in (4, 3, 2):
        pts = [(r["W"], r["S"], i) for i, r in enumerate(results) if r["Dreq"] == D]
        nd = [i for (w, s_, i) in pts
              if not any(w2 <= w and s2 >= s_ and (w2 < w or s2 > s_) for (w2, s2, _) in pts)]
        pareto[str(D)] = sorted(nd)
    out = {"results": [{k: r[k] for k in ("lam","Dreq","seed","W","S","Dmin","maxstretch")} for r in results],
           "pareto_idx": pareto,
           "tours": {str(i): results[i]["tour"] for i in sum(pareto.values(), [])},
           "elapsed_s": round(time.time()-t0, 1)}
    os.makedirs(os.path.dirname(os.path.abspath(__file__))+"/../pareto", exist_ok=True)
    json.dump(out, open(os.path.dirname(os.path.abspath(__file__))+"/../pareto/frontier.json","w"))
    print("done", out["elapsed_s"], "pareto sizes", {k: len(v) for k,v in pareto.items()}, flush=True)
