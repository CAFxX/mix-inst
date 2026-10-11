# GA log — analytical failure analysis + evolution

Append-only. Frontier-candidacy flags are NOT PARETO.md edits; the human coordinator verifies from raw logs.

[2026-10-03T16:11:51Z] GA start: pop=20 archive=4 (seed-parsed, no re-synthesis)
[2026-10-03T16:11:51Z] gen 0: evaluating seed seed_hand_const_iota {"const_fam": "iota", "const_where": "round_F", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "t...
[2026-10-03T16:12:13Z]   [seed_hand_const_iota] xcheck rc=0 XCHECK seed_hand_const_iota: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T16:12:13Z]   [seed_hand_const_iota] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T16:14:55Z] migrated checkpoint: built archive_q from archive
[2026-10-03T16:14:55Z] resumed at gen 0 evals=0 archiveS=4 archiveQ=0
[2026-10-03T16:14:55Z] gen 0: evaluating seed seed_hand_const_iota {"const_fam": "iota", "const_where": "round_F", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "t...
[2026-10-03T16:15:13Z]   [seed_hand_const_iota] xcheck rc=0 XCHECK seed_hand_const_iota: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T16:15:13Z]   [seed_hand_const_iota] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T16:17:32Z] migrated checkpoint: rebuilt archive_q (7 members) from mined seeds
[2026-10-03T16:17:32Z] resumed at gen 0 evals=0 archiveS=4 archiveQ=7
[2026-10-03T16:17:32Z] gen 0: evaluating seed seed_hand_const_iota {"const_fam": "iota", "const_where": "round_F", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "t...
[2026-10-03T16:17:45Z]   [seed_hand_const_iota] xcheck rc=0 XCHECK seed_hand_const_iota: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T16:17:45Z]   [seed_hand_const_iota] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T16:22:46Z]   [seed_hand_const_iota] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T16:27:46Z]   [seed_hand_const_iota] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T16:32:46Z]   [seed_hand_const_iota] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T16:37:46Z]   [seed_hand_const_iota] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T16:42:46Z]   [seed_hand_const_iota] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T16:47:58Z]   [seed_hand_const_iota] S0 no result json: [Errno 2] No such file or directory: '/home/hatch/workspace/mix/exploration/ga/results/seed_hand_const_iota/s0_result.json'; rc=1
[2026-10-03T16:47:58Z] gen 0: evaluating seed seed_hand_replacerot {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-03T16:48:45Z]   [seed_hand_replacerot] xcheck rc=0 XCHECK seed_hand_replacerot: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T16:48:58Z]   [seed_hand_replacerot] S0 no result json: [Errno 2] No such file or directory: '/home/hatch/workspace/mix/exploration/ga/results/seed_hand_replacerot/s0_result.json'; rc=1
[2026-10-03T16:48:58Z] gen 0: evaluating seed seed_hand_between64 {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-03T16:50:21Z]   [seed_hand_between64] xcheck rc=0 XCHECK seed_hand_between64: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T16:54:04Z] INFRA: iverilog was wiped by the VM deployment/reboot; reinstalled iverilog 12.0 from /var/cache/apt/archives via dpkg -i. S0 pipeline verified: seed_hand_const_iota = 37.9u/4170c/11954a PASS (equiv 1000/1000). The 16:47:58Z S0 rc=1 was FileNotFoundError iverilog, not a design or harness bug.
[2026-10-03T16:57:14Z]   [seed_hand_between64] S0 delay=39.0 cells=3467 area=9963.0 verdict=PASS rc=0
[2026-10-03T16:58:01Z]   [seed_hand_between64] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-03T16:58:01Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-03T16:58:01Z] gen 0: evaluating seed seed_hand_mask {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-03T16:58:12Z]   [seed_hand_mask] xcheck rc=0 XCHECK seed_hand_mask: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T17:03:48Z]   [seed_hand_mask] S0 delay=45.0 cells=5170 area=14764.0 verdict=PASS rc=0
[2026-10-03T17:03:48Z]   [seed_hand_mask] Stage-A discard: dominated by both archives
[2026-10-03T17:03:48Z] gen 0: evaluating seed seed_hand_prepost {"const_fam": "bit", "const_where": "prepost", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "ta...
[2026-10-03T17:04:05Z]   [seed_hand_prepost] xcheck rc=0 XCHECK seed_hand_prepost: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T17:04:05Z]   [seed_hand_prepost] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T17:09:05Z]   [seed_hand_prepost] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T17:14:05Z]   [seed_hand_prepost] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T17:19:05Z]   [seed_hand_prepost] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T17:24:06Z]   [seed_hand_prepost] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T17:36:43Z]   [seed_hand_prepost] S0 delay=39.7 cells=4653 area=13120.0 verdict=PASS rc=0
[2026-10-03T17:36:43Z]   [seed_hand_prepost] Stage-A discard: dominated by both archives
[2026-10-03T17:36:43Z] gen 0: evaluating seed seed_rnd16 {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 7, "tags":...
[2026-10-03T17:37:03Z]   [seed_rnd16] xcheck rc=1 ffdda k=f26fff4cc4fd394d C=d9bcc6be7b3798ab py=a506e2d9d9bcc6be
XCHECK seed_rnd16: FAIL 10000/10000 mismatches
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T17:37:03Z] gen 0: evaluating seed seed_rnd17 {"const_fam": "bit", "const_where": "prepost", "mask": "r2_FF", "pbox_perm": null, "pbox_where": "none", "rounds": 7, "t...
[2026-10-03T17:37:03Z]   [seed_rnd17] EMIT failed: name 'chi16_assigns' is not defined
[2026-10-03T17:37:03Z] gen 0: evaluating seed seed_rnd18 {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-03T17:37:25Z]   [seed_rnd18] xcheck rc=0 XCHECK seed_rnd18: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T17:37:25Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T17:42:25Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-03T17:47:25Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s

[2026-10-04T00:05Z] RESUME (subagent): driver died ~2026-10-03 17:47Z in seed_rnd18's polite_wait (runtime restart, not a task failure).
[2026-10-04T00:05Z] INCIDENT: this resume's own test_ga.py run clobbered state/checkpoint.pkl at 23:36Z — test_checkpoint_roundtrip wrote a 3-key toy dict over the production checkpoint. Recovered EXACTLY: mine_archive re-parse (all 12 member points verified identical), HAND_BUILT, GA_LOG S0 points, disk genome.json for rnd16/rnd18, transcript for rnd17, failures[0]+assoc transcribed verbatim, 7 fingerprints recomputed, t0/evals/deaths restored. One loss: seed_rnd19's genome existed only in the checkpoint (never emitted) -> regenerated a fresh valid random genome (logged substitution). Root causes fixed: (1) test now uses a temp STATE dir (never touches ga/state); (2) genome.py random_tag/_repair_final_tags used GLOBAL random instead of the passed rng (made fills irreproducible) -> rng threaded through all callers.
[2026-10-04T00:05Z] HARNESS FIXES (both verified 10k/10k xcheck + iverilog RTL sim): (1) emit.py is_base now requires rounds==6 — gen_r20's C_MAIN_TMPL hardcodes 6 rounds, so 7-round genomes failed xcheck 10000/10000 (seed_rnd16) and now route through the round-parameterized custom emitter; (2) ps-tag RTL used gen_r20._ps_block which calls chi16_assigns, undefined in gen_r20 (latent bug; round 20 never emitted ps) -> local _ps_block_local() ported from gen_r19 semantics, bit-exact vs gamodels._nl_ps.
[2026-10-04T00:05Z] Requeued infra-killed seeds seed_hand_const_iota + seed_hand_replacerot (S0 rc=1 was iverilog-wipe FileNotFoundError, not a design verdict) -> initial_sweep will re-run them on resume.
[2026-10-03T23:48:06Z] resumed at gen 0 evals=0 archiveS=4 archiveQ=7
[2026-10-03T23:48:06Z] gen 0: evaluating seed seed_hand_const_iota {"const_fam": "iota", "const_where": "round_F", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "t...
[2026-10-03T23:48:18Z]   [seed_hand_const_iota] xcheck rc=0 XCHECK seed_hand_const_iota: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T23:50:17Z]   [seed_hand_const_iota] S0 delay=37.9 cells=4170 area=11954.0 verdict=PASS rc=0
[2026-10-03T23:50:57Z]   [seed_hand_const_iota] S1 verdict=FLAG rc=2 lin=0 diff=1 pb=0 rd=0
[2026-10-03T23:50:57Z]   death @S1: HYPOTHESIS: differential weakness in F (1 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-03T23:50:57Z] gen 0: evaluating seed seed_hand_replacerot {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-03T23:51:32Z]   [seed_hand_replacerot] xcheck rc=0 XCHECK seed_hand_replacerot: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T23:53:47Z]   [seed_hand_replacerot] S0 delay=37.7 cells=3948 area=11262.0 verdict=PASS rc=0
[2026-10-03T23:54:34Z]   [seed_hand_replacerot] S1 verdict=FLAG rc=2 lin=10 diff=10 pb=0 rd=0
[2026-10-03T23:54:34Z]   death @S1: HYPOTHESIS: linear hull through the round linears (10 LIN rejections) — the (a,b) rotation pairs admit a high-bias linear trail at 6r.
[2026-10-03T23:54:34Z] gen 0: evaluating seed seed_rnd18 {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-03T23:54:42Z]   [seed_rnd18] xcheck rc=0 XCHECK seed_rnd18: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-03T23:57:06Z]   [seed_rnd18] S0 delay=38.4 cells=4031 area=11359.0 verdict=PASS rc=0
[2026-10-04T00:00:55Z]   [seed_rnd18] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T02:23:58Z] resumed at gen 0 evals=0 archiveS=4 archiveQ=7
[2026-10-04T02:23:58Z] gen 0: evaluating seed seed_rnd18 {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T02:24:06Z]   [seed_rnd18] xcheck rc=0 XCHECK seed_rnd18: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T02:25:39Z]   [seed_rnd18] S0 delay=38.4 cells=4031 area=11359.0 verdict=PASS rc=0
[2026-10-04T02:28:02Z]   [seed_rnd18] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T03:01:14Z] resumed at gen 0 evals=0 archiveS=4 archiveQ=7
[2026-10-04T03:01:14Z] gen 0: evaluating seed seed_rnd18 {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T03:01:22Z]   [seed_rnd18] xcheck rc=0 XCHECK seed_rnd18: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T03:03:21Z]   [seed_rnd18] S0 delay=38.4 cells=4031 area=11359.0 verdict=PASS rc=0
[2026-10-04T03:07:17Z]   [seed_rnd18] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T07:54:27Z] resumed at gen 0 evals=0 archiveS=4 archiveQ=7
[2026-10-04T07:54:27Z] gen 0: evaluating seed seed_rnd18 {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T07:54:55Z]   [seed_rnd18] xcheck rc=0 XCHECK seed_rnd18: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T07:54:55Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T07:59:55Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:04:55Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:09:55Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:14:55Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:19:56Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:24:56Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:29:56Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:34:56Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:39:56Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:44:56Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:49:56Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:54:57Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T08:59:57Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:04:57Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:09:57Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:18:18Z]   [seed_rnd18] S0 delay=38.4 cells=4031 area=11359.0 verdict=PASS rc=0
[2026-10-04T09:18:18Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:23:18Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:28:18Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:33:18Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:38:18Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:43:18Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:48:19Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T09:53:19Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T10:03:51Z]   [seed_rnd18] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T10:25:33Z] resumed at gen 0 evals=0 archiveS=4 archiveQ=7
[2026-10-04T10:25:33Z] gen 0: evaluating seed seed_rnd18 {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T10:25:40Z]   [seed_rnd18] xcheck rc=0 XCHECK seed_rnd18: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T10:28:04Z]   [seed_rnd18] S0 delay=38.4 cells=4031 area=11359.0 verdict=PASS rc=0
[2026-10-04T10:31:17Z]   [seed_rnd18] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T10:43:10Z]   [seed_rnd18] S2 verdict=PASS max_repeats=0 max_z=3.7 rc=0 spikes=0
[2026-10-04T10:43:10Z]   [seed_rnd18] ARCHIVE-Q ENTER (provisional): (38.4, 4031, 11359) evicted=['r19_feist6_alt_notr_fm07_nw', 'r19_feist6_alt_notr_fm11_nw', 'r19_feist6_alt_notr_fm311_nw', 'r18_feist6_alt_palk_nw', 'r15_feist6_parsplit_nw', 'r9_feist6_rot311_nw', 'r8_feist6_s1_1sbox_nw']
[2026-10-04T10:46:46Z]   [seed_rnd18] S3 cfg1 rc=0
[2026-10-04T10:50:56Z]   [seed_rnd18] S3 cfg2 rc=0
[2026-10-04T10:52:54Z]   [seed_rnd18] S4 rc=0 passed=True
[2026-10-04T10:52:54Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T10:57:54Z]   [seed_rnd18] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T11:07:14Z]   [seed_rnd18] Q1 sac_z5=0 bic=0.02694
[2026-10-04T11:07:14Z]   [seed_rnd18] ARCHIVE-Q EVICT: bic=0.026940838846846435 > 0.02
[2026-10-04T11:07:14Z] gen 0: evaluating seed seed_rnd19 {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 7, "tags":...
[2026-10-04T11:07:29Z]   [seed_rnd19] xcheck rc=0 XCHECK seed_rnd19: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T11:10:32Z]   [seed_rnd19] S0 delay=44.1 cells=5087 area=14584.0 verdict=PASS rc=0
[2026-10-04T11:10:32Z]   [seed_rnd19] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T11:15:32Z]   [seed_rnd19] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T11:26:12Z]   [seed_rnd19] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T11:50:10Z]   [seed_rnd19] S2 verdict=PASS max_repeats=0 max_z=4.1 rc=0 spikes=0
[2026-10-04T11:50:10Z]   [seed_rnd19] ARCHIVE-Q ENTER (provisional): (44.1, 5087, 14584) evicted=[]
[2026-10-04T11:56:07Z]   [seed_rnd19] S3 cfg1 rc=0
[2026-10-04T12:01:16Z]   [seed_rnd19] S3 cfg2 rc=0
[2026-10-04T12:03:53Z]   [seed_rnd19] S4 rc=0 passed=True
[2026-10-04T12:07:00Z]   [seed_rnd19] Q1 sac_z5=0 bic=0.00902
[2026-10-04T12:07:00Z]   [seed_rnd19] ARCHIVE CONFIRMED: (44.1, 5087, 14584) bic=0.00902 S=out Q=in
[2026-10-04T12:07:00Z]   [seed_rnd19] *** FRONTIER-Q-CANDIDATE seed_rnd19 (44.1, 5087, 14584) bic=0.00902 ***
[2026-10-04T12:07:00Z] gen 0: evaluating ga_g00_001 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-04T12:08:11Z]   [ga_g00_001] xcheck rc=0 XCHECK ga_g00_001: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T12:08:11Z]   [ga_g00_001] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T12:13:11Z]   [ga_g00_001] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T12:18:12Z]   [ga_g00_001] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T12:33:45Z]   [ga_g00_001] S0 no result json: [Errno 2] No such file or directory: '/home/hatch/workspace/mix/exploration/ga/results/ga_g00_001/s0_result.json'; rc=1
[2026-10-04T12:33:45Z] gen 0: evaluating ga_g00_002 via mutate {"const_fam": "iota", "const_where": "round_F", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 7, "t...
[2026-10-04T12:34:27Z]   [ga_g00_002] xcheck rc=0 XCHECK ga_g00_002: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T12:39:26Z]   [ga_g00_002] S0 delay=43.5 cells=4780 area=13750.0 verdict=PASS rc=0
[2026-10-04T12:45:17Z]   [ga_g00_002] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T13:04:55Z]   [ga_g00_002] S2 verdict=PASS max_repeats=0 max_z=3.8 rc=0 spikes=0
[2026-10-04T13:04:55Z]   [ga_g00_002] ARCHIVE-Q ENTER (provisional): (43.5, 4780, 13750) evicted=['seed_rnd19']
[2026-10-04T13:10:28Z]   [ga_g00_002] S3 cfg1 rc=0
[2026-10-04T13:15:14Z]   [ga_g00_002] S3 cfg2 rc=0
[2026-10-04T13:17:31Z]   [ga_g00_002] S4 rc=0 passed=True
[2026-10-04T13:20:36Z]   [ga_g00_002] Q1 sac_z5=0 bic=0.00962
[2026-10-04T13:20:36Z]   [ga_g00_002] ARCHIVE CONFIRMED: (43.5, 4780, 13750) bic=0.00962 S=out Q=in
[2026-10-04T13:20:36Z]   [ga_g00_002] *** FRONTIER-Q-CANDIDATE ga_g00_002 (43.5, 4780, 13750) bic=0.00962 ***
[2026-10-04T13:20:36Z] gen 0: evaluating ga_g00_003 via guided(S1:guided_nonlinear) {"const_fam": "iota", "const_where": "round_F", "mask": "r2_SP", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "...
[2026-10-04T13:20:55Z]   [ga_g00_003] xcheck rc=0 XCHECK ga_g00_003: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T13:24:00Z]   [ga_g00_003] S0 delay=42.6 cells=4006 area=11554.0 verdict=PASS rc=0
[2026-10-04T13:27:47Z]   [ga_g00_003] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T13:43:28Z]   [ga_g00_003] S2 verdict=PASS max_repeats=0 max_z=11.3 rc=0 spikes=0
[2026-10-04T13:43:28Z]   [ga_g00_003] ARCHIVE-Q ENTER (provisional): (42.6, 4006, 11554) evicted=['ga_g00_002']
[2026-10-04T13:47:20Z]   [ga_g00_003] S3 cfg1 rc=0
[2026-10-04T13:51:05Z]   [ga_g00_003] S3 cfg2 rc=0
[2026-10-04T13:52:44Z]   [ga_g00_003] S4 rc=0 passed=True
[2026-10-04T13:55:32Z]   [ga_g00_003] Q1 sac_z5=0 bic=0.14118
[2026-10-04T13:55:32Z]   [ga_g00_003] ARCHIVE-Q EVICT: bic=0.14117509504547385 > 0.02
[2026-10-04T13:55:32Z] gen 0: evaluating ga_g00_004 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T13:55:41Z]   [ga_g00_004] xcheck rc=0 XCHECK ga_g00_004: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T13:57:27Z]   [ga_g00_004] S0 delay=37.4 cells=4339 area=12266.0 verdict=PASS rc=0
[2026-10-04T14:01:03Z]   [ga_g00_004] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T14:23:17Z] migrated checkpoint: rebuilt archive_q (7 members) from mined seeds
[2026-10-04T14:23:17Z] resumed at gen 0 evals=3 archiveS=4 archiveQ=7
[2026-10-04T14:23:17Z] gen 0: evaluating ga_g00_004 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T14:23:22Z]   [ga_g00_004] xcheck rc=0 XCHECK ga_g00_004: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T14:24:34Z]   [ga_g00_004] S0 delay=37.0 cells=4357 area=12511.0 verdict=PASS rc=0
[2026-10-04T14:28:21Z]   [ga_g00_004] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T14:40:33Z]   [ga_g00_004] S2 verdict=PASS max_repeats=0 max_z=11.2 rc=0 spikes=0
[2026-10-04T14:40:33Z]   [ga_g00_004] ARCHIVE-S ENTER (provisional): (37.0, 4357, 12511) evicted=[]
[2026-10-04T14:40:33Z]   [ga_g00_004] ARCHIVE-Q ENTER (provisional): (37.0, 4357, 12511) evicted=['r18_feist6_alt_palk_nw', 'r19_feist6_alt_notr_fm07_nw', 'r19_feist6_alt_notr_fm311_nw', 'r21_feist6_alt_notr_chioff13all_fm311_nw']
[2026-10-04T14:42:09Z]   [ga_g00_004] S3 cfg1 rc=0
[2026-10-04T14:44:24Z]   [ga_g00_004] S3 cfg2 rc=0
[2026-10-04T14:45:49Z]   [ga_g00_004] S4 rc=0 passed=True
[2026-10-04T14:45:49Z]   [ga_g00_004] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T14:54:13Z]   [ga_g00_004] Q1 sac_z5=0 bic=0.14149
[2026-10-04T14:54:13Z]   [ga_g00_004] ARCHIVE-Q EVICT: bic=0.14149255646039563 > 0.02
[2026-10-04T14:54:13Z]   [ga_g00_004] ARCHIVE CONFIRMED: (37.0, 4357, 12511) bic=0.14149 S=in Q=out
[2026-10-04T14:54:13Z]   [ga_g00_004] *** FRONTIER-S-CANDIDATE ga_g00_004 (37.0, 4357, 12511) bic=0.14149 ***
[2026-10-04T14:54:13Z] gen 0: evaluating ga_g00_005 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T14:54:21Z]   [ga_g00_005] xcheck rc=0 XCHECK ga_g00_005: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T14:56:19Z]   [ga_g00_005] S0 delay=37.7 cells=4505 area=12752.0 verdict=PASS rc=0
[2026-10-04T14:58:22Z]   [ga_g00_005] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T15:05:01Z]   [ga_g00_005] S2 verdict=PASS max_repeats=0 max_z=11.3 rc=0 spikes=0
[2026-10-04T15:05:01Z]   [ga_g00_005] ARCHIVE-Q ENTER (provisional): (37.7, 4505, 12752) evicted=[]
[2026-10-04T15:06:58Z]   [ga_g00_005] S3 cfg1 rc=0
[2026-10-04T15:08:56Z]   [ga_g00_005] S3 cfg2 rc=0
[2026-10-04T15:09:49Z]   [ga_g00_005] S4 rc=0 passed=False
[2026-10-04T15:11:00Z]   [ga_g00_005] Q1 sac_z5=0 bic=0.14002
[2026-10-04T15:11:00Z]   [ga_g00_005] ARCHIVE EVICT: Stage D failed at s4
[2026-10-04T15:11:00Z]   death @s4: no hypothesis
[2026-10-04T15:11:00Z] gen 0: evaluating ga_g00_006 via guided(S1:guided_nonlinear) {"const_fam": "iota", "const_where": "round_F", "mask": "r1_SP", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "...
[2026-10-04T15:11:05Z]   [ga_g00_006] xcheck rc=0 XCHECK ga_g00_006: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T15:12:06Z]   [ga_g00_006] S0 delay=40.4 cells=4370 area=12487.0 verdict=PASS rc=0
[2026-10-04T15:13:37Z]   [ga_g00_006] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T15:19:42Z]   [ga_g00_006] S2 verdict=PASS max_repeats=0 max_z=11.8 rc=0 spikes=0
[2026-10-04T15:19:42Z]   [ga_g00_006] ARCHIVE-Q ENTER (provisional): (40.4, 4370, 12487) evicted=[]
[2026-10-04T15:21:30Z]   [ga_g00_006] S3 cfg1 rc=0
[2026-10-04T15:23:30Z]   [ga_g00_006] S3 cfg2 rc=0
[2026-10-04T15:24:26Z]   [ga_g00_006] S4 rc=0 passed=True
[2026-10-04T15:25:44Z]   [ga_g00_006] Q1 sac_z5=0 bic=0.13949
[2026-10-04T15:25:44Z]   [ga_g00_006] ARCHIVE-Q EVICT: bic=0.13949168055070832 > 0.02
[2026-10-04T15:25:44Z] gen 0: evaluating ga_g00_007 via mutate {"const_fam": null, "const_where": "none", "mask": "r2_H2", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-04T15:25:49Z]   [ga_g00_007] xcheck rc=0 XCHECK ga_g00_007: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T15:27:31Z]   [ga_g00_007] S0 delay=46.6 cells=4523 area=13085.0 verdict=PASS rc=0
[2026-10-04T15:27:31Z]   [ga_g00_007] Stage-A discard: dominated by both archives
[2026-10-04T15:27:31Z] gen 0: evaluating ga_g00_008 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T15:27:35Z]   [ga_g00_008] xcheck rc=0 XCHECK ga_g00_008: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T15:28:29Z]   [ga_g00_008] S0 delay=37.6 cells=4152 area=11795.0 verdict=PASS rc=0
[2026-10-04T15:30:11Z]   [ga_g00_008] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T15:36:04Z]   [ga_g00_008] S2 verdict=PASS max_repeats=0 max_z=10.8 rc=0 spikes=0
[2026-10-04T15:36:04Z]   [ga_g00_008] ARCHIVE-Q ENTER (provisional): (37.6, 4152, 11795) evicted=['r15_feist6_parsplit_nw', 'r9_feist6_rot311_nw']
[2026-10-04T15:37:38Z]   [ga_g00_008] S3 cfg1 rc=0
[2026-10-04T15:39:28Z]   [ga_g00_008] S3 cfg2 rc=0
[2026-10-04T15:40:16Z]   [ga_g00_008] S4 rc=0 passed=True
[2026-10-04T15:41:30Z]   [ga_g00_008] Q1 sac_z5=0 bic=0.14439
[2026-10-04T15:41:30Z]   [ga_g00_008] ARCHIVE-Q EVICT: bic=0.14439392690549377 > 0.02
[2026-10-04T15:41:30Z] gen 0: evaluating ga_g00_009 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T15:41:35Z]   [ga_g00_009] xcheck rc=0 XCHECK ga_g00_009: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T15:42:51Z]   [ga_g00_009] S0 delay=40.1 cells=4577 area=13010.0 verdict=PASS rc=0
[2026-10-04T15:45:16Z]   [ga_g00_009] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T15:52:33Z]   [ga_g00_009] S2 verdict=PASS max_repeats=0 max_z=17.1 rc=0 spikes=0
[2026-10-04T15:52:33Z]   [ga_g00_009] ARCHIVE-Q ENTER (provisional): (40.1, 4577, 13010) evicted=[]
[2026-10-04T15:54:49Z]   [ga_g00_009] S3 cfg1 rc=0
[2026-10-04T15:54:49Z]   [ga_g00_009] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T16:00:59Z]   [ga_g00_009] S3 cfg2 rc=0
[2026-10-04T16:01:35Z]   [ga_g00_009] S4 rc=0 passed=True
[2026-10-04T16:02:44Z]   [ga_g00_009] Q1 sac_z5=0 bic=0.00834
[2026-10-04T16:02:44Z]   [ga_g00_009] ARCHIVE CONFIRMED: (40.1, 4577, 13010) bic=0.00834 S=out Q=in
[2026-10-04T16:02:44Z]   [ga_g00_009] *** FRONTIER-Q-CANDIDATE ga_g00_009 (40.1, 4577, 13010) bic=0.00834 ***
[2026-10-04T16:02:44Z] gen 0: evaluating ga_g00_010 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 7, "tags":...
[2026-10-04T16:02:50Z]   [ga_g00_010] xcheck rc=0 XCHECK ga_g00_010: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:04:03Z]   [ga_g00_010] S0 delay=43.3 cells=5318 area=15053.0 verdict=PASS rc=0
[2026-10-04T16:04:03Z]   [ga_g00_010] Stage-A discard: dominated by both archives
[2026-10-04T16:04:03Z] gen 0: evaluating ga_g00_011 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T16:04:07Z]   [ga_g00_011] xcheck rc=0 XCHECK ga_g00_011: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:05:13Z]   [ga_g00_011] S0 delay=38.8 cells=5053 area=14320.0 verdict=PASS rc=0
[2026-10-04T16:06:39Z]   [ga_g00_011] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T16:12:07Z]   [ga_g00_011] S2 verdict=PASS max_repeats=0 max_z=10.7 rc=0 spikes=0
[2026-10-04T16:12:07Z]   [ga_g00_011] ARCHIVE-Q ENTER (provisional): (38.8, 5053, 14320) evicted=[]
[2026-10-04T16:13:41Z]   [ga_g00_011] S3 cfg1 rc=0
[2026-10-04T16:15:20Z]   [ga_g00_011] S3 cfg2 rc=0
[2026-10-04T16:16:03Z]   [ga_g00_011] S4 rc=0 passed=True
[2026-10-04T16:17:13Z]   [ga_g00_011] Q1 sac_z5=0 bic=0.00805
[2026-10-04T16:17:13Z]   [ga_g00_011] ARCHIVE CONFIRMED: (38.8, 5053, 14320) bic=0.00805 S=out Q=in
[2026-10-04T16:17:13Z]   [ga_g00_011] *** FRONTIER-Q-CANDIDATE ga_g00_011 (38.8, 5053, 14320) bic=0.00805 ***
[2026-10-04T16:17:13Z] gen 0: evaluating ga_g00_012 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-04T16:17:35Z]   [ga_g00_012] xcheck rc=0 XCHECK ga_g00_012: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:19:37Z]   [ga_g00_012] S0 delay=37.5 cells=3788 area=10794.0 verdict=PASS rc=0
[2026-10-04T16:19:55Z]   [ga_g00_012] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-04T16:19:55Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T16:19:55Z] gen 0: evaluating ga_g00_013 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-04T16:20:18Z]   [ga_g00_013] xcheck rc=0 XCHECK ga_g00_013: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:22:04Z]   [ga_g00_013] S0 delay=38.8 cells=3519 area=10188.0 verdict=PASS rc=0
[2026-10-04T16:22:24Z]   [ga_g00_013] S1 verdict=FLAG rc=2 lin=1 diff=10 pb=0 rd=0
[2026-10-04T16:22:24Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T16:22:24Z] gen 0: evaluating ga_g00_014 via guided(S1:guided_linear) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-04T16:22:39Z]   [ga_g00_014] xcheck rc=0 XCHECK ga_g00_014: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:23:22Z]   [ga_g00_014] S0 delay=36.4 cells=4073 area=11666.0 verdict=PASS rc=0
[2026-10-04T16:23:39Z]   [ga_g00_014] S1 verdict=FLAG rc=2 lin=10 diff=4 pb=0 rd=0
[2026-10-04T16:23:39Z]   death @S1: HYPOTHESIS: linear hull through the round linears (10 LIN rejections) — the (a,b) rotation pairs admit a high-bias linear trail at 6r.
[2026-10-04T16:23:39Z] --- gen 1 done: pop=20 archiveS=5 archiveQ=3 evals=14 deaths=7
[2026-10-04T16:23:39Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-04T16:23:39Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-04T16:23:39Z]     archS 37.2u 4382c 12497a bic=0.17232347425964098 [r20_feist6_alt_notr_keyin_nw]
[2026-10-04T16:23:39Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-04T16:23:39Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-04T16:23:39Z]     archQ 38.8u 5053c 14320a bic=0.008049706125215255 [ga_g00_011]
[2026-10-04T16:23:39Z]     archQ 40.1u 4577c 13010a bic=0.00833566795696304 [ga_g00_009]
[2026-10-04T16:23:39Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-04T16:23:39Z]     assoc [S1] rounds=6: x6
[2026-10-04T16:23:39Z]     assoc [S1] s1_311x3: x4
[2026-10-04T16:23:39Z]     assoc [S1] trunc-ish:chi_notr@r6: x3
[2026-10-04T16:23:39Z]     assoc [S1] chi_notrx1: x3
[2026-10-04T16:23:39Z]     assoc [S1] pbox:between64/interleave64: x3
[2026-10-04T16:23:39Z]     assoc [S1] trunc-ish:chi32v_notr@r6: x3
[2026-10-04T16:23:39Z] gen 1: evaluating ga_g01_015 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T16:23:43Z]   [ga_g01_015] xcheck rc=0 XCHECK ga_g01_015: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:24:11Z]   [ga_g01_015] S0 delay=39.2 cells=4587 area=12714.0 verdict=PASS rc=0
[2026-10-04T16:25:43Z]   [ga_g01_015] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T16:31:46Z]   [ga_g01_015] S2 verdict=PASS max_repeats=0 max_z=3.5 rc=0 spikes=0
[2026-10-04T16:31:46Z]   [ga_g01_015] ARCHIVE-Q ENTER (provisional): (39.2, 4587, 12714) evicted=[]
[2026-10-04T16:33:16Z]   [ga_g01_015] S3 cfg1 rc=0
[2026-10-04T16:34:49Z]   [ga_g01_015] S3 cfg2 rc=0
[2026-10-04T16:35:32Z]   [ga_g01_015] S4 rc=0 passed=True
[2026-10-04T16:36:45Z]   [ga_g01_015] Q1 sac_z5=0 bic=0.02623
[2026-10-04T16:36:45Z]   [ga_g01_015] ARCHIVE-Q EVICT: bic=0.026229948217980855 > 0.02
[2026-10-04T16:36:45Z] gen 1: evaluating ga_g01_016 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-04T16:37:08Z]   [ga_g01_016] xcheck rc=0 XCHECK ga_g01_016: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:37:08Z]   [ga_g01_016] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T16:44:38Z]   [ga_g01_016] S0 delay=43.0 cells=3881 area=11288.0 verdict=PASS rc=0
[2026-10-04T16:44:58Z]   [ga_g01_016] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-04T16:44:58Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T16:44:58Z] gen 1: evaluating ga_g01_017 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-04T16:45:21Z]   [ga_g01_017] xcheck rc=0 XCHECK ga_g01_017: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:47:36Z]   [ga_g01_017] S0 delay=41.8 cells=3483 area=10025.0 verdict=PASS rc=0
[2026-10-04T16:47:59Z]   [ga_g01_017] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-04T16:47:59Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T16:47:59Z] gen 1: evaluating ga_g01_018 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-04T16:48:20Z]   [ga_g01_018] xcheck rc=0 XCHECK ga_g01_018: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:50:32Z]   [ga_g01_018] S0 delay=42.0 cells=3362 area=9780.0 verdict=PASS rc=0
[2026-10-04T16:50:51Z]   [ga_g01_018] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-04T16:50:51Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T16:50:51Z] gen 1: evaluating ga_g01_019 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T16:50:55Z]   [ga_g01_019] xcheck rc=0 XCHECK ga_g01_019: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T16:52:00Z]   [ga_g01_019] S0 delay=39.5 cells=4848 area=13891.0 verdict=PASS rc=0
[2026-10-04T16:53:29Z]   [ga_g01_019] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T16:59:14Z]   [ga_g01_019] S2 verdict=PASS max_repeats=0 max_z=11.2 rc=0 spikes=0
[2026-10-04T16:59:14Z]   [ga_g01_019] ARCHIVE-Q ENTER (provisional): (39.5, 4848, 13891) evicted=[]
[2026-10-04T17:01:00Z]   [ga_g01_019] S3 cfg1 rc=0
[2026-10-04T17:02:43Z]   [ga_g01_019] S3 cfg2 rc=0
[2026-10-04T17:03:25Z]   [ga_g01_019] S4 rc=0 passed=True
[2026-10-04T17:04:35Z]   [ga_g01_019] Q1 sac_z5=0 bic=0.00860
[2026-10-04T17:04:35Z]   [ga_g01_019] ARCHIVE CONFIRMED: (39.5, 4848, 13891) bic=0.00860 S=out Q=in
[2026-10-04T17:04:35Z]   [ga_g01_019] *** FRONTIER-Q-CANDIDATE ga_g01_019 (39.5, 4848, 13891) bic=0.00860 ***
[2026-10-04T17:04:35Z] gen 1: evaluating ga_g01_020 via mutate {"const_fam": "iota", "const_where": "round_F", "mask": "r3_H2", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "...
[2026-10-04T17:04:39Z]   [ga_g01_020] xcheck rc=0 XCHECK ga_g01_020: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T17:07:25Z]   [ga_g01_020] S0 delay=42.9 cells=4447 area=12690.0 verdict=PASS rc=0
[2026-10-04T17:07:25Z]   [ga_g01_020] Stage-A discard: dominated by both archives
[2026-10-04T17:07:25Z] gen 1: evaluating ga_g01_021 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_SP", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-04T17:24:41Z] resumed at gen 1 evals=20 archiveS=5 archiveQ=4
[2026-10-04T17:24:41Z] gen 1: evaluating ga_g01_021 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T17:24:45Z]   [ga_g01_021] xcheck rc=0 XCHECK ga_g01_021: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T17:26:10Z]   [ga_g01_021] S0 delay=37.9 cells=4255 area=12095.0 verdict=PASS rc=0
[2026-10-04T17:27:58Z]   [ga_g01_021] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T17:43:23Z]   [ga_g01_021] S2 verdict=PASS max_repeats=0 max_z=10.7 rc=0 spikes=0
[2026-10-04T17:43:23Z]   [ga_g01_021] ARCHIVE-Q ENTER (provisional): (37.9, 4255, 12095) evicted=['ga_g00_009', 'ga_g00_011', 'ga_g01_019']
[2026-10-04T17:43:23Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T17:48:23Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T17:53:23Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T17:58:24Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:03:24Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:08:24Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:20:36Z]   [ga_g01_021] S3 cfg1 rc=0
[2026-10-04T18:20:36Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:25:36Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:30:36Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:35:36Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:43:31Z]   [ga_g01_021] S3 cfg2 rc=0
[2026-10-04T18:43:31Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:48:32Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:53:32Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T18:59:42Z]   [ga_g01_021] S4 rc=0 passed=True
[2026-10-04T18:59:42Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T19:04:42Z]   [ga_g01_021] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T19:11:17Z]   [ga_g01_021] Q1 sac_z5=0 bic=0.17371
[2026-10-04T19:11:17Z]   [ga_g01_021] ARCHIVE-Q EVICT: bic=0.1737068352691734 > 0.02
[2026-10-04T19:11:17Z] gen 1: evaluating ga_g01_022 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-04T19:11:46Z]   [ga_g01_022] xcheck rc=0 XCHECK ga_g01_022: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T19:17:21Z]   [ga_g01_022] S0 delay=48.3 cells=3657 area=10580.0 verdict=PASS rc=0
[2026-10-04T19:18:04Z]   [ga_g01_022] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-04T19:18:04Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T19:18:04Z] gen 1: evaluating ga_g01_023 via mutate {"const_fam": null, "const_where": "none", "mask": "r2_FF", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-04T19:18:29Z]   [ga_g01_023] xcheck rc=0 XCHECK ga_g01_023: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T19:26:05Z]   [ga_g01_023] S0 delay=47.1 cells=4126 area=12089.0 verdict=PASS rc=0
[2026-10-04T19:26:34Z]   [ga_g01_023] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-04T19:26:34Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T19:26:34Z] gen 1: evaluating ga_g01_024 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T19:26:40Z]   [ga_g01_024] xcheck rc=0 XCHECK ga_g01_024: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T19:41:34Z] resumed at gen 1 evals=23 archiveS=5 archiveQ=1
[2026-10-04T19:41:34Z] gen 1: evaluating ga_g01_024 via guided(S1:guided_nonlinear) {"const_fam": "iota", "const_where": "round_F", "mask": "r1_A5", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "...
[2026-10-04T19:41:38Z]   [ga_g01_024] xcheck rc=0 XCHECK ga_g01_024: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T19:43:18Z]   [ga_g01_024] S0 delay=42.7 cells=5289 area=14801.0 verdict=PASS rc=0
[2026-10-04T19:43:58Z]   [ga_g01_024] S1 verdict=FLAG rc=2 lin=0 diff=0 pb=0 rd=0
[2026-10-04T19:43:58Z]   death @S1: HYPOTHESIS: S1 FLAG without family detail — see s1_result.json.
[2026-10-04T19:43:58Z] gen 1: evaluating ga_g01_025 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-04T19:44:26Z]   [ga_g01_025] xcheck rc=0 XCHECK ga_g01_025: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T19:46:19Z]   [ga_g01_025] S0 delay=38.5 cells=3401 area=9903.0 verdict=PASS rc=0
[2026-10-04T19:46:51Z]   [ga_g01_025] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-04T19:46:51Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T19:46:51Z] gen 1: evaluating ga_g01_026 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-04T19:47:47Z]   [ga_g01_026] xcheck rc=0 XCHECK ga_g01_026: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T19:49:19Z]   [ga_g01_026] S0 delay=33.0 cells=3103 area=8962.0 verdict=PASS rc=0
[2026-10-04T19:49:48Z]   [ga_g01_026] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-04T19:49:48Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T19:49:48Z] gen 1: evaluating ga_g01_027 via mutate {"const_fam": null, "const_where": "none", "mask": "r2_FF", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "ro...
[2026-10-04T19:50:06Z]   [ga_g01_027] xcheck rc=0 XCHECK ga_g01_027: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T19:53:48Z]   [ga_g01_027] S0 delay=45.6 cells=4468 area=12901.0 verdict=PASS rc=0
[2026-10-04T19:53:48Z]   [ga_g01_027] Stage-A discard: dominated by both archives
[2026-10-04T19:53:48Z] gen 1: evaluating ga_g01_028 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-04T19:54:54Z]   [ga_g01_028] xcheck rc=0 XCHECK ga_g01_028: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T20:00:47Z]   [ga_g01_028] S0 delay=46.9 cells=3713 area=10729.0 verdict=PASS rc=0
[2026-10-04T20:01:33Z]   [ga_g01_028] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-04T20:01:33Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-04T20:01:33Z] gen 1: evaluating ga_g01_029 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T20:01:43Z]   [ga_g01_029] xcheck rc=0 XCHECK ga_g01_029: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T20:02:35Z]   [ga_g01_029] S0 delay=38.0 cells=4703 area=13341.0 verdict=PASS rc=0
[2026-10-04T20:02:35Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:07:35Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:12:35Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:17:35Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:22:35Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:27:36Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:32:36Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:37:36Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:42:36Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:47:36Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:52:36Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T20:57:36Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:02:36Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:13:42Z]   [ga_g01_029] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-04T21:13:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:18:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:23:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:28:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:33:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:38:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:43:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:48:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:53:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T21:58:42Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T22:10:32Z]   [ga_g01_029] S2 verdict=PASS max_repeats=0 max_z=11.2 rc=0 spikes=0
[2026-10-04T22:10:32Z]   [ga_g01_029] ARCHIVE-Q ENTER (provisional): (38.0, 4703, 13341) evicted=[]
[2026-10-04T22:12:32Z]   [ga_g01_029] S3 cfg1 rc=0
[2026-10-04T22:14:29Z]   [ga_g01_029] S3 cfg2 rc=0
[2026-10-04T22:14:29Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T22:20:43Z]   [ga_g01_029] S4 rc=0 passed=True
[2026-10-04T22:20:43Z]   [ga_g01_029] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T22:27:11Z]   [ga_g01_029] Q1 sac_z5=0 bic=0.17374
[2026-10-04T22:27:11Z]   [ga_g01_029] ARCHIVE-Q EVICT: bic=0.17374029560349072 > 0.02
[2026-10-04T22:27:11Z] gen 1: evaluating ga_g01_030 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_0F", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-04T22:27:46Z]   [ga_g01_030] xcheck rc=0 XCHECK ga_g01_030: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T22:27:46Z]   [ga_g01_030] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T22:32:46Z]   [ga_g01_030] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T22:37:46Z]   [ga_g01_030] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T22:46:28Z]   [ga_g01_030] S0 delay=45.0 cells=3615 area=10471.0 verdict=PASS rc=0
[2026-10-04T22:46:28Z]   [ga_g01_030] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T22:51:29Z]   [ga_g01_030] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T22:56:29Z]   [ga_g01_030] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T23:24:24Z] resumed at gen 1 evals=29 archiveS=5 archiveQ=1
[2026-10-04T23:24:24Z] gen 1: evaluating ga_g01_030 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-04T23:25:28Z]   [ga_g01_030] xcheck rc=0 XCHECK ga_g01_030: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T23:25:28Z]   [ga_g01_030] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T23:40:49Z]   [ga_g01_030] S0 delay=45.0 cells=3615 area=10471.0 verdict=PASS rc=1
[2026-10-04T23:40:49Z] gen 1: evaluating ga_g01_031 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-04T23:41:10Z]   [ga_g01_031] xcheck rc=0 XCHECK ga_g01_031: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-04T23:44:30Z]   [ga_g01_031] S0 delay=37.1 cells=4249 area=12275.0 verdict=PASS rc=0
[2026-10-04T23:44:30Z]   [ga_g01_031] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T23:49:30Z]   [ga_g01_031] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-04T23:57:48Z]   [ga_g01_031] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-05T00:17:41Z]   [ga_g01_031] S2 verdict=PASS max_repeats=0 max_z=27.7 rc=0 spikes=0
[2026-10-05T00:17:41Z]   [ga_g01_031] ARCHIVE-S ENTER (provisional): (37.1, 4249, 12275) evicted=['r20_feist6_alt_notr_keyin_nw']
[2026-10-05T00:17:41Z]   [ga_g01_031] ARCHIVE-Q ENTER (provisional): (37.1, 4249, 12275) evicted=[]
[2026-10-05T00:21:00Z]   [ga_g01_031] S3 cfg1 rc=0
[2026-10-05T00:21:00Z]   [ga_g01_031] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T00:29:22Z]   [ga_g01_031] S3 cfg2 rc=0
[2026-10-05T00:30:28Z]   [ga_g01_031] S4 rc=0 passed=True
[2026-10-05T00:31:37Z]   [ga_g01_031] Q1 sac_z5=10 bic=0.14842
[2026-10-05T00:31:37Z]   [ga_g01_031] ARCHIVE EVICT: Stage D failed at Q1
[2026-10-05T00:31:37Z]   death @Q1: HYPOTHESIS: avalanche failure (sac_z5=10) — insufficient bit diffusion across the 6 rounds.
[2026-10-05T00:31:37Z] gen 1: evaluating ga_g01_032 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-05T00:31:42Z]   [ga_g01_032] xcheck rc=0 XCHECK ga_g01_032: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T00:32:37Z]   [ga_g01_032] S0 delay=37.6 cells=4091 area=11693.0 verdict=PASS rc=0
[2026-10-05T00:34:49Z]   [ga_g01_032] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-05T00:42:45Z]   [ga_g01_032] S2 verdict=PASS max_repeats=0 max_z=17.1 rc=0 spikes=0
[2026-10-05T00:42:45Z]   [ga_g01_032] ARCHIVE-Q ENTER (provisional): (37.6, 4091, 11693) evicted=[]
[2026-10-05T00:44:41Z]   [ga_g01_032] S3 cfg1 rc=0
[2026-10-05T00:46:31Z]   [ga_g01_032] S3 cfg2 rc=0
[2026-10-05T00:47:16Z]   [ga_g01_032] S4 rc=0 passed=True
[2026-10-05T00:48:37Z]   [ga_g01_032] Q1 sac_z5=1 bic=0.18764
[2026-10-05T00:48:37Z]   [ga_g01_032] ARCHIVE EVICT: Stage D failed at Q1
[2026-10-05T00:48:37Z]   death @Q1: HYPOTHESIS: avalanche failure (sac_z5=1) — insufficient bit diffusion across the 6 rounds.
[2026-10-05T00:48:37Z] gen 1: evaluating ga_g01_033 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T00:49:10Z]   [ga_g01_033] xcheck rc=0 XCHECK ga_g01_033: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T00:52:41Z]   [ga_g01_033] S0 delay=46.9 cells=3823 area=11048.0 verdict=PASS rc=0
[2026-10-05T00:53:06Z]   [ga_g01_033] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T00:53:06Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T00:53:06Z] gen 1: evaluating ga_g01_034 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T00:53:21Z]   [ga_g01_034] xcheck rc=0 XCHECK ga_g01_034: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T00:54:41Z]   [ga_g01_034] S0 delay=39.8 cells=4416 area=12492.0 verdict=PASS rc=0
[2026-10-05T00:55:03Z]   [ga_g01_034] S1 verdict=FLAG rc=2 lin=10 diff=10 pb=0 rd=0
[2026-10-05T00:55:03Z]   death @S1: HYPOTHESIS: linear hull through the round linears (10 LIN rejections) — the (a,b) rotation pairs admit a high-bias linear trail at 6r.
[2026-10-05T00:55:03Z] gen 1: evaluating ga_g01_035 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T00:55:29Z]   [ga_g01_035] xcheck rc=0 XCHECK ga_g01_035: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T00:57:59Z]   [ga_g01_035] S0 delay=35.8 cells=3474 area=10068.0 verdict=PASS rc=0
[2026-10-05T00:59:08Z]   [ga_g01_035] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T00:59:08Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T00:59:08Z] gen 1: evaluating ga_g01_036 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-05T00:59:33Z]   [ga_g01_036] xcheck rc=0 XCHECK ga_g01_036: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T01:03:42Z]   [ga_g01_036] S0 delay=40.5 cells=4733 area=13530.0 verdict=PASS rc=0
[2026-10-05T01:05:13Z]   [ga_g01_036] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-05T01:19:46Z]   [ga_g01_036] S2 verdict=PASS max_repeats=0 max_z=14.1 rc=0 spikes=0
[2026-10-05T01:19:46Z]   [ga_g01_036] ARCHIVE-Q ENTER (provisional): (40.5, 4733, 13530) evicted=[]
[2026-10-05T01:24:37Z]   [ga_g01_036] S3 cfg1 rc=0
[2026-10-05T01:31:27Z]   [ga_g01_036] S3 cfg2 rc=0
[2026-10-05T01:33:22Z]   [ga_g01_036] S4 rc=0 passed=True
[2026-10-05T01:35:37Z]   [ga_g01_036] Q1 sac_z5=1 bic=0.03084
[2026-10-05T01:35:37Z]   [ga_g01_036] ARCHIVE EVICT: Stage D failed at Q1
[2026-10-05T01:35:37Z]   death @Q1: HYPOTHESIS: avalanche failure (sac_z5=1) — insufficient bit diffusion across the 6 rounds.
[2026-10-05T01:35:37Z] --- gen 2 done: pop=20 archiveS=4 archiveQ=1 evals=36 deaths=22
[2026-10-05T01:35:37Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T01:35:37Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T01:35:37Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T01:35:37Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T01:35:37Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T01:35:37Z]     assoc [S1] rounds=6: x18
[2026-10-05T01:35:37Z]     assoc [S1] pbox:between64/interleave64: x11
[2026-10-05T01:35:37Z]     assoc [S1] trunc-ish:chi_notr@r6: x10
[2026-10-05T01:35:37Z]     assoc [S1] chi_notrx1: x10
[2026-10-05T01:35:37Z]     assoc [S1] s1_311x2: x10
[2026-10-05T01:35:37Z]     assoc [S1] s1_311x3: x8
[2026-10-05T01:35:38Z] gen 2: evaluating ga_g02_037 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:37:22Z]   [ga_g02_037] xcheck rc=0 XCHECK ga_g02_037: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T01:40:54Z]   [ga_g02_037] S0 delay=43.0 cells=3603 area=10388.0 verdict=PASS rc=0
[2026-10-05T01:41:19Z]   [ga_g02_037] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T01:41:20Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T01:41:20Z] gen 2: evaluating ga_g02_038 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_FF", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T01:41:20Z]   [ga_g02_038] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccQJiogQ.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g02_038/impl.c:261:1: fatal error: error writing to /tmp/ccQJiogQ.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:20Z] gen 2: evaluating ga_g02_039 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_SP", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:20Z]   [ga_g02_039] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cc2RjAp7.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g02_039/impl.c:261:1: fatal error: error writing to /tmp/cc2RjAp7.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:20Z] gen 2: evaluating ga_g02_040 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-05T01:41:21Z]   [ga_g02_040] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccvMN5d5.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g02_040/impl.c:160:1: fatal error: error writing to /tmp/ccvMN5d5.s: No space left on device
  160 | }
      | ^
