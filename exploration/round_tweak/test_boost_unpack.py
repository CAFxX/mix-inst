#!/usr/bin/env python3
"""Regression test: diagnose() boost tuples must unpack in the boost
reprioritization path (sweep.py).

2026-10-04 incident: main() crashed with
    ValueError: too many values to unpack (expected 3)
because the boost-application loop unpacked diagnose()'s 4-tuples
(desc, target_nb, reason, amount) as 3-tuples. Every probe whose
diagnosis emitted boosts (S2 localized spikes, S1 LIN/DIFF rejections)
killed the whole sweep. Remediation (same day, two peer reviews):
  - boost tuples shrunk to (nb_name, reason, amount); the vestigial
    numeric field is gone, docstring corrected;
  - the loop extracted into sweep.apply_boosts(queue, name, boosts);
  - one bad probe can no longer kill the sweep (try/except, fail
    closed, log loudly).

This test calls the REAL sweep.apply_boosts -- it does not hand-copy
the loop -- so a consumer-side regression fails the test instead of
the sweep.

Run: python3 test_boost_unpack.py   (exit 0 = pass)
"""
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "sweep_boost", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "sweep.py"))
sweep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sweep)


def main():
    # synthetic rec: S2 spikes < 20 and localized (bits width 0 <= 16) ->
    # two boosts (N2, Z2); S1 lin_rej > 0 -> one boost (N1).
    rec = {"name": "t", "nb": "N7",
           "s1": {"lin_rej": 1, "worst_D": 8.0, "diff_rej": 0,
                  "worst_z": 2.0, "verdict": "FLAG"},
           "s2": {"spikes": [("0000000000000001", 20.0)] * 8,
                  "repeats_max": 5, "zmax": 20.0}}
    sig, hyp, boosts = sweep.diagnose(rec)
    assert sig != "no statistical failure", "synthetic rec must trigger boosts"
    assert len(boosts) == 3, f"expected 3 boosts, got {boosts!r}"
    for b in boosts:
        # producer contract: 3-tuple (nb_name, reason, amount); this is
        # what crashed main() when the consumer unpacked the wrong arity.
        assert len(b) == 3, f"boost tuple not 3-shaped: {b!r}"
        assert isinstance(b[0], str) and isinstance(b[1], str) \
            and isinstance(b[2], int), f"boost field types: {b!r}"

    queue = [{"name": "q1", "nb": "N1", "prio": 50000, "boosted_by": []},
             {"name": "q2", "nb": "N2", "prio": 40000, "boosted_by": []},
             {"name": "qz", "nb": "Z2", "prio": 30000, "boosted_by": []},
             {"name": "q7", "nb": "N7", "prio": 20000, "boosted_by": []}]
    sweep.apply_boosts(queue, "t", boosts)  # must not raise
    prio = {q["nb"]: q["prio"] for q in queue}
    by = {q["nb"]: q["boosted_by"] for q in queue}
    assert prio == {"N1": 49600, "N2": 39700, "Z2": 29700,
                    "N7": 20000}, prio
    # one tag per (probe, neighborhood): the two N2 boosts cut prio
    # twice but log a single entry.
    assert by["N2"] == ["t:S2-localized weakness bits 0-0"], by
    assert by["Z2"] == ["t:pbox changes bit adjacency"], by
    assert by["N1"] == ["t:LIN rej: try larger-spread pairs"], by
    assert by["N7"] == [], by

    # dedup phase: two boosts from one probe to the SAME neighborhood
    # (S2-localized + S1-DIFF both target N2) must stack the prio cut
    # but log only one tag.
    rec2 = dict(rec, s1=dict(rec["s1"], diff_rej=3, worst_z=9.0))
    _, _, boosts2 = sweep.diagnose(rec2)
    n2 = [b for b in boosts2 if b[0] == "N2"]
    assert len(n2) == 2, f"expected 2 N2 boosts, got {boosts2!r}"
    queue2 = [{"name": "q2", "nb": "N2", "prio": 40000, "boosted_by": []}]
    sweep.apply_boosts(queue2, "t2", boosts2)
    assert queue2[0]["prio"] == 40000 - 300 - 400, queue2[0]
    assert len(queue2[0]["boosted_by"]) == 1, queue2[0]
    assert queue2[0]["boosted_by"][0].startswith("t2:"), queue2[0]
    print("test_boost_unpack: PASS (real apply_boosts, 3 boosts, "
          "prio re-weighted, dedup holds)")


if __name__ == "__main__":
    main()
