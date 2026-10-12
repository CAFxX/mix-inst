"""Python model wrapper for r3_xorlin_qm (fast_battery candidate interface).
r3_xorlin_qm is bit-identical to spn4_xorlin_1137 (QM-minimized PRESENT S-box).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/models")
from spn4_xorlin_1137 import mix_spn4_xorlin_1137_scalar as mix  # noqa: F401
from spn4_xorlin_1137 import mix_spn4_xorlin_1137_np as mix_np  # noqa: F401
