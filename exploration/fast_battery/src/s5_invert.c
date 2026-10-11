/* Invertibility spot-check: #include the candidate's impl.c so the test
 * exercises the exact shipped code (static F_spn / rk / sbox_layer32).
 * Usage: gcc -O2 -o /tmp/inv_<name> s5_invert.c -DIMPL_PATH="candidates/<name>/impl.c"
 *        /tmp/inv_<name> <seed> <nvec>
 * Inverts mix_hash via the Feistel inverse and checks round-trip.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Compile with -DIMPLSTR='"path/to/impl.c"' (quotes inside the -D value). */
#include IMPLSTR

/* splitmix64 for test vectors */
static uint64_t sm_state;
static uint64_t sm_next(void) {
    uint64_t z = (sm_state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static uint64_t mix_inv(uint64_t out, uint64_t key) {
    uint32_t L = (uint32_t)out;          /* L8 */
    uint32_t R = (uint32_t)(out >> 32);  /* R8 */
    for (int i = 8; i >= 1; i--) {
        uint32_t Li = L, Ri = R;
        /* forward was: nL=R_{i-1}, nR=L_{i-1}^F(R_{i-1}) ; so R_{i-1}=L_i, L_{i-1}=R_i^F(L_i) */
        uint32_t Rp = Li;
        uint32_t Lp = Ri ^ F_spn(Li, rk(key, i));
        L = Lp; R = Rp;
    }
    uint32_t vh = L ^ (uint32_t)(key >> 32);
    uint32_t vl = R ^ (uint32_t)key;
    return ((uint64_t)vh << 32) | vl;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: inv <seed> <nvec>\n"); return 2; }
    sm_state = strtoull(argv[1], 0, 0);
    long n = atol(argv[2]);
    long bad = 0;
    /* edge cases first: 0, all-ones, powers of two */
    uint64_t edges[] = {0ULL, ~0ULL, 1ULL, 0x8000000000000000ULL,
                        0x0000000100000000ULL, 0xFFFFFFFF00000000ULL};
    for (unsigned e = 0; e < sizeof(edges)/sizeof(edges[0]); e++) {
        for (int k = 0; k < 4; k++) {
            uint64_t key = k ? sm_next() : 0x123456789abcdef0ULL;
            uint64_t v = edges[e];
            if (mix_inv(mix_hash(v, key), key) != v) { bad++; printf("EDGE FAIL v=%lx key=%lx\n", (unsigned long)v, (unsigned long)key); }
        }
    }
    for (long i = 0; i < n; i++) {
        uint64_t v = sm_next(), key = sm_next();
        if (mix_inv(mix_hash(v, key), key) != v) {
            bad++;
            if (bad < 5) printf("FAIL v=%lx key=%lx\n", (unsigned long)v, (unsigned long)key);
        }
    }
    /* distinctness spot check: n sequential vals, one key -> count collisions via sort-free hash set is
       overkill; rely on invertibility (a non-injective map cannot have a 2-sided inverse on samples) */
    printf("invert: %ld vectors, %ld failures\n", n, bad);
    return bad ? 1 : 0;
}
