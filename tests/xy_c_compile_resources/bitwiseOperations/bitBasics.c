#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

uint32_t bitBasics_test(void) {
    uint32_t l_a = 0xABCDu;
    uint32_t l_b = 0x1234u;
    const uint32_t l_c = l_a | l_b;
    const uint32_t l_d = l_a & l_b;
    const uint32_t l_e = l_a ^ l_b;
    const uint32_t l_f = l_d << 4 ^ l_e >> 5;
    const uint32_t l_g = ~(l_c | (l_f & l_e));
    const uint32_t l_h = (int32_t)l_g >> 10;
    return (uint32_t)l_h;
}
