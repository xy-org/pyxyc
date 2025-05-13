#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

uint32_t bitBasics_test(void) {
    uint32_t l_a = (uint32_t)0xABCD;
    uint32_t l_b = (uint32_t)0x1234;
    const uint32_t l_c = l_a | l_b;
    const uint32_t l_d = l_a & l_b;
    const uint32_t l_e = l_a ^ l_b;
    const uint32_t l_f = l_d << 4 ^ l_e >> 5;
    const uint32_t l_g = ~(l_c | (l_f & l_e));
    const uint32_t l_h = (uint32_t)((int32_t)l_g >> 10);
    return (uint32_t)l_h;
}
