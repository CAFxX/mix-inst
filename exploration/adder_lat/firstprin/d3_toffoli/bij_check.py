"""Brute-force bijectivity checks for small n. Run under nice -n 10."""
import itertools

def S_orig(x, n, a, b):
    # out[i] = in[i] ^ (in[(i+a)%n] & in[(i+b)%n]) -- the task's specified stage
    return tuple((x[i] ^ (x[(i+a)%n] & x[(i+b)%n])) for i in range(n))

def S_chi(x, n, a, b):
    # Keccak-chi-like: out[i] = in[i] ^ ((~in[(i+a)%n]) & in[(i+b)%n])
    return tuple((x[i] ^ ((1^x[(i+a)%n]) & x[(i+b)%n])) for i in range(n))

def S_bipartite(x, n, a, b):
    # Repair A: even targets, odd controls frozen (a,b odd)
    out = list(x)
    for i in range(0, n, 2):
        out[i] = x[i] ^ (x[(i+a)%n] & x[(i+b)%n])
    return tuple(out)

def is_bij(S, n, a, b):
    seen = set()
    for bits in itertools.product((0,1), repeat=n):
        y = S(bits, n, a, b)
        if y in seen:
            return False, bits
        seen.add(y)
    return True, None

for n in (3,4,5):
    ok, wit = is_bij(S_orig, n, 1, 2)
    print(f"ORIG n={n} (1,2): bijective={ok}" + (f" witness collision at {wit}" if not ok else ""))
print()
for n in (3,4,5,6,7):
    ok, wit = is_bij(S_chi, n, 1, 2)
    print(f"CHI  n={n} (1,2): bijective={ok}" + (f" witness collision at {wit}" if not ok else ""))
print()
for n in (4,6,8):
    ok, wit = is_bij(S_bipartite, n, 1, 3)
    print(f"BIPARTITE n={n} (1,3): bijective={ok}" + (f" witness collision at {wit}" if not ok else ""))
# analytic 64-bit collision for ORIG
z64 = tuple([0]*64); o64 = tuple([1]*64)
print()
print("ORIG n=64 analytic: S(0^64)==S(1^64):", S_orig(z64,64,1,3) == S_orig(o64,64,1,3),
      " both =", S_orig(z64,64,1,3)[:4], "...")
