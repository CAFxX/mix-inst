import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import KEYS
print(len(KEYS))
print([hex(int(k)) for k in KEYS])
