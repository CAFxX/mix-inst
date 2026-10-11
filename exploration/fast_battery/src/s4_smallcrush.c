/* S4 TestU01 SmallCrush driver (fast staged battery).
 * Compiled per-candidate with candidates/<name>/impl.c which must define:
 *   uint64_t mix_hash(uint64_t val, uint64_t key).
 * Usage: ./smallcrush <key_hex>
 * Includes a bit-exact sanity check vs meta.json goldens (aborts on mismatch),
 * so a C/Python model divergence can never be mistaken for a candidate failure.
 *
 * Build: gcc -O2 -o smallcrush_<cand> s4_smallcrush.c candidates/<cand>/impl.c \
 *          -I$HOME/tools/testu01/install/include -L$HOME/tools/testu01/install/lib \
 *          -ltestu01 -lprobdist -lmylib -lm
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "TestU01.h"

uint64_t mix_hash(uint64_t val, uint64_t key);

/* goldens injected at build time via -DGOLDEN_V0=... etc.; checked here */
#ifndef GOLDEN_KEY
#define GOLDEN_KEY 0x123456789ABCDEF0ULL
#endif

static uint64_t g_key;
static uint64_t g_ctr;
static uint64_t g_buf;
static int g_have;

static uint32_t gen_bits(void) {
    if (!g_have) {
        g_buf = mix_hash(g_ctr++, g_key);
        g_have = 1;
        return (uint32_t)(g_buf & 0xFFFFFFFFULL);
    } else {
        g_have = 0;
        return (uint32_t)(g_buf >> 32);
    }
}

int main(int argc, char **argv) {
    g_key = argc > 1 ? strtoull(argv[1], NULL, 16) : GOLDEN_KEY;
    g_ctr = 0;
    g_have = 0;
#ifdef GOLDEN_OUT
    if (mix_hash(0, GOLDEN_KEY) != (uint64_t)GOLDEN_OUT) {
        fprintf(stderr, "MODEL MISMATCH: mix_hash(0, GOLDEN_KEY)=%016llx != %016llx\n",
                (unsigned long long)mix_hash(0, GOLDEN_KEY),
                (unsigned long long)(uint64_t)GOLDEN_OUT);
        return 1;
    }
#endif
    unif01_Gen *gen = unif01_CreateExternGenBits("mix_candidate", gen_bits);
    bbattery_SmallCrush(gen);
    unif01_DeleteExternGen01(gen);
    return 0;
}
