"""Model for t6_aor5b, delegates to t6_models_b7."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions")
from t6_models_b7 import CANDIDATES_B7
import numpy as np
_fn, _desc = CANDIDATES_B7["t6_aor5b"]
def mix_model(val, key):
    return int(_fn(np.uint64(val), np.uint64(key)))
