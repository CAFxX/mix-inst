"""D1/D2 collision gate (mandatory: not bijective by construction).
ANY collision -> construction kill, no S1. Logs to collision_gate.log."""
import sys, time
sys.path.insert(0, "round_hyb/models")
import rhyb

with open("round_hyb/collision_gate.log", "w") as log:
    for nrounds, tag in ((4, "D1"), (5, "D2")):
        t0 = time.time()
        n, detail = rhyb.wide128_collision_gate(nrounds)
        line = (f"{tag} (rh_wide128_feist{nrounds}_nw): collisions={n} "
                f"| {detail} | {time.time()-t0:.1f}s")
        print(line, flush=True)
        log.write(line + "\n")
        log.flush()
