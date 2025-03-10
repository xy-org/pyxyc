#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

uint32_t bitBasics_test(void) {
    uint32_t a = (uint32_t){0xABCD};
    uint32_t b = (uint32_t){0x1234};
    const uint32_t c = a | b;
    const uint32_t d = a & b;
    const uint32_t e = a ^ b;
    return e;
}