compilation terminated.

[2026-10-05T01:41:21Z] gen 2: evaluating ga_g02_041 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T01:41:21Z]   [ga_g02_041] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccYpjAAn.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g02_041/impl.c:255:1: fatal error: error writing to /tmp/ccYpjAAn.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:21Z] gen 2: evaluating ga_g02_042 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:22Z]   [ga_g02_042] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccwMBniv.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g02_042/impl.c:261:1: fatal error: error writing to /tmp/ccwMBniv.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:22Z] gen 2: evaluating ga_g02_043 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-05T01:41:24Z]   [ga_g02_043] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccg8Fgto.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g02_043/impl.c:189:1: fatal error: error writing to /tmp/ccg8Fgto.s: No space left on device
  189 | }
      | ^
compilation terminated.

[2026-10-05T01:41:24Z] gen 2: evaluating ga_g02_044 via crossover {"const_fam": null, "const_where": "none", "mask": "r1_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:24Z]   [ga_g02_044] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cccnXoox.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g02_044/impl.c:261:1: fatal error: error writing to /tmp/cccnXoox.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:24Z] --- gen 3 done: pop=20 archiveS=4 archiveQ=1 evals=44 deaths=23
[2026-10-05T01:41:24Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T01:41:24Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T01:41:24Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T01:41:24Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T01:41:24Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T01:41:24Z]     assoc [S1] rounds=6: x19
[2026-10-05T01:41:24Z]     assoc [S1] pbox:between64/interleave64: x12
[2026-10-05T01:41:24Z]     assoc [S1] trunc-ish:chi_notr@r6: x11
[2026-10-05T01:41:24Z]     assoc [S1] chi_notrx1: x11
[2026-10-05T01:41:24Z]     assoc [S1] s1_311x2: x10
[2026-10-05T01:41:24Z]     assoc [S1] s1_311x3: x9
[2026-10-05T01:41:25Z] gen 3: evaluating ga_g03_045 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:26Z]   [ga_g03_045] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccmOllSj.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g03_045/impl.c:261:1: fatal error: error writing to /tmp/ccmOllSj.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:26Z] gen 3: evaluating ga_g03_046 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_SP", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-05T01:41:27Z]   [ga_g03_046] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccrEyL31.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g03_046/impl.c:189:1: fatal error: error writing to /tmp/ccrEyL31.s: No space left on device
  189 | }
      | ^
