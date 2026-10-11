/* S3 PractRand generator (fast staged battery).
 * Compiled per-candidate with candidates/<name>/impl.c which must define:
 *   uint64_t mix_hash(uint64_t val, uint64_t key).
 * Usage: ./gen <key_hex> <nbytes> [stride]
 *   writes raw little-endian bytes of mix(i, key) [sequential] or
 *   mix(i*stride, key) [strided] to stdout. No intermediate files:
 *   pipe directly into RNG_test stdin64.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

uint64_t mix_hash(uint64_t val, uint64_t key);

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: gen <key_hex> <nbytes> [stride]\n"); return 1; }
    uint64_t key = strtoull(argv[1], NULL, 16);
    unsigned long long nbytes = strtoull(argv[2], NULL, 10);
    uint64_t stride = argc > 3 ? strtoull(argv[3], NULL, 0) : 1;
    unsigned long long nvals = nbytes / 8;
    /* buffered output: 1 MiB chunks */
    static uint64_t buf[1 << 17];
    unsigned long long done = 0;
    while (done < nvals) {
        unsigned long long m = nvals - done;
        if (m > (1 << 17)) m = (1 << 17);
        for (unsigned long long i = 0; i < m; i++)
            buf[i] = mix_hash((done + i) * stride, key);
        if (fwrite(buf, 8, (size_t)m, stdout) != (size_t)m) { perror("fwrite"); return 1; }
        done += m;
    }
    fflush(stdout);
    return 0;
}
