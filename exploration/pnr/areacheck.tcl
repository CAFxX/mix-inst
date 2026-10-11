read_liberty $env(PDK_LIB)
read_lef $env(PDK_TLEF)
read_lef $env(PDK_LEF_SC_HD)
read_verilog $env(SYNTH)
link_design $env(TOP)
set block [ord::get_db_block]
set area 0.0
foreach inst [$block getInsts] {
  set m [$inst getMaster]
  set area [expr {$area + [$m getArea]}]
}
set dbu [$block getDbUnitsPerMicron]
puts "CELLS_AREA_UM2 [format %.1f [expr {$area/($dbu*$dbu)}]]"
