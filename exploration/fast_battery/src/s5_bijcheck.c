/* Bijectivity sanity: n random inputs under a key, outputs collision-free.
 * Usage: bij_check <key_hex> <n> <seed_hex>
 * impl.c provides uint64_t mix_hash(uint64_t val, uint64_t key).
 * Exit 2 on any collision, 0 if clean. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

uint64_t mix_hash(uint64_t val, uint64_t key);

static uint64_t xorshift64(uint64_t *s) {
    uint64_t x = *s;
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    return *s = x;
}

static int cmpu64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "usage: %s <key_hex> <n> <seed>\n", argv[0]); return 1; }
    uint64_t key = strtoull(argv[1], NULL, 16);
    size_t n = strtoull(argv[2], NULL, 10);
    uint64_t st = strtoull(argv[3], NULL, 16);
    uint64_t *outs = malloc(n * sizeof(uint64_t));
    if (!outs) { fprintf(stderr, "OOM\n"); return 1; }
    for (size_t i = 0; i < n; i++)
        outs[i] = mix_hash(xorshift64(&st), key);
    qsort(outs, n, sizeof(uint64_t), cmpu64);
    size_t coll = 0;
    for (size_t i = 1; i < n; i++)
        if (outs[i] == outs[i-1]) coll++;
    printf("key=0x%016llx n=%zu collisions=%zu\n",
           (unsigned long long)key, n, coll);
    free(outs);
    return coll ? 2 : 0;
}
