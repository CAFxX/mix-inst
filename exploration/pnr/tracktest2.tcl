read_liberty $env(PDK_LIB)
read_lef $env(PDK_TLEF)
read_lef $env(PDK_LEF_SC_HD)
read_verilog synth_add64.v
link_design add64
initialize_floorplan -die_area "0 0 200 200" -core_area "15 15 185 185" -site unithd
make_tracks li1 -x_offset 0.23 -x_pitch 0.46
make_tracks met1 -y_offset 0.17 -y_pitch 0.34
set block [ord::get_db_block]
foreach tg [$block getTrackGrids] {
  set layer [[$tg getTechLayer] getName]
  puts "TRACKGRID layer=$layer nxpat=[$tg getNumGridPatternsX] nypat=[$tg getNumGridPatternsY]"
  for {set i 0} {$i < [$tg getNumGridPatternsX]} {incr i} {
    set gp [$tg getGridPatternX $i]
    puts "   XPATTERN start=[$gp getStart] n=[$gp getCount] step=[$gp getStep]"
  }
  for {set i 0} {$i < [$tg getNumGridPatternsY]} {incr i} {
    set gp [$tg getGridPatternY $i]
    puts "   YPATTERN start=[$gp getStart] n=[$gp getCount] step=[$gp getStep]"
  }
}
