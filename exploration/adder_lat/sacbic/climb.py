"""
Hill-climber for SAC/BIC with incremental scoring.

State maintains:
- funcs[j] = list of (a,b) pairs
- M[i][j] = partner mask
- counts[i][mask] = occurrences
- sac, bic violation counts
"""

import random
import time
from sacbic import compute_masks


class SACBICState:
    def __init__(self, funcs):
        self.funcs = [list(p) for p in funcs]  # deep copy
        self.M = compute_masks(self.funcs)
        self.counts = [dict() for _ in range(64)]
        for i in range(64):
            d = self.counts[i]
            for j in range(64):
                m = self.M[i][j]
                d[m] = d.get(m, 0) + 1
        self.sac = 0
        self.bic = 0
        for i in range(64):
            d = self.counts[i]
            if 0 in d:
                self.sac += d[0]
            for c in d.values():
                if c > 1:
                    self.bic += (c - 1)

    def _mask_delta(self, j, old_pair, new_pair):
        """Compute the 4 (input, old_mask, new_mask) changes for replacing
        old_pair with new_pair in funcs[j]. Returns list of (i, old_m, new_m)."""
        a, b = old_pair
        a2, b2 = new_pair
        # Masks before change
        changes = []
        # We'll compute new masks by XORing out old contributions and XORing in new
        # M[x][j] new = M[x][j] old ^ (contrib removed) ^ (contrib added)
        affected = {}
        for (x, y, sign) in [(a, b, -1), (b, a, -1), (a2, b2, +1), (b2, a2, +1)]:
            # sign -1: remove y from x's partners; +1: add y
            if x not in affected:
                affected[x] = self.M[x][j]
            if sign == -1:
                affected[x] ^= (1 << y)
            else:
                affected[x] ^= (1 << y)
        for x, new_m in affected.items():
            old_m = self.M[x][j]
            if old_m != new_m:
                changes.append((x, old_m, new_m))
        return changes

    def try_move(self, j, p, new_pair):
        """Try replacing funcs[j][p] with new_pair. Returns (dsac, dbic) delta.
        Does NOT commit. Caller must call commit_move to apply."""
        old_pair = self.funcs[j][p]
        if old_pair == new_pair or (new_pair[1], new_pair[0]) == old_pair:
            return (0, 0), []
        # Ensure canonical (a<b)
        a2, b2 = new_pair
        if a2 > b2:
            a2, b2 = b2, a2
        if a2 == b2:
            return (0, 0), []
        new_pair = (a2, b2)
        # Check not duplicate in funcs[j]
        for q, pr in enumerate(self.funcs[j]):
            if q != p and pr == new_pair:
                return (0, 0), []

        changes = self._mask_delta(j, old_pair, new_pair)
        dsac = 0
        dbic = 0
        for (x, old_m, new_m) in changes:
            # SAC delta
            if old_m == 0:
                dsac -= 1
            if new_m == 0:
                dsac += 1
            # BIC delta for input x
            d = self.counts[x]
            c_old = d.get(old_m, 0)
            c_new = d.get(new_m, 0)
            # old decreases by 1
            if c_old >= 2:
                dbic -= 1
            # new increases by 1
            if c_new >= 1:
                dbic += 1
        return (dsac, dbic), (changes, j, p, old_pair, new_pair)

    def commit_move(self, move_info):
        """Apply a move previously evaluated by try_move."""
        changes, j, p, old_pair, new_pair = move_info
        # Update funcs
        self.funcs[j][p] = new_pair
        # Update M and counts
        for (x, old_m, new_m) in changes:
            # Update sac/bic (we'll recompute deltas, or trust caller)
            # Update M
            self.M[x][j] = new_m
            # Update counts
            d = self.counts[x]
            # decrement old
            d[old_m] -= 1
            if d[old_m] == 0:
                del d[old_m]
            # increment new
            d[new_m] = d.get(new_m, 0) + 1
        # Recompute sac/bic from scratch for safety (or use deltas)
        # For now, use deltas passed in? Let's just recompute the affected parts.
        # Actually simplest: caller tracks sac/bic via deltas.
        pass

    def recompute_scores(self):
        """Recompute sac/bic from M (for verification)."""
        sac = 0
        bic = 0
        for i in range(64):
            seen = set()
            for j in range(64):
                m = self.M[i][j]
                if m == 0:
                    sac += 1
                if m in seen:
                    bic += 1
                else:
                    seen.add(m)
        self.sac = sac
        self.bic = bic


def hill_climb(t=40, max_iter=200000, seed=123):
    from sacbic import structured_init
    rng = random.Random(seed)
    funcs = structured_init(t, rng)
    st = SACBICState(funcs)
    print(f"Init: sac={st.sac}, bic={st.bic}", flush=True)

    best = (st.sac, st.bic)
    it = 0
    no_improve = 0
    t0 = time.time()
    while it < max_iter and (st.sac > 0 or st.bic > 0):
        it += 1
        # Random move: pick j, p, new random pair
        j = rng.randrange(64)
        p = rng.randrange(len(st.funcs[j]))
        a2 = rng.randrange(64)
        b2 = rng.randrange(64)
        if a2 == b2:
            continue
        if a2 > b2:
            a2, b2 = b2, a2
        new_pair = (a2, b2)

        (dsac, dbic), move_info = st.try_move(j, p, new_pair)
        new_sac = st.sac + dsac
        new_bic = st.bic + dbic
        # Accept if strictly better (lexicographic: sac first, then bic)
        if (new_sac, new_bic) < (st.sac, st.bic):
            # Commit
            changes, jj, pp, old_pair, np2 = move_info
            st.funcs[jj][pp] = np2
            for (x, old_m, new_m) in changes:
                st.M[x][jj] = new_m
                d = st.counts[x]
                d[old_m] -= 1
                if d[old_m] == 0:
                    del d[old_m]
                d[new_m] = d.get(new_m, 0) + 1
            st.sac = new_sac
            st.bic = new_bic
            if (new_sac, new_bic) < best:
                best = (new_sac, new_bic)
                no_improve = 0
                if it % 100 == 0:
                    print(f"it={it}: sac={new_sac}, bic={new_bic} *", flush=True)
            else:
                no_improve += 1
        else:
            no_improve += 1

        if it % 5000 == 0:
            # Verify
            st.recompute_scores()
            print(f"it={it}: sac={st.sac}, bic={st.bic} (verified), time={time.time()-t0:.1f}s", flush=True)
            if st.sac == 0 and st.bic == 0:
                break

    st.recompute_scores()
    print(f"Done: it={it}, sac={st.sac}, bic={st.bic}, time={time.time()-t0:.1f}s", flush=True)
    return st


if __name__ == "__main__":
    import sys
    t = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    max_iter = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
    st = hill_climb(t=t, max_iter=max_iter)
    # Save
    import pickle
    with open(f"best_t{t}.pkl", "wb") as f:
        pickle.dump(st.funcs, f)
    print(f"Saved to best_t{t}.pkl")