compilation terminated.

[2026-10-05T01:41:27Z] gen 3: evaluating ga_g03_047 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_A5", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T01:41:28Z]   [ga_g03_047] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccJwxLzF.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g03_047/impl.c:261:1: fatal error: error writing to /tmp/ccJwxLzF.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:28Z] gen 3: evaluating ga_g03_048 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "nibrev64", "pbox_where": "between64", "rounds"...
[2026-10-05T01:41:29Z]   [ga_g03_048] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccG3l8od.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g03_048/impl.c:261:1: fatal error: error writing to /tmp/ccG3l8od.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:29Z] gen 3: evaluating ga_g03_049 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-05T01:41:30Z]   [ga_g03_049] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cch1dp7W.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g03_049/impl.c:189:1: fatal error: error writing to /tmp/cch1dp7W.s: No space left on device
  189 | }
      | ^
compilation terminated.

[2026-10-05T01:41:30Z] gen 3: evaluating ga_g03_050 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T01:41:30Z]   [ga_g03_050] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cc6dxsPa.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g03_050/impl.c:261:1: fatal error: error writing to /tmp/cc6dxsPa.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:30Z] gen 3: evaluating ga_g03_051 via crossover {"const_fam": null, "const_where": "none", "mask": "r1_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:31Z]   [ga_g03_051] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccBROpt5.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g03_051/impl.c:261:1: fatal error: error writing to /tmp/ccBROpt5.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:31Z] gen 3: evaluating ga_g03_052 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": "rot64_32", "pbox_where": "between64", "rounds"...
[2026-10-05T01:41:32Z]   [ga_g03_052] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccahDIUv.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g03_052/impl.c:261:1: fatal error: error writing to /tmp/ccahDIUv.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:32Z] --- gen 4 done: pop=20 archiveS=4 archiveQ=1 evals=52 deaths=23
[2026-10-05T01:41:32Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T01:41:32Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T01:41:32Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T01:41:32Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T01:41:32Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T01:41:32Z]     assoc [S1] rounds=6: x19
[2026-10-05T01:41:32Z]     assoc [S1] pbox:between64/interleave64: x12
[2026-10-05T01:41:32Z]     assoc [S1] trunc-ish:chi_notr@r6: x11
[2026-10-05T01:41:32Z]     assoc [S1] chi_notrx1: x11
[2026-10-05T01:41:32Z]     assoc [S1] s1_311x2: x10
[2026-10-05T01:41:32Z]     assoc [S1] s1_311x3: x9
[2026-10-05T01:41:32Z] gen 4: evaluating ga_g04_053 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_FF", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "ro...
[2026-10-05T01:41:33Z]   [ga_g04_053] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccqGRRwi.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g04_053/impl.c:229:1: fatal error: error writing to /tmp/ccqGRRwi.s: No space left on device
  229 | }
      | ^
