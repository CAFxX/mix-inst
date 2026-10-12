"""Python model wrapper for h_xorspn3 (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round4/models")
from r4_hybrid import mix_h_xorspn3_s as mix  # noqa: F401
from r4_hybrid import mix_h_xorspn3_np as mix_np  # noqa: F401
