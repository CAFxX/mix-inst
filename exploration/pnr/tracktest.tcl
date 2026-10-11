read_lef $env(PDK_TLEF)
read_lef $env(PDK_LEF_SC_HD)
# only X tracks for li1 (omit y)
make_tracks li1 -x_offset 0.23 -x_pitch 0.46
set tech [ord::get_db_tech]
foreach layer [$tech getLayers] {
  set name [$layer getName]
  if {$name == "li1" || $name == "met1"} {
    puts "LAYER $name"
  }
}
# count track grids via dbTech
puts "done"
