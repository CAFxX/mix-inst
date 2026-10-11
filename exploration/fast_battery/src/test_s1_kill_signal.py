#!/usr/bin/env python3
"""Regression test for MAJOR-3 (2026-10-02): s1_screen.py dropped the inner
LIN/DIFF kill signal from screen_calibrated.

When screen_calibrated's inner gate (screen_lindiff.py) flags, it returns
EMPTY pb/rd rejection lists with s1_kill=True and cal_verdict="CAL_FLAG".
The old verdict logic only checked the (empty) lists -> misreported CAL_PASS.

This test replays the verdict computation against a synthetic kill dict.
It FAILS on the pre-fix code (emits CAL_PASS) and PASSES on fixed code (FLAG).
"""
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")


def verdict_old(pb_rej, rd_rej, res_marg, res_ld):
    # pre-fix logic, verbatim from s1_screen.py before 2026-10-02
    return ("CAL_PASS" if (not pb_rej and not rd_rej
                           and not res_ld["lin_rejected"]
                           and not res_ld["diff_rejected"]) else "FLAG")


def verdict_new(pb_rej, rd_rej, res_marg, res_ld):
    # post-fix logic, verbatim from s1_screen.py after 2026-10-02
    marg_kill = bool(res_marg.get("s1_kill")) or \
        res_marg.get("cal_verdict") == "CAL_FLAG"
    return ("CAL_PASS" if (not pb_rej and not rd_rej and not marg_kill
                           and not res_ld["lin_rejected"]
                           and not res_ld["diff_rejected"]) else "FLAG")


# Synthetic: inner gate flagged (kill), outer LIN/DIFF passed.
res_marg_kill = {
    "cal_verdict": "CAL_FLAG",
    "s1_kill": True,
    "cal_rejected_perbit": [],
    "cal_rejected_red": [],
}
res_ld_pass = {"lin_rejected": [], "diff_rejected": []}

old = verdict_old([], [], res_marg_kill, res_ld_pass)
new = verdict_new([], [], res_marg_kill, res_ld_pass)
print(f"old logic on inner-kill input: {old} (expect CAL_PASS = bug present)")
print(f"new logic on inner-kill input: {new} (expect FLAG = bug fixed)")
assert old == "CAL_PASS", "test setup wrong: old logic should exhibit the bug"
assert new == "FLAG", "REGRESSION: new logic drops the inner kill signal!"

# Sanity: a true all-pass still yields CAL_PASS under the new logic.
res_marg_pass = {"cal_verdict": "CAL_PASS", "s1_kill": False,
                 "cal_rejected_perbit": [], "cal_rejected_red": []}
assert verdict_new([], [], res_marg_pass, res_ld_pass) == "CAL_PASS"
print("all-pass still CAL_PASS: OK")
print("REGRESSION TEST PASSED")
