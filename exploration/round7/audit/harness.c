// Harness: reads vectors.hex (val key expected), checks mix_hash from impl.c.
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>

uint64_t mix_hash(uint64_t val, uint64_t key);

int main(void) {
    FILE *f = fopen("vectors.hex", "r");
    if (!f) { printf("FATAL: cannot open vectors.hex\n"); return 2; }
    char line[128];
    long n = 0, nfail = 0;
    int first_fail = -1;
    while (fgets(line, sizeof line, f)) {
        uint64_t v, k, e;
        if (sscanf(line, "%" SCNx64 " %" SCNx64 " %" SCNx64, &v, &k, &e) != 3)
            continue;
        n++;
        if (n > 300) break;  // a few hundred vectors
        uint64_t got = mix_hash(v, k);
        if (got != e) {
            nfail++;
            if (first_fail < 0) first_fail = (int)n;
            if (nfail <= 5)
                printf("C MISMATCH #%ld: val=%016" PRIx64 " key=%016" PRIx64
                       " c=%016" PRIx64 " model=%016" PRIx64 "\n",
                       n, v, k, got, e);
        }
    }
    fclose(f);
    printf("C RESULT total=%ld fail=%ld first_fail=%d\n", n, nfail, first_fail);
    return nfail != 0;
}
