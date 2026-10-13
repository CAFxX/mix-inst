/* M9 item 1: count 64-bit collisions over N=2^24 sequential vals, fixed key. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
uint64_t mix_hash(uint64_t val, uint64_t key);
static int cmp64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t*)a, y = *(const uint64_t*)b;
    return (x > y) - (x < y);
}
int main(int argc, char **argv) {
    uint64_t key = strtoull(argv[1], 0, 16);
    const size_t N = 1u << 24;
    uint64_t *h = malloc(N * sizeof *h);
    if (!h) { fprintf(stderr, "oom\n"); return 2; }
    for (size_t i = 0; i < N; i++) h[i] = mix_hash((uint64_t)i, key);
    qsort(h, N, sizeof *h, cmp64);
    long long coll = 0;
    for (size_t i = 1; i < N; i++) if (h[i] == h[i-1]) coll++;
    printf("key=%016llx N=2^24 collisions=%lld (birthday expectation ~2^-17)\n",
           (unsigned long long)key, coll);
    free(h);
    return 0;
}
