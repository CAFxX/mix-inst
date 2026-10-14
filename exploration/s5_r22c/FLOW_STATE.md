# S5 FLOW_STATE — resume log (append-only; driver appends per completed stage)
# 2026-10-04: first driver run FAILED (openroad Verilog parser rejects `reg` decls;
#   driver trusted rc instead of checkpoints). Reworked: yosys stage-0 -> sky130
#   structural netlist + 20k-vector equivalence gate, checkpoint-file-based driver.
r22c:FAILED:stage s1_link finished without checkpoint [/home/hatch/workspace/mix/exploration/s5_r22c/r22c/linked.ok](r22c/linked.ok):2026-10-04T04:53:14Z
r22c:s1_link:2026-10-04T04:53:43Z:ok
r22c:FAILED:stage s2_floor finished without checkpoint [/home/hatch/workspace/mix/exploration/s5_r22c/r22c/floorplan.def](r22c/floorplan.def):2026-10-04T04:53:46Z
r22c:FAILED:stage s2_floor finished without checkpoint [/home/hatch/workspace/mix/exploration/s5_r22c/r22c/floorplan.def](r22c/floorplan.def):2026-10-04T04:55:24Z
r22c:FAILED:stage s2_floor finished without checkpoint [/home/hatch/workspace/mix/exploration/s5_r22c/r22c/floorplan.def](r22c/floorplan.def):2026-10-04T04:57:15Z
r22c:FAILED:stage s2_floor finished without checkpoint [/home/hatch/workspace/mix/exploration/s5_r22c/r22c/floorplan.def](r22c/floorplan.def):2026-10-04T04:59:26Z
r22c:FAILED:stage s2_floor finished without checkpoint [/home/hatch/workspace/mix/exploration/s5_r22c/r22c/floorplan.def](r22c/floorplan.def):2026-10-04T05:01:32Z
r22c:FAILED:stage s2_floor finished without checkpoint [/home/hatch/workspace/mix/exploration/s5_r22c/r22c/floorplan.def](r22c/floorplan.def):2026-10-04T05:03:34Z
r22c:s2_floor:2026-10-04T05:05:44Z:ok
r22c:FAILED:stage s3_place finished without checkpoint [/home/hatch/workspace/mix/exploration/s5_r22c/r22c/placed.def](r22c/placed.def):2026-10-04T05:05:47Z
r22c:FAILED:stage s3_place finished without checkpoint [/home/hatch/workspace/mix/exploration/s5_r22c/r22c/placed.def](r22c/placed.def):2026-10-04T05:08:34Z
r22c:s3_place:2026-10-04T05:10:43Z:ok
r22c:FAILED:stage s4_route finished without checkpoint /home/hatch/workspace/mix/exploration/s5_r22c/r22c/routed.def:2026-10-04T05:10:49Z
r22c:FAILED:stage s4_route finished without checkpoint /home/hatch/workspace/mix/exploration/s5_r22c/r22c/routed.def:2026-10-04T05:12:32Z
r22c:s3_place:2026-10-04T05:15:19Z:ok
mult:s0_ysynth:2026-10-04T05:58:53Z:ok
mult:s1_link:2026-10-04T05:58:53Z:ok
mult:s2_floorplan:2026-10-04T05:58:53Z:ok
mult:s3_place:2026-10-04T05:58:53Z:ok
mult:equiv:2026-10-04T05:58:53Z:ok
r22c:FAILED:stage s4_route finished without checkpoint /home/hatch/workspace/mix/exploration/s5_r22c/r22c/routed.def:2026-10-04T06:33:11Z
r22c:RESTART:40pct-utilization:2026-10-04T06:33:23Z:route-stuck-60pct-4147viol
r22c:s4b_global:2026-10-04T07:17:13Z:ok
mult:s4b_global:2026-10-04T07:17:13Z:ok
S5_GATE:PASS:r22c_4.41ns_vs_mult_12.80ns_ratio_0.344:2026-10-04T07:17:13Z