compilation terminated.

[2026-10-05T01:41:33Z] gen 4: evaluating ga_g04_054 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:34Z]   [ga_g04_054] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cc0S0Y2w.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g04_054/impl.c:261:1: fatal error: error writing to /tmp/cc0S0Y2w.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:34Z] gen 4: evaluating ga_g04_055 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-05T01:41:34Z]   [ga_g04_055] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccZHaL8z.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g04_055/impl.c:160:1: fatal error: error writing to /tmp/ccZHaL8z.s: No space left on device
  160 | }
      | ^
compilation terminated.

[2026-10-05T01:41:34Z] gen 4: evaluating ga_g04_056 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T01:41:35Z]   [ga_g04_056] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccxIQFog.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g04_056/impl.c:223:1: fatal error: error writing to /tmp/ccxIQFog.s: No space left on device
  223 | }
      | ^
compilation terminated.

[2026-10-05T01:41:35Z] gen 4: evaluating ga_g04_057 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_SP", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:36Z]   [ga_g04_057] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccrI9kn1.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g04_057/impl.c:261:1: fatal error: error writing to /tmp/ccrI9kn1.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:36Z] gen 4: evaluating ga_g04_058 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:41:37Z]   [ga_g04_058] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccQPU5pj.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g04_058/impl.c:259:1: fatal error: error writing to /tmp/ccQPU5pj.s: No space left on device
  259 | }
      | ^
compilation terminated.

[2026-10-05T01:41:37Z] --- gen 5 done: pop=20 archiveS=4 archiveQ=1 evals=58 deaths=23
[2026-10-05T01:41:37Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T01:41:37Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T01:41:37Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T01:41:37Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T01:41:37Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T01:41:37Z]     assoc [S1] rounds=6: x19
[2026-10-05T01:41:37Z]     assoc [S1] pbox:between64/interleave64: x12
[2026-10-05T01:41:37Z]     assoc [S1] trunc-ish:chi_notr@r6: x11
[2026-10-05T01:41:37Z]     assoc [S1] chi_notrx1: x11
[2026-10-05T01:41:37Z]     assoc [S1] s1_311x2: x10
[2026-10-05T01:41:37Z]     assoc [S1] s1_311x3: x9
[2026-10-05T01:41:37Z] gen 5: evaluating ga_g05_059 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:37Z]   [ga_g05_059] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccyGISq6.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g05_059/impl.c:261:1: fatal error: error writing to /tmp/ccyGISq6.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:37Z] gen 5: evaluating ga_g05_060 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_FF", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:38Z]   [ga_g05_060] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cclkgbo4.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g05_060/impl.c:261:1: fatal error: error writing to /tmp/cclkgbo4.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:38Z] gen 5: evaluating ga_g05_061 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot32_16", "pbox_where": "replacerot", "rounds"...
[2026-10-05T01:41:39Z]   [ga_g05_061] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cc63kz4d.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g05_061/impl.c:223:1: fatal error: error writing to /tmp/cc63kz4d.s: No space left on device
  223 | }
      | ^
