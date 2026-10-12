#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
uint64_t mix_hash(uint64_t val, uint64_t key);
int main(int argc, char**argv) {
  uint64_t v = strtoull(argv[1], NULL, 16), k = strtoull(argv[2], NULL, 16);
  printf("%016llx\n", (unsigned long long)mix_hash(v, k));
  return 0;
}
