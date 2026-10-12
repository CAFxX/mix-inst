# S5 SDC — IDENTICAL for r22c and mult (identical-condition A/B).
# Combinational single-cycle requirement modeled with a virtual clock:
#   achieved_delay = 20.0 - 0.5 - 0.5 - worst_slack = 19.0 - worst_slack
# Both designs get the same constraint; the comparison (r22c vs mult) is
# what the <=multiplier hard requirement is checked against.
create_clock -name virt_clk -period 20.0
set_input_delay -clock virt_clk 0.5 [all_inputs]
set_output_delay -clock virt_clk 0.5 [all_outputs]