compilation terminated.

[2026-10-05T01:41:39Z] gen 5: evaluating ga_g05_062 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:41:41Z]   [ga_g05_062] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccLiwNtC.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g05_062/impl.c:255:1: fatal error: error writing to /tmp/ccLiwNtC.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:41Z] gen 5: evaluating ga_g05_063 via guided(Q1:guided_diffusion) {"const_fam": null, "const_where": "none", "mask": "r3_A5", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-05T01:41:41Z]   [ga_g05_063] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cciuFdyg.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g05_063/impl.c:189:1: fatal error: error writing to /tmp/cciuFdyg.s: No space left on device
  189 | }
      | ^
compilation terminated.

[2026-10-05T01:41:41Z] gen 5: evaluating ga_g05_064 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_SP", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:42Z]   [ga_g05_064] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccl0Cjjb.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g05_064/impl.c:261:1: fatal error: error writing to /tmp/ccl0Cjjb.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:42Z] gen 5: evaluating ga_g05_065 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-05T01:41:43Z]   [ga_g05_065] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccHgdEWX.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g05_065/impl.c:189:1: fatal error: error writing to /tmp/ccHgdEWX.s: No space left on device
  189 | }
      | ^
compilation terminated.

[2026-10-05T01:41:43Z] gen 5: evaluating ga_g05_066 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-05T01:41:43Z]   [ga_g05_066] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccdG6PcI.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g05_066/impl.c:160:1: fatal error: error writing to /tmp/ccdG6PcI.s: No space left on device
  160 | }
      | ^
compilation terminated.

[2026-10-05T01:41:43Z] gen 5: evaluating ga_g05_067 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T01:41:44Z]   [ga_g05_067] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccUWQC5t.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g05_067/impl.c:223:1: fatal error: error writing to /tmp/ccUWQC5t.s: No space left on device
  223 | }
      | ^
compilation terminated.

[2026-10-05T01:41:44Z] --- gen 6 done: pop=20 archiveS=4 archiveQ=1 evals=67 deaths=23
[2026-10-05T01:41:44Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T01:41:44Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T01:41:44Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T01:41:44Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T01:41:44Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T01:41:44Z]     assoc [S1] rounds=6: x19
[2026-10-05T01:41:44Z]     assoc [S1] pbox:between64/interleave64: x12
[2026-10-05T01:41:44Z]     assoc [S1] trunc-ish:chi_notr@r6: x11
[2026-10-05T01:41:44Z]     assoc [S1] chi_notrx1: x11
[2026-10-05T01:41:44Z]     assoc [S1] s1_311x2: x10
[2026-10-05T01:41:44Z]     assoc [S1] s1_311x3: x9
[2026-10-05T01:41:44Z] gen 6: evaluating ga_g06_068 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:41:45Z]   [ga_g06_068] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccRCoRVP.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g06_068/impl.c:255:1: fatal error: error writing to /tmp/ccRCoRVP.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:45Z] gen 6: evaluating ga_g06_069 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "nibrev64", "pbox_where": "between64", "rounds":...
[2026-10-05T01:41:45Z]   [ga_g06_069] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cc6MakYp.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g06_069/impl.c:255:1: fatal error: error writing to /tmp/cc6MakYp.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:45Z] gen 6: evaluating ga_g06_070 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_0F", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T01:41:46Z]   [ga_g06_070] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cc8iP9zq.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g06_070/impl.c:261:1: fatal error: error writing to /tmp/cc8iP9zq.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:46Z] gen 6: evaluating ga_g06_071 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T01:41:47Z]   [ga_g06_071] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccPa9uXq.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g06_071/impl.c:255:1: fatal error: error writing to /tmp/ccPa9uXq.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:47Z] gen 6: evaluating ga_g06_072 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x8", "pbox_where": "between64", "roun...
[2026-10-05T01:41:48Z]   [ga_g06_072] build diffprof FAILED rc=1: idates/ga_g06_072/impl.c:210:39: warning: left shift count >= width of type [-Wshift-count-overflow]
  210 |     r |= ((uint32_t)((x >> 63) & 1u)) << 63;
      |                                       ^~
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g06_072/impl.c: At top level:
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g06_072/impl.c:255:1: fatal error: error writing to /tmp/cclrXRzj.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:48Z] gen 6: evaluating ga_g06_073 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "bitrev32", "pbox_where": "replacerot", "rounds"...
[2026-10-05T01:41:48Z]   [ga_g06_073] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cco2S8QE.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g06_073/impl.c:223:1: fatal error: error writing to /tmp/cco2S8QE.s: No space left on device
  223 | }
      | ^
compilation terminated.

[2026-10-05T01:41:48Z] gen 6: evaluating ga_g06_074 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T01:41:49Z]   [ga_g06_074] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccpIfkB4.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g06_074/impl.c:261:1: fatal error: error writing to /tmp/ccpIfkB4.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:49Z] gen 6: evaluating ga_g06_075 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T01:41:50Z]   [ga_g06_075] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cchSwF62.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g06_075/impl.c:261:1: fatal error: error writing to /tmp/cchSwF62.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:50Z] --- gen 7 done: pop=20 archiveS=4 archiveQ=1 evals=75 deaths=23
[2026-10-05T01:41:50Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T01:41:50Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T01:41:50Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T01:41:50Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T01:41:50Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T01:41:50Z]     assoc [S1] rounds=6: x19
[2026-10-05T01:41:50Z]     assoc [S1] pbox:between64/interleave64: x12
[2026-10-05T01:41:50Z]     assoc [S1] trunc-ish:chi_notr@r6: x11
[2026-10-05T01:41:50Z]     assoc [S1] chi_notrx1: x11
[2026-10-05T01:41:50Z]     assoc [S1] s1_311x2: x10
[2026-10-05T01:41:50Z]     assoc [S1] s1_311x3: x9
[2026-10-05T01:41:50Z] gen 7: evaluating ga_g07_076 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:51Z]   [ga_g07_076] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccUbSPnl.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g07_076/impl.c:261:1: fatal error: error writing to /tmp/ccUbSPnl.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:51Z] gen 7: evaluating ga_g07_077 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "nibrev64", "pbox_where": "between64", "rounds":...
[2026-10-05T01:41:51Z]   [ga_g07_077] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccyaksWR.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g07_077/impl.c:255:1: fatal error: error writing to /tmp/ccyaksWR.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:51Z] gen 7: evaluating ga_g07_078 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:41:52Z]   [ga_g07_078] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccOsVIta.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g07_078/impl.c:255:1: fatal error: error writing to /tmp/ccOsVIta.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:52Z] gen 7: evaluating ga_g07_079 via guided(S1:guided_linear) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T01:41:53Z]   [ga_g07_079] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccYhhkBK.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g07_079/impl.c:224:1: fatal error: error writing to /tmp/ccYhhkBK.s: No space left on device
  224 | }
      | ^
compilation terminated.

[2026-10-05T01:41:53Z] gen 7: evaluating ga_g07_080 via guided(S1:guided_linear) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T01:41:54Z]   [ga_g07_080] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cch6ShdQ.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g07_080/impl.c:223:1: fatal error: error writing to /tmp/cch6ShdQ.s: No space left on device
  223 | }
      | ^
compilation terminated.

[2026-10-05T01:41:54Z] gen 7: evaluating ga_g07_081 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-05T01:41:54Z]   [ga_g07_081] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccw1QmbG.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g07_081/impl.c:160:1: fatal error: error writing to /tmp/ccw1QmbG.s: No space left on device
  160 | }
      | ^
compilation terminated.

[2026-10-05T01:41:54Z] --- gen 8 done: pop=20 archiveS=4 archiveQ=1 evals=81 deaths=23
[2026-10-05T01:41:54Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T01:41:54Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T01:41:54Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T01:41:54Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T01:41:54Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T01:41:54Z]     assoc [S1] rounds=6: x19
[2026-10-05T01:41:54Z]     assoc [S1] pbox:between64/interleave64: x12
[2026-10-05T01:41:54Z]     assoc [S1] trunc-ish:chi_notr@r6: x11
[2026-10-05T01:41:54Z]     assoc [S1] chi_notrx1: x11
[2026-10-05T01:41:54Z]     assoc [S1] s1_311x2: x10
[2026-10-05T01:41:54Z]     assoc [S1] s1_311x3: x9
[2026-10-05T01:41:54Z] gen 8: evaluating ga_g08_082 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:55Z]   [ga_g08_082] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccwbX6XO.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g08_082/impl.c:261:1: fatal error: error writing to /tmp/ccwbX6XO.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:55Z] gen 8: evaluating ga_g08_083 via guided(Q1:guided_diffusion) {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": "rot64_32", "pbox_where": "between64", "rounds"...
[2026-10-05T01:41:56Z]   [ga_g08_083] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccBTXlZv.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g08_083/impl.c:261:1: fatal error: error writing to /tmp/ccBTXlZv.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:56Z] gen 8: evaluating ga_g08_084 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "bitrev64", "pbox_where": "between64", "rounds":...
[2026-10-05T01:41:57Z]   [ga_g08_084] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccuJOIa4.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g08_084/impl.c:255:1: fatal error: error writing to /tmp/ccuJOIa4.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:57Z] gen 8: evaluating ga_g08_085 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:57Z]   [ga_g08_085] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccW7LvBs.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g08_085/impl.c:261:1: fatal error: error writing to /tmp/ccW7LvBs.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:57Z] gen 8: evaluating ga_g08_086 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:41:58Z]   [ga_g08_086] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cceVU9o1.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g08_086/impl.c:261:1: fatal error: error writing to /tmp/cceVU9o1.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:41:58Z] gen 8: evaluating ga_g08_087 via guided(Q1:guided_diffusion) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-05T01:41:59Z]   [ga_g08_087] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccEDV3BF.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g08_087/impl.c:160:1: fatal error: error writing to /tmp/ccEDV3BF.s: No space left on device
  160 | }
      | ^
compilation terminated.

[2026-10-05T01:41:59Z] --- gen 9 done: pop=20 archiveS=4 archiveQ=1 evals=87 deaths=23
[2026-10-05T01:41:59Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T01:41:59Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T01:41:59Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T01:41:59Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T01:41:59Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T01:41:59Z]     assoc [S1] rounds=6: x19
[2026-10-05T01:41:59Z]     assoc [S1] pbox:between64/interleave64: x12
[2026-10-05T01:41:59Z]     assoc [S1] trunc-ish:chi_notr@r6: x11
[2026-10-05T01:41:59Z]     assoc [S1] chi_notrx1: x11
[2026-10-05T01:41:59Z]     assoc [S1] s1_311x2: x10
[2026-10-05T01:41:59Z]     assoc [S1] s1_311x3: x9
[2026-10-05T01:41:59Z] gen 9: evaluating ga_g09_088 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T01:41:59Z]   [ga_g09_088] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccdnZoQ2.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g09_088/impl.c:255:1: fatal error: error writing to /tmp/ccdnZoQ2.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:41:59Z] gen 9: evaluating ga_g09_089 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T01:42:00Z]   [ga_g09_089] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccdWPnsk.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g09_089/impl.c:261:1: fatal error: error writing to /tmp/ccdWPnsk.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:42:00Z] gen 9: evaluating ga_g09_090 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:42:01Z]   [ga_g09_090] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccMRiJmn.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g09_090/impl.c:255:1: fatal error: error writing to /tmp/ccMRiJmn.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:42:01Z] gen 9: evaluating ga_g09_091 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:42:01Z]   [ga_g09_091] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccLta4Lq.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g09_091/impl.c:261:1: fatal error: error writing to /tmp/ccLta4Lq.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:42:01Z] gen 9: evaluating ga_g09_092 via guided(S1:guided_linear) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T01:42:02Z]   [ga_g09_092] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccnzSyNL.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g09_092/impl.c:224:1: fatal error: error writing to /tmp/ccnzSyNL.s: No space left on device
  224 | }
      | ^
compilation terminated.

[2026-10-05T01:42:02Z] gen 9: evaluating ga_g09_093 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:42:02Z]   [ga_g09_093] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccG2hmup.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g09_093/impl.c:255:1: fatal error: error writing to /tmp/ccG2hmup.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:42:02Z] gen 9: evaluating ga_g09_094 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "bitrev64", "pbox_where": "between64", "rounds":...
[2026-10-05T01:42:03Z]   [ga_g09_094] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccB2nxLw.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g09_094/impl.c:255:1: fatal error: error writing to /tmp/ccB2nxLw.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:42:03Z] gen 9: evaluating ga_g09_095 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags":...
[2026-10-05T01:42:03Z]   [ga_g09_095] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cchB1xmW.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g09_095/impl.c:160:1: fatal error: error closing /tmp/cchB1xmW.s: No space left on device
  160 | }
      | ^
compilation terminated.

[2026-10-05T01:42:03Z] --- gen 10 done: pop=20 archiveS=4 archiveQ=1 evals=95 deaths=23
[2026-10-05T01:42:03Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T01:42:03Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T01:42:03Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T01:42:03Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T01:42:03Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T01:42:03Z]     assoc [S1] rounds=6: x19
[2026-10-05T01:42:03Z]     assoc [S1] pbox:between64/interleave64: x12
[2026-10-05T01:42:03Z]     assoc [S1] trunc-ish:chi_notr@r6: x11
[2026-10-05T01:42:03Z]     assoc [S1] chi_notrx1: x11
[2026-10-05T01:42:03Z]     assoc [S1] s1_311x2: x10
[2026-10-05T01:42:03Z]     assoc [S1] s1_311x3: x9
[2026-10-05T01:42:03Z] gen 10: evaluating ga_g10_096 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_FF", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:42:04Z]   [ga_g10_096] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccCfKfs4.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g10_096/impl.c:261:1: fatal error: error writing to /tmp/ccCfKfs4.s: No space left on device
  261 | }
      | ^
compilation terminated.

[2026-10-05T01:42:04Z] gen 10: evaluating ga_g10_097 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:42:05Z]   [ga_g10_097] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/ccqyF8X1.s: No space left on device
  161 | }
      | ^
compilation terminated.
/home/hatch/workspace/mix/exploration/fast_battery/candidates/ga_g10_097/impl.c:255:1: fatal error: error writing to /tmp/ccqyF8X1.s: No space left on device
  255 | }
      | ^
compilation terminated.

[2026-10-05T01:42:05Z] gen 10: evaluating ga_g10_098 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:42:05Z]   [ga_g10_098] build diffprof FAILED rc=1: /home/hatch/workspace/mix/exploration/fast_battery/src/s2_diffprof.c:161:1: fatal error: error writing to /tmp/cc6Ax9zr.s: No space left on device
  161 | }
      | ^
