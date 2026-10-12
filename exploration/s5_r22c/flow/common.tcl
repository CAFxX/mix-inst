# S5 flow common setup — sourced by every stage Tcl.
# Env vars expected: PDK_LIB, PDK_TLEF, PDK_LEF_SC_HD, PDK_LEF_PR (from sky130-env.sh)
read_liberty $::env(PDK_LIB)
read_lef $::env(PDK_TLEF)
read_lef $::env(PDK_LEF_SC_HD)
read_lef $::env(PDK_LEF_PR)
