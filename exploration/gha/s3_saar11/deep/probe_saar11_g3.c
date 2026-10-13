#include <stdio.h>
#include <stdint.h>
uint64_t mix_hash(uint64_t val, uint64_t key);
int main(void){ printf("0x%llx\n", (unsigned long long)mix_hash(0, 0x123456789abcdef0ULL)); return 0; }