compilation terminated.

[2026-10-05T01:42:05Z] gen 10: evaluating ga_g10_099 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:42:35Z]   [ga_g10_099] xcheck rc=0 XCHECK ga_g10_099: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T01:47:32Z]   [ga_g10_099] S0 delay=39.6 cells=3369 area=9732.0 verdict=PASS rc=0
[2026-10-05T01:47:53Z]   [ga_g10_099] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T01:47:53Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T01:47:53Z] gen 10: evaluating ga_g10_100 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_FF", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T01:48:17Z]   [ga_g10_100] xcheck rc=0 XCHECK ga_g10_100: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T01:49:51Z]   [ga_g10_100] S0 delay=35.9 cells=4210 area=11949.0 verdict=PASS rc=0
[2026-10-05T01:50:13Z]   [ga_g10_100] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T01:50:13Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T01:50:13Z] gen 10: evaluating ga_g10_101 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T01:50:44Z]   [ga_g10_101] xcheck rc=0 XCHECK ga_g10_101: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T01:55:34Z]   [ga_g10_101] S0 delay=37.2 cells=3383 area=9741.0 verdict=PASS rc=0
[2026-10-05T01:55:55Z]   [ga_g10_101] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T01:55:55Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T01:55:55Z] gen 10: evaluating ga_g10_102 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T01:56:17Z]   [ga_g10_102] xcheck rc=0 XCHECK ga_g10_102: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T01:59:35Z]   [ga_g10_102] S0 delay=44.5 cells=3648 area=10652.0 verdict=PASS rc=0
[2026-10-05T02:00:06Z]   [ga_g10_102] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T02:00:06Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T02:00:06Z] gen 10: evaluating ga_g10_103 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_FF", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T02:00:50Z]   [ga_g10_103] xcheck rc=0 XCHECK ga_g10_103: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:05:29Z]   [ga_g10_103] S0 delay=47.8 cells=4374 area=12614.0 verdict=PASS rc=0
[2026-10-05T02:05:29Z]   [ga_g10_103] Stage-A discard: dominated by both archives
[2026-10-05T02:05:29Z] gen 10: evaluating ga_g10_104 via guided(Q1:guided_diffusion) {"const_fam": null, "const_where": "none", "mask": "r1_A5", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-05T02:05:35Z]   [ga_g10_104] xcheck rc=0 XCHECK ga_g10_104: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:07:18Z]   [ga_g10_104] S0 delay=43.4 cells=4697 area=13110.0 verdict=PASS rc=0
[2026-10-05T02:07:18Z]   [ga_g10_104] Stage-A discard: dominated by both archives
[2026-10-05T02:07:18Z] --- gen 11 done: pop=20 archiveS=4 archiveQ=1 evals=104 deaths=27
[2026-10-05T02:07:18Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T02:07:18Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T02:07:18Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T02:07:18Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T02:07:18Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T02:07:18Z]     assoc [S1] rounds=6: x23
[2026-10-05T02:07:18Z]     assoc [S1] pbox:between64/interleave64: x15
[2026-10-05T02:07:18Z]     assoc [S1] trunc-ish:chi_notr@r6: x14
[2026-10-05T02:07:18Z]     assoc [S1] chi_notrx1: x14
[2026-10-05T02:07:18Z]     assoc [S1] s1_311x3: x11
[2026-10-05T02:07:18Z]     assoc [S1] s1_311x2: x11
[2026-10-05T02:07:18Z] gen 11: evaluating ga_g11_105 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T02:07:43Z]   [ga_g11_105] xcheck rc=0 XCHECK ga_g11_105: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:08:48Z]   [ga_g11_105] S0 delay=37.4 cells=4298 area=12378.0 verdict=PASS rc=0
[2026-10-05T02:09:59Z]   [ga_g11_105] S1 verdict=FLAG rc=2 lin=10 diff=4 pb=0 rd=0
[2026-10-05T02:09:59Z]   death @S1: HYPOTHESIS: linear hull through the round linears (10 LIN rejections) — the (a,b) rotation pairs admit a high-bias linear trail at 6r.
[2026-10-05T02:09:59Z] gen 11: evaluating ga_g11_106 via crossover {"const_fam": null, "const_where": "none", "mask": "r2_FF", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-05T02:10:20Z]   [ga_g11_106] xcheck rc=0 XCHECK ga_g11_106: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:24:50Z] resumed at gen 11 evals=105 archiveS=4 archiveQ=1
[2026-10-05T02:24:50Z] gen 11: evaluating ga_g11_106 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "tags"...
[2026-10-05T02:24:55Z]   [ga_g11_106] xcheck rc=0 XCHECK ga_g11_106: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:27:17Z]   [ga_g11_106] S0 delay=42.9 cells=4743 area=13464.0 verdict=PASS rc=0
[2026-10-05T02:27:17Z]   [ga_g11_106] Stage-A discard: dominated by both archives
[2026-10-05T02:27:17Z] gen 11: evaluating ga_g11_107 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T02:28:02Z]   [ga_g11_107] xcheck rc=0 XCHECK ga_g11_107: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:30:39Z]   [ga_g11_107] S0 delay=45.3 cells=3534 area=10219.0 verdict=PASS rc=0
[2026-10-05T02:31:09Z]   [ga_g11_107] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T02:31:09Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T02:31:09Z] gen 11: evaluating ga_g11_108 via guided(S1:guided_linear) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T02:31:30Z]   [ga_g11_108] xcheck rc=0 XCHECK ga_g11_108: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:32:13Z]   [ga_g11_108] S0 delay=37.7 cells=4244 area=12079.0 verdict=PASS rc=0
[2026-10-05T02:32:45Z]   [ga_g11_108] S1 verdict=FLAG rc=2 lin=10 diff=10 pb=0 rd=0
[2026-10-05T02:32:45Z]   death @S1: HYPOTHESIS: linear hull through the round linears (10 LIN rejections) — the (a,b) rotation pairs admit a high-bias linear trail at 6r.
[2026-10-05T02:32:45Z] --- gen 12 done: pop=20 archiveS=4 archiveQ=1 evals=108 deaths=30
[2026-10-05T02:32:45Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T02:32:45Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T02:32:45Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T02:32:45Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T02:32:45Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T02:32:45Z]     assoc [S1] rounds=6: x26
[2026-10-05T02:32:45Z]     assoc [S1] pbox:between64/interleave64: x16
[2026-10-05T02:32:45Z]     assoc [S1] trunc-ish:chi_notr@r6: x14
[2026-10-05T02:32:45Z]     assoc [S1] chi_notrx1: x14
[2026-10-05T02:32:45Z]     assoc [S1] s1_311x3: x13
[2026-10-05T02:32:45Z]     assoc [S1] s1_311x2: x12
[2026-10-05T02:32:45Z] gen 12: evaluating ga_g12_109 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T02:34:24Z]   [ga_g12_109] xcheck rc=0 XCHECK ga_g12_109: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:38:50Z]   [ga_g12_109] S0 delay=39.3 cells=3649 area=10454.0 verdict=PASS rc=0
[2026-10-05T02:39:55Z]   [ga_g12_109] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T02:39:55Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T02:39:55Z] gen 12: evaluating ga_g12_110 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_FF", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T02:41:46Z]   [ga_g12_110] xcheck rc=0 XCHECK ga_g12_110: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:52:09Z]   [ga_g12_110] S0 no result json: [Errno 2] No such file or directory: '/home/hatch/workspace/mix/exploration/ga/results/ga_g12_110/s0_result.json'; rc=1
[2026-10-05T02:52:09Z] gen 12: evaluating ga_g12_111 via guided(S1:None) {"const_fam": "iota", "const_where": "round_F", "mask": "r1_A5", "pbox_perm": null, "pbox_where": "none", "rounds": 6, "...
[2026-10-05T02:52:34Z]   [ga_g12_111] xcheck rc=0 XCHECK ga_g12_111: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:57:00Z]   [ga_g12_111] S0 delay=43.0 cells=4957 area=14020.0 verdict=PASS rc=0
[2026-10-05T02:57:00Z]   [ga_g12_111] Stage-A discard: dominated by both archives
[2026-10-05T02:57:00Z] gen 12: evaluating ga_g12_112 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x8", "pbox_where": "between64", "roun...
[2026-10-05T02:59:31Z]   [ga_g12_112] xcheck rc=1 ffdda k=f26fff4cc4fd394d C=96171f27020c050e py=d5b07cee2a1b6039
XCHECK ga_g12_112: FAIL 10000/10000 mismatches
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T02:59:31Z] gen 12: evaluating ga_g12_113 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T03:01:00Z]   [ga_g12_113] xcheck rc=0 XCHECK ga_g12_113: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T03:06:56Z]   [ga_g12_113] S0 delay=43.7 cells=4731 area=13442.0 verdict=PASS rc=0
[2026-10-05T03:06:56Z]   [ga_g12_113] Stage-A discard: dominated by both archives
[2026-10-05T03:06:56Z] gen 12: evaluating ga_g12_114 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "bitrev64", "pbox_where": "between64", "rounds":...
[2026-10-05T03:09:30Z]   [ga_g12_114] xcheck rc=0 XCHECK ga_g12_114: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T03:09:41Z]   [ga_g12_114] S0 no result json: [Errno 2] No such file or directory: '/home/hatch/workspace/mix/exploration/ga/results/ga_g12_114/s0_result.json'; rc=1
[2026-10-05T03:09:41Z] gen 12: evaluating ga_g12_115 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T03:11:21Z]   [ga_g12_115] xcheck rc=0 XCHECK ga_g12_115: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T03:18:06Z]   [ga_g12_115] S0 delay=39.0 cells=3398 area=9808.0 verdict=PASS rc=0
[2026-10-05T03:19:12Z]   [ga_g12_115] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T03:19:12Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T03:19:12Z] --- gen 13 done: pop=20 archiveS=4 archiveQ=1 evals=115 deaths=32
[2026-10-05T03:19:12Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T03:19:12Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T03:19:12Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T03:19:12Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T03:19:12Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T03:19:12Z]     assoc [S1] rounds=6: x28
[2026-10-05T03:19:12Z]     assoc [S1] pbox:between64/interleave64: x17
[2026-10-05T03:19:12Z]     assoc [S1] trunc-ish:chi_notr@r6: x16
[2026-10-05T03:19:12Z]     assoc [S1] chi_notrx1: x16
[2026-10-05T03:19:12Z]     assoc [S1] s1_311x3: x14
[2026-10-05T03:19:12Z]     assoc [S1] s1_311x2: x13
[2026-10-05T03:19:13Z] gen 13: evaluating ga_g13_116 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T03:20:31Z]   [ga_g13_116] xcheck rc=0 XCHECK ga_g13_116: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T03:28:19Z]   [ga_g13_116] S0 delay=43.0 cells=3662 area=10517.0 verdict=PASS rc=0
[2026-10-05T03:30:08Z]   [ga_g13_116] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T03:30:08Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T03:30:08Z] gen 13: evaluating ga_g13_117 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T03:33:26Z]   [ga_g13_117] xcheck rc=0 XCHECK ga_g13_117: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T03:41:52Z]   [ga_g13_117] S0 delay=39.6 cells=3401 area=9770.0 verdict=PASS rc=0
[2026-10-05T03:44:01Z]   [ga_g13_117] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T03:44:01Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T03:44:01Z] gen 13: evaluating ga_g13_118 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T03:46:11Z]   [ga_g13_118] xcheck rc=0 XCHECK ga_g13_118: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T03:55:25Z]   [ga_g13_118] S0 delay=36.5 cells=3685 area=10640.0 verdict=PASS rc=0
[2026-10-05T03:56:53Z]   [ga_g13_118] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T03:56:53Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T03:56:53Z] gen 13: evaluating ga_g13_119 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T03:59:33Z]   [ga_g13_119] xcheck rc=0 XCHECK ga_g13_119: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T04:02:56Z]   [ga_g13_119] S0 delay=30.8 cells=2923 area=8380.0 verdict=PASS rc=0
[2026-10-05T04:04:21Z]   [ga_g13_119] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T04:04:21Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T04:04:21Z] gen 13: evaluating ga_g13_120 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T04:06:44Z]   [ga_g13_120] xcheck rc=0 XCHECK ga_g13_120: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T04:14:34Z]   [ga_g13_120] S0 delay=39.5 cells=3568 area=10134.0 verdict=PASS rc=0
[2026-10-05T04:16:14Z]   [ga_g13_120] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T04:16:14Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T04:16:14Z] gen 13: evaluating ga_g13_121 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T04:17:32Z]   [ga_g13_121] xcheck rc=0 XCHECK ga_g13_121: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T04:27:50Z]   [ga_g13_121] S0 no result json: [Errno 2] No such file or directory: '/home/hatch/workspace/mix/exploration/ga/results/ga_g13_121/s0_result.json'; rc=1
[2026-10-05T04:27:50Z] gen 13: evaluating ga_g13_122 via mutate {"const_fam": null, "const_where": "none", "mask": "r2_H2", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "ro...
[2026-10-05T04:29:18Z]   [ga_g13_122] xcheck rc=0 XCHECK ga_g13_122: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T04:29:18Z]   [ga_g13_122] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T04:44:49Z]   [ga_g13_122] S0 no result json: [Errno 2] No such file or directory: '/home/hatch/workspace/mix/exploration/ga/results/ga_g13_122/s0_result.json'; rc=1
[2026-10-05T04:44:49Z] gen 13: evaluating ga_g13_123 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_0F", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T04:48:35Z]   [ga_g13_123] xcheck rc=0 XCHECK ga_g13_123: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T04:48:35Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T04:53:35Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T04:58:35Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:03:35Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:08:35Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:13:35Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:28:04Z] resumed at gen 13 evals=122 archiveS=4 archiveQ=1
[2026-10-05T05:28:05Z] gen 13: evaluating ga_g13_123 via guided(S1:guided_linear) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T05:29:33Z]   [ga_g13_123] xcheck rc=0 XCHECK ga_g13_123: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T05:29:33Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:34:33Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:39:33Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:44:33Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:49:33Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:54:33Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T05:59:33Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T06:04:33Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T06:09:34Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T06:14:34Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T06:19:34Z]   [ga_g13_123] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T06:25:36Z]   [ga_g13_123] S0 delay=36.8 cells=4127 area=11654.0 verdict=PASS rc=0
[2026-10-05T06:26:39Z]   [ga_g13_123] S1 verdict=FLAG rc=2 lin=10 diff=1 pb=0 rd=0
[2026-10-05T06:26:39Z]   death @S1: HYPOTHESIS: linear hull through the round linears (10 LIN rejections) — the (a,b) rotation pairs admit a high-bias linear trail at 6r.
[2026-10-05T06:26:39Z] gen 13: evaluating ga_g13_124 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T06:29:06Z]   [ga_g13_124] xcheck rc=0 XCHECK ga_g13_124: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T06:29:06Z]   [ga_g13_124] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T06:39:32Z]   [ga_g13_124] S0 delay=36.2 cells=3736 area=10759.0 verdict=PASS rc=0
[2026-10-05T06:41:09Z]   [ga_g13_124] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T06:41:09Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T06:41:09Z] gen 13: evaluating ga_g13_125 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T06:42:21Z]   [ga_g13_125] xcheck rc=0 XCHECK ga_g13_125: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T06:47:40Z]   [ga_g13_125] S0 delay=39.0 cells=3467 area=10025.0 verdict=PASS rc=0
[2026-10-05T06:48:39Z]   [ga_g13_125] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T06:48:39Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T06:48:39Z] gen 13: evaluating ga_g13_126 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_0F", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T06:49:55Z]   [ga_g13_126] xcheck rc=0 XCHECK ga_g13_126: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T06:49:55Z]   [ga_g13_126] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T06:54:55Z]   [ga_g13_126] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T06:59:55Z]   [ga_g13_126] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T07:04:55Z]   [ga_g13_126] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T07:09:55Z]   [ga_g13_126] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T07:14:55Z]   [ga_g13_126] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T07:19:55Z]   [ga_g13_126] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T07:35:17Z]   [ga_g13_126] S0 no result json: [Errno 2] No such file or directory: '/home/hatch/workspace/mix/exploration/ga/results/ga_g13_126/s0_result.json'; rc=1
[2026-10-05T07:35:17Z] gen 13: evaluating ga_g13_127 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_SP", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T07:36:54Z]   [ga_g13_127] xcheck rc=0 XCHECK ga_g13_127: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T07:36:54Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T07:41:55Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T07:46:55Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T07:51:55Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T07:56:55Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T08:01:55Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T08:06:55Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T08:11:55Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T08:16:55Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T08:21:55Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T08:30:14Z]   [ga_g13_127] S0 delay=33.2 cells=3080 area=8775.0 verdict=PASS rc=0
[2026-10-05T08:30:14Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T08:35:14Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T08:55:32Z] resumed at gen 13 evals=126 archiveS=4 archiveQ=1
[2026-10-05T08:55:32Z] gen 13: evaluating ga_g13_127 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_A5", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T08:57:05Z]   [ga_g13_127] xcheck rc=0 XCHECK ga_g13_127: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T08:57:05Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T09:02:05Z]   [ga_g13_127] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T09:10:05Z]   [ga_g13_127] S0 delay=37.6 cells=2756 area=8009.0 verdict=PASS rc=0
[2026-10-05T09:11:59Z]   [ga_g13_127] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T09:11:59Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T09:11:59Z] gen 13: evaluating ga_g13_128 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T09:14:36Z]   [ga_g13_128] xcheck rc=0 XCHECK ga_g13_128: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T09:14:36Z]   [ga_g13_128] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T09:24:05Z]   [ga_g13_128] S0 delay=36.7 cells=4113 area=11795.0 verdict=PASS rc=0
[2026-10-05T09:24:51Z]   [ga_g13_128] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T09:24:51Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T09:24:51Z] gen 13: evaluating ga_g13_129 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T09:25:37Z]   [ga_g13_129] xcheck rc=0 XCHECK ga_g13_129: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T09:25:37Z]   [ga_g13_129] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T09:30:37Z]   [ga_g13_129] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T09:35:37Z]   [ga_g13_129] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T09:40:38Z]   [ga_g13_129] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T09:45:38Z]   [ga_g13_129] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T09:50:38Z]   [ga_g13_129] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T09:55:38Z]   [ga_g13_129] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T10:00:38Z]   [ga_g13_129] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T10:08:05Z]   [ga_g13_129] S0 delay=30.6 cells=2594 area=7500.0 verdict=PASS rc=0
[2026-10-05T10:08:54Z]   [ga_g13_129] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T10:08:54Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T10:08:54Z] gen 13: evaluating ga_g13_130 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T10:11:18Z]   [ga_g13_130] xcheck rc=0 XCHECK ga_g13_130: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T10:19:16Z]   [ga_g13_130] S0 delay=43.8 cells=3588 area=10227.0 verdict=PASS rc=0
[2026-10-05T10:19:16Z]   [ga_g13_130] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T10:24:16Z]   [ga_g13_130] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T10:29:39Z]   [ga_g13_130] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T10:29:39Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T10:29:39Z] gen 13: evaluating ga_g13_131 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T10:30:07Z]   [ga_g13_131] xcheck rc=0 XCHECK ga_g13_131: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T10:32:44Z]   [ga_g13_131] S0 delay=36.6 cells=3752 area=10820.0 verdict=PASS rc=0
[2026-10-05T10:32:44Z]   [ga_g13_131] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T10:38:18Z]   [ga_g13_131] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T10:38:18Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T10:38:18Z] gen 13: evaluating ga_g13_132 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T10:39:06Z]   [ga_g13_132] xcheck rc=0 XCHECK ga_g13_132: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T10:39:06Z]   [ga_g13_132] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T10:48:44Z]   [ga_g13_132] S0 delay=45.6 cells=3985 area=11427.0 verdict=PASS rc=0
[2026-10-05T10:48:44Z]   [ga_g13_132] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T10:54:38Z]   [ga_g13_132] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T10:54:38Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T10:54:38Z] gen 13: evaluating ga_g13_133 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_FF", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T10:56:32Z]   [ga_g13_133] xcheck rc=0 XCHECK ga_g13_133: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T10:56:32Z]   [ga_g13_133] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T11:01:32Z]   [ga_g13_133] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T11:06:32Z]   [ga_g13_133] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T11:11:33Z]   [ga_g13_133] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T11:19:07Z]   [ga_g13_133] S0 delay=36.1 cells=4280 area=12152.0 verdict=PASS rc=0
[2026-10-05T11:19:40Z]   [ga_g13_133] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T11:19:40Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T11:19:40Z] --- gen 14 done: pop=20 archiveS=4 archiveQ=1 evals=133 deaths=47
[2026-10-05T11:19:40Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T11:19:40Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T11:19:40Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T11:19:40Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T11:19:40Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T11:19:40Z]     assoc [S1] rounds=6: x42
[2026-10-05T11:19:40Z]     assoc [S1] pbox:between64/interleave64: x25
[2026-10-05T11:19:40Z]     assoc [S1] chi_notrx1: x23
[2026-10-05T11:19:40Z]     assoc [S1] trunc-ish:chi_notr@r6: x22
[2026-10-05T11:19:40Z]     assoc [S1] s1_311x3: x20
[2026-10-05T11:19:40Z]     assoc [S1] s1_311x2: x20
[2026-10-05T11:19:40Z] gen 14: evaluating ga_g14_134 via guided(S1:guided_linear) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T11:20:06Z]   [ga_g14_134] xcheck rc=0 XCHECK ga_g14_134: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T11:20:50Z]   [ga_g14_134] S0 delay=37.0 cells=4149 area=11655.0 verdict=PASS rc=0
[2026-10-05T11:21:23Z]   [ga_g14_134] S1 verdict=FLAG rc=2 lin=2 diff=0 pb=0 rd=0
[2026-10-05T11:21:23Z]   death @S1: HYPOTHESIS: linear hull through the round linears (2 LIN rejections) — the (a,b) rotation pairs admit a high-bias linear trail at 6r.
[2026-10-05T11:21:23Z] gen 14: evaluating ga_g14_135 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T11:22:03Z]   [ga_g14_135] xcheck rc=0 XCHECK ga_g14_135: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T11:26:21Z]   [ga_g14_135] S0 delay=37.5 cells=3767 area=10761.0 verdict=PASS rc=0
[2026-10-05T11:27:09Z]   [ga_g14_135] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T11:27:09Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T11:27:09Z] gen 14: evaluating ga_g14_136 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T11:28:18Z]   [ga_g14_136] xcheck rc=0 XCHECK ga_g14_136: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T11:35:43Z]   [ga_g14_136] S0 delay=43.4 cells=3381 area=9818.0 verdict=PASS rc=0
[2026-10-05T11:36:14Z]   [ga_g14_136] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T11:36:14Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T11:36:14Z] gen 14: evaluating ga_g14_137 via guided(S1:guided_linear) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T11:36:32Z]   [ga_g14_137] xcheck rc=0 XCHECK ga_g14_137: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T11:37:15Z]   [ga_g14_137] S0 delay=37.9 cells=4214 area=12005.0 verdict=PASS rc=0
[2026-10-05T11:37:15Z]   [ga_g14_137] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T11:42:48Z]   [ga_g14_137] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T11:42:48Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T11:42:48Z] gen 14: evaluating ga_g14_138 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T11:55:41Z] resumed at gen 14 evals=137 archiveS=4 archiveQ=1
[2026-10-05T11:55:41Z] gen 14: evaluating ga_g14_138 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_A5", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T11:56:24Z]   [ga_g14_138] xcheck rc=0 XCHECK ga_g14_138: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T11:58:29Z]   [ga_g14_138] S0 delay=37.2 cells=3290 area=9544.0 verdict=PASS rc=0
[2026-10-05T11:58:29Z]   [ga_g14_138] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T12:03:29Z]   [ga_g14_138] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T12:08:29Z]   [ga_g14_138] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T12:14:22Z]   [ga_g14_138] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T12:14:22Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T12:14:22Z] gen 14: evaluating ga_g14_139 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T12:15:02Z]   [ga_g14_139] xcheck rc=0 XCHECK ga_g14_139: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T12:20:13Z]   [ga_g14_139] S0 delay=39.8 cells=4017 area=11649.0 verdict=PASS rc=0
[2026-10-05T12:21:22Z]   [ga_g14_139] S1 verdict=FLAG rc=2 lin=10 diff=4 pb=0 rd=0
[2026-10-05T12:21:22Z]   death @S1: HYPOTHESIS: linear hull through the round linears (10 LIN rejections) — the (a,b) rotation pairs admit a high-bias linear trail at 6r.
[2026-10-05T12:21:22Z] gen 14: evaluating ga_g14_140 via mutate {"const_fam": null, "const_where": "none", "mask": "r1_0F", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T12:22:03Z]   [ga_g14_140] xcheck rc=0 XCHECK ga_g14_140: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T12:24:10Z]   [ga_g14_140] S0 delay=37.5 cells=4104 area=11640.0 verdict=PASS rc=0
[2026-10-05T12:24:37Z]   [ga_g14_140] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T12:24:37Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T12:24:37Z] gen 14: evaluating ga_g14_141 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_FF", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T12:25:14Z]   [ga_g14_141] xcheck rc=0 XCHECK ga_g14_141: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T12:29:51Z]   [ga_g14_141] S0 delay=47.3 cells=3642 area=10490.0 verdict=PASS rc=0
[2026-10-05T12:30:25Z]   [ga_g14_141] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T12:30:25Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T12:30:25Z] gen 14: evaluating ga_g14_142 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T12:30:57Z]   [ga_g14_142] xcheck rc=0 XCHECK ga_g14_142: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T12:33:27Z]   [ga_g14_142] S0 delay=36.7 cells=3843 area=10974.0 verdict=PASS rc=0
[2026-10-05T12:34:12Z]   [ga_g14_142] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T12:34:12Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T12:34:12Z] gen 14: evaluating ga_g14_143 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T12:35:10Z]   [ga_g14_143] xcheck rc=0 XCHECK ga_g14_143: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T12:38:28Z]   [ga_g14_143] S0 delay=36.0 cells=3695 area=10452.0 verdict=PASS rc=0
[2026-10-05T12:38:28Z]   [ga_g14_143] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T12:49:43Z]   [ga_g14_143] S1 verdict=FLAG rc=2 lin=0 diff=0 pb=9 rd=0
[2026-10-05T12:49:43Z]   death @S1: HYPOTHESIS: marginal statistical blemish (PB rej=9, RD rej=0) — possible round self-similarity/slide structure; round constants break the symmetry.
[2026-10-05T12:49:43Z] gen 14: evaluating ga_g14_144 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T12:50:34Z]   [ga_g14_144] xcheck rc=0 XCHECK ga_g14_144: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T12:52:33Z]   [ga_g14_144] S0 delay=32.5 cells=3386 area=9606.0 verdict=PASS rc=0
[2026-10-05T12:53:14Z]   [ga_g14_144] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T12:53:14Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T12:53:14Z] gen 14: evaluating ga_g14_145 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T12:53:57Z]   [ga_g14_145] xcheck rc=0 XCHECK ga_g14_145: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T12:58:56Z]   [ga_g14_145] S0 delay=42.3 cells=3445 area=9914.0 verdict=PASS rc=0
[2026-10-05T12:59:35Z]   [ga_g14_145] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T12:59:35Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T12:59:35Z] --- gen 15 done: pop=20 archiveS=4 archiveQ=1 evals=145 deaths=59
[2026-10-05T12:59:35Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T12:59:35Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T12:59:35Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T12:59:35Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T12:59:35Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T12:59:35Z]     assoc [S1] rounds=6: x54
[2026-10-05T12:59:35Z]     assoc [S1] chi_notrx1: x30
[2026-10-05T12:59:35Z]     assoc [S1] trunc-ish:chi_notr@r6: x29
[2026-10-05T12:59:35Z]     assoc [S1] pbox:between64/interleave64: x29
[2026-10-05T12:59:35Z]     assoc [S1] s1_311x2: x28
[2026-10-05T12:59:35Z]     assoc [S1] s1_311x3: x24
[2026-10-05T12:59:35Z] gen 15: evaluating ga_g15_146 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T13:00:01Z]   [ga_g15_146] xcheck rc=0 XCHECK ga_g15_146: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T13:00:01Z]   [ga_g15_146] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T13:05:01Z]   [ga_g15_146] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T13:11:24Z]   [ga_g15_146] S0 delay=31.0 cells=2576 area=7444.0 verdict=PASS rc=0
[2026-10-05T13:12:05Z]   [ga_g15_146] S1 verdict=FLAG rc=2 lin=1 diff=10 pb=0 rd=0
[2026-10-05T13:12:05Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T13:12:05Z] gen 15: evaluating ga_g15_147 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_A5", "pbox_perm": "rot32_8", "pbox_where": "inF32", "rounds": 6, ...
[2026-10-05T13:12:39Z]   [ga_g15_147] xcheck rc=0 XCHECK ga_g15_147: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T13:17:42Z]   [ga_g15_147] S0 delay=41.4 cells=4451 area=12726.0 verdict=PASS rc=0
[2026-10-05T13:20:50Z]   [ga_g15_147] S1 verdict=CAL_PASS rc=0 lin=0 diff=0 pb=0 rd=0
[2026-10-05T13:43:41Z]   [ga_g15_147] S2 verdict=PASS max_repeats=0 max_z=5.6 rc=0 spikes=0
[2026-10-05T13:43:41Z]   [ga_g15_147] ARCHIVE-Q ENTER (provisional): (41.4, 4451, 12726) evicted=[]
[2026-10-05T13:49:16Z]   [ga_g15_147] S3 cfg1 rc=0
[2026-10-05T13:54:20Z]   [ga_g15_147] S3 cfg2 rc=0
[2026-10-05T13:57:37Z]   [ga_g15_147] S4 rc=0 passed=True
[2026-10-05T14:04:22Z]   [ga_g15_147] Q1 sac_z5=0 bic=0.04341
[2026-10-05T14:04:22Z]   [ga_g15_147] ARCHIVE-Q EVICT: bic=0.04341458745139213 > 0.02
[2026-10-05T14:04:22Z] gen 15: evaluating ga_g15_148 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "interleave64", "pbox_where": "between64", "roun...
[2026-10-05T14:05:45Z]   [ga_g15_148] xcheck rc=0 XCHECK ga_g15_148: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T14:05:45Z]   [ga_g15_148] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T14:13:32Z]   [ga_g15_148] S0 delay=37.8 cells=3549 area=10195.0 verdict=PASS rc=0
[2026-10-05T14:14:01Z]   [ga_g15_148] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T14:14:01Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T14:14:01Z] gen 15: evaluating ga_g15_149 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_A5", "pbox_perm": "nibrev64", "pbox_where": "between64", "rounds"...
[2026-10-05T14:14:36Z]   [ga_g15_149] xcheck rc=0 XCHECK ga_g15_149: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T14:14:39Z]   [ga_g15_149] S0 no result json: [Errno 2] No such file or directory: '/home/hatch/workspace/mix/exploration/ga/results/ga_g15_149/s0_result.json'; rc=1
[2026-10-05T14:14:39Z] gen 15: evaluating ga_g15_150 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T14:15:27Z]   [ga_g15_150] xcheck rc=0 XCHECK ga_g15_150: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T14:17:10Z]   [ga_g15_150] S0 delay=31.5 cells=2750 area=7895.0 verdict=PASS rc=0
[2026-10-05T14:17:40Z]   [ga_g15_150] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T14:17:40Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T14:17:40Z] gen 15: evaluating ga_g15_151 via crossover {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T14:18:17Z]   [ga_g15_151] xcheck rc=0 XCHECK ga_g15_151: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T14:20:25Z]   [ga_g15_151] S0 delay=33.7 cells=3187 area=9178.0 verdict=PASS rc=0
[2026-10-05T14:21:06Z]   [ga_g15_151] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T14:21:06Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T14:21:06Z] gen 15: evaluating ga_g15_152 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_0F", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T14:21:50Z]   [ga_g15_152] xcheck rc=0 XCHECK ga_g15_152: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T14:29:17Z]   [ga_g15_152] S0 delay=45.2 cells=3829 area=10993.0 verdict=PASS rc=0
[2026-10-05T14:30:08Z]   [ga_g15_152] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T14:30:08Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T14:30:08Z] gen 15: evaluating ga_g15_153 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_FF", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "ro...
[2026-10-05T14:30:48Z]   [ga_g15_153] xcheck rc=0 XCHECK ga_g15_153: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T14:32:27Z]   [ga_g15_153] S0 delay=44.4 cells=4653 area=13152.0 verdict=PASS rc=0
[2026-10-05T14:32:28Z]   [ga_g15_153] Stage-A discard: dominated by both archives
[2026-10-05T14:32:28Z] gen 15: evaluating ga_g15_154 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T14:33:36Z]   [ga_g15_154] xcheck rc=0 XCHECK ga_g15_154: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T14:37:07Z]   [ga_g15_154] S0 delay=35.7 cells=3524 area=10183.0 verdict=PASS rc=0
[2026-10-05T14:42:30Z]   [ga_g15_154] S1 verdict=FLAG rc=2 lin=0 diff=0 pb=9 rd=0
[2026-10-05T14:42:30Z]   death @S1: HYPOTHESIS: marginal statistical blemish (PB rej=9, RD rej=0) — possible round self-similarity/slide structure; round constants break the symmetry.
[2026-10-05T14:42:30Z] --- gen 16 done: pop=20 archiveS=4 archiveQ=1 evals=154 deaths=65
[2026-10-05T14:42:30Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T14:42:30Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T14:42:30Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T14:42:30Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T14:42:30Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T14:42:30Z]     assoc [S1] rounds=6: x59
[2026-10-05T14:42:30Z]     assoc [S1] chi_notrx1: x34
[2026-10-05T14:42:30Z]     assoc [S1] s1_311x2: x33
[2026-10-05T14:42:30Z]     assoc [S1] trunc-ish:chi_notr@r6: x32
[2026-10-05T14:42:30Z]     assoc [S1] pbox:between64/interleave64: x31
[2026-10-05T14:42:30Z]     assoc [S1] s1_311x3: x24
[2026-10-05T14:42:30Z] gen 16: evaluating ga_g16_155 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T14:43:19Z]   [ga_g16_155] xcheck rc=0 XCHECK ga_g16_155: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T14:47:23Z]   [ga_g16_155] S0 delay=37.0 cells=3851 area=11007.0 verdict=PASS rc=0
[2026-10-05T14:51:53Z]   [ga_g16_155] S1 verdict=FLAG rc=2 lin=0 diff=0 pb=29 rd=1
[2026-10-05T14:51:53Z]   death @S1: HYPOTHESIS: marginal statistical blemish (PB rej=29, RD rej=1) — possible round self-similarity/slide structure; round constants break the symmetry.
[2026-10-05T14:51:53Z] gen 16: evaluating ga_g16_156 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T14:52:47Z]   [ga_g16_156] xcheck rc=0 XCHECK ga_g16_156: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T14:56:58Z]   [ga_g16_156] S0 delay=33.3 cells=2940 area=8331.0 verdict=PASS rc=0
[2026-10-05T14:56:59Z]   [ga_g16_156] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T15:01:59Z]   [ga_g16_156] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T15:07:31Z]   [ga_g16_156] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T15:07:31Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T15:07:31Z] gen 16: evaluating ga_g16_157 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T15:08:49Z]   [ga_g16_157] xcheck rc=0 XCHECK ga_g16_157: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T15:11:42Z]   [ga_g16_157] S0 delay=32.2 cells=2618 area=7597.0 verdict=PASS rc=0
[2026-10-05T15:12:05Z]   [ga_g16_157] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T15:12:05Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T15:12:05Z] --- gen 17 done: pop=20 archiveS=4 archiveQ=1 evals=157 deaths=68
[2026-10-05T15:12:05Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T15:12:05Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T15:12:05Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T15:12:05Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T15:12:05Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T15:12:05Z]     assoc [S1] rounds=6: x61
[2026-10-05T15:12:05Z]     assoc [S1] chi_notrx1: x35
[2026-10-05T15:12:05Z]     assoc [S1] s1_311x2: x34
[2026-10-05T15:12:05Z]     assoc [S1] trunc-ish:chi_notr@r6: x32
[2026-10-05T15:12:05Z]     assoc [S1] pbox:between64/interleave64: x31
[2026-10-05T15:12:05Z]     assoc [S1] s1_311x3: x24
[2026-10-05T15:12:05Z] gen 17: evaluating ga_g17_158 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T15:12:49Z]   [ga_g17_158] xcheck rc=0 XCHECK ga_g17_158: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T15:14:37Z]   [ga_g17_158] S0 delay=32.3 cells=3355 area=9473.0 verdict=PASS rc=0
[2026-10-05T15:14:37Z]   [ga_g17_158] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T15:20:21Z]   [ga_g17_158] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T15:20:21Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T15:20:21Z] gen 17: evaluating ga_g17_159 via guided(S1:guided_const) {"const_fam": "iota", "const_where": "round_F", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "ro...
[2026-10-05T15:21:03Z]   [ga_g17_159] xcheck rc=0 XCHECK ga_g17_159: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T15:23:34Z]   [ga_g17_159] S0 delay=36.3 cells=3609 area=10376.0 verdict=PASS rc=0
[2026-10-05T15:24:05Z]   [ga_g17_159] S1 verdict=FLAG rc=2 lin=0 diff=8 pb=0 rd=0
[2026-10-05T15:24:05Z]   death @S1: HYPOTHESIS: differential weakness in F (8 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T15:24:05Z] gen 17: evaluating ga_g17_160 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T15:24:39Z]   [ga_g17_160] xcheck rc=0 XCHECK ga_g17_160: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T15:58:34Z] resumed at gen 17 evals=159 archiveS=4 archiveQ=1
[2026-10-05T15:58:34Z] gen 17: evaluating ga_g17_160 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T16:00:08Z]   [ga_g17_160] xcheck rc=0 XCHECK ga_g17_160: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T16:01:57Z] resumed at gen 17 evals=159 archiveS=4 archiveQ=1
[2026-10-05T16:01:57Z] gen 17: evaluating ga_g17_160 via crossover {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T16:02:28Z]   [ga_g17_160] xcheck rc=0 XCHECK ga_g17_160: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T16:05:04Z]   [ga_g17_160] S0 delay=35.1 cells=3722 area=10731.0 verdict=PASS rc=0
[2026-10-05T16:05:04Z]   [ga_g17_160] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T16:10:18Z]   [ga_g17_160] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T16:10:18Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T16:10:18Z] gen 17: evaluating ga_g17_161 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r3_A5", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T16:10:37Z]   [ga_g17_161] xcheck rc=0 XCHECK ga_g17_161: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T16:11:38Z]   [ga_g17_161] S0 delay=37.1 cells=2900 area=8383.0 verdict=PASS rc=0
[2026-10-05T16:11:53Z]   [ga_g17_161] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T16:11:53Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T16:11:53Z] gen 17: evaluating ga_g17_162 via mutate {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds":...
[2026-10-05T16:12:16Z]   [ga_g17_162] xcheck rc=0 XCHECK ga_g17_162: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T16:13:10Z]   [ga_g17_162] S0 delay=31.2 cells=2994 area=8594.0 verdict=PASS rc=0
[2026-10-05T16:13:24Z]   [ga_g17_162] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T16:13:24Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T16:13:24Z] gen 17: evaluating ga_g17_163 via mutate {"const_fam": null, "const_where": "none", "mask": "r3_H2", "pbox_perm": "rot64_16", "pbox_where": "between64", "rounds"...
[2026-10-05T16:13:38Z]   [ga_g17_163] xcheck rc=0 XCHECK ga_g17_163: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T16:14:49Z]   [ga_g17_163] S0 delay=32.4 cells=2622 area=7541.0 verdict=PASS rc=0
[2026-10-05T16:15:17Z]   [ga_g17_163] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T16:15:17Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T16:15:17Z] gen 17: evaluating ga_g17_164 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r1_FF", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T16:15:49Z]   [ga_g17_164] xcheck rc=0 XCHECK ga_g17_164: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T16:20:05Z]   [ga_g17_164] S0 delay=46.9 cells=3680 area=10592.0 verdict=PASS rc=0
[2026-10-05T16:20:29Z]   [ga_g17_164] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T16:20:29Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T16:20:29Z] gen 17: evaluating ga_g17_165 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T16:20:54Z]   [ga_g17_165] xcheck rc=0 XCHECK ga_g17_165: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T16:24:41Z]   [ga_g17_165] S0 delay=45.6 cells=3564 area=10380.0 verdict=PASS rc=0
[2026-10-05T16:25:00Z]   [ga_g17_165] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T16:25:00Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T16:25:00Z] gen 17: evaluating ga_g17_166 via guided(S1:guided_linear) {"const_fam": null, "const_where": "none", "mask": "none", "pbox_perm": "transpose8x4", "pbox_where": "replacerot", "rou...
[2026-10-05T16:25:15Z]   [ga_g17_166] xcheck rc=0 XCHECK ga_g17_166: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T16:26:10Z]   [ga_g17_166] S0 delay=36.8 cells=4341 area=12242.0 verdict=PASS rc=0
[2026-10-05T16:26:10Z]   [ga_g17_166] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T16:31:10Z]   [ga_g17_166] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T16:36:10Z]   [ga_g17_166] polite_wait: >=2 foreign heavy pipelines, sleeping 300s
[2026-10-05T16:41:28Z]   [ga_g17_166] S1 verdict=FLAG rc=2 lin=5 diff=0 pb=0 rd=0
[2026-10-05T16:41:28Z]   death @S1: HYPOTHESIS: linear hull through the round linears (5 LIN rejections) — the (a,b) rotation pairs admit a high-bias linear trail at 6r.
[2026-10-05T16:41:28Z] gen 17: evaluating ga_g17_167 via guided(S1:guided_nonlinear) {"const_fam": null, "const_where": "none", "mask": "r2_A5", "pbox_perm": "interleave64", "pbox_where": "between64", "rou...
[2026-10-05T16:41:53Z]   [ga_g17_167] xcheck rc=0 XCHECK ga_g17_167: PASS 10000/10000 C==Python
/home/hatch/workspace/mix/exploration/round20/models/r20.py:93: RuntimeWarning: overflow encountered in scalar multiply
  return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32

[2026-10-05T16:43:26Z]   [ga_g17_167] S0 delay=46.1 cells=3820 area=10952.0 verdict=PASS rc=0
[2026-10-05T16:43:44Z]   [ga_g17_167] S1 verdict=FLAG rc=2 lin=0 diff=10 pb=0 rd=0
[2026-10-05T16:43:44Z]   death @S1: HYPOTHESIS: differential weakness in F (10 DIFF rejections) — the nonlinear layer/chi offsets leak a differential trail.
[2026-10-05T16:43:44Z] --- gen 18 done: pop=20 archiveS=4 archiveQ=1 evals=167 deaths=78
[2026-10-05T16:43:44Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [r20_feist6_alt_notr_chioff13all_nw]
[2026-10-05T16:43:44Z]     archS 37.0u 4357c 12511a bic=0.14149255646039563 [ga_g00_004]
[2026-10-05T16:43:44Z]     archS 37.4u 4149c 11820a bic=0.14216636907212074 [r19_feist6_alt_notr_chioff13_nw]
[2026-10-05T16:43:44Z]     archS 37.5u 3863c 11199a bic=0.14091860175566215 [r20_feist6_alt_notr_chioff31_nw]
[2026-10-05T16:43:44Z]     archQ 42.9u 4133c 11670a bic=0.008037 [r8_feist6_s1_1sbox_nw]
[2026-10-05T16:43:44Z]     assoc [S1] rounds=6: x70
[2026-10-05T16:43:44Z]     assoc [S1] chi_notrx1: x41
[2026-10-05T16:43:44Z]     assoc [S1] s1_311x2: x40
[2026-10-05T16:43:44Z]     assoc [S1] trunc-ish:chi_notr@r6: x37
[2026-10-05T16:43:44Z]     assoc [S1] pbox:between64/interleave64: x34
[2026-10-05T16:43:44Z]     assoc [S1] pbox:between64/rot64_16: x28
[2026-10-05T16:43:44Z] 48h wall budget exhausted — exiting
