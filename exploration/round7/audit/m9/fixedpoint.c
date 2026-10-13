/* fixed points / 2-cycles under weak key and normal keys */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
uint64_t mix_hash(uint64_t val, uint64_t key);
int main(int argc, char **argv) {
    uint64_t key = strtoull(argv[1], 0, 16);
    long long n = atoll(argv[2]);
    long long fp = 0, c2 = 0;
    uint64_t s = 0x123456789abcdefULL;
    for (long long i = 0; i < n; i++) {
        s = s * 6364136223846793005ULL + 1442695040888963407ULL;
        uint64_t h1 = mix_hash(s, key);
        if (h1 == s) fp++;
        else if (mix_hash(h1, key) == s) c2++;
    }
    printf("key=%016llx n=%lld fixed_points=%lld two_cycles=%lld\n",
           (unsigned long long)key, n, fp, c2);
    return 0;
}
