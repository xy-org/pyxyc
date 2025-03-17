#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void cmpBits_test(uint32_t a, uint32_t b) {
    const uint32_t c = ~(a ^ b);
    const uint32_t d = a ^ b;
    const uint32_t e = ~a;
    const uint32_t f = ~~a;
    const uint32_t g = a ^ b;
    const uint32_t h = a ^ b | ~(uint32_t)0;
    const uint32_t i = (a ^ b) & 0;
    const uint32_t j = ~(a ^ b);
    const uint32_t k = a & b;
    const uint32_t l = a | b;
    const uint32_t m = a ^ b;
    const uint32_t n = a ^ b;
}
