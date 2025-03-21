#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void cmpBits_test(uint32_t p_a, uint32_t p_b) {
    const uint32_t l_c = ~(p_a ^ p_b);
    const uint32_t l_d = p_a ^ p_b;
    const uint32_t l_e = ~p_a;
    const uint32_t l_f = ~~p_a;
    const uint32_t l_g = p_a ^ p_b;
    const uint32_t l_h = p_a ^ p_b | ~(uint32_t)0;
    const uint32_t l_i = (p_a ^ p_b) & 0;
    const uint32_t l_j = ~(p_a ^ p_b);
    const uint32_t l_k = p_a & p_b;
    const uint32_t l_l = p_a | p_b;
    const uint32_t l_m = p_a ^ p_b;
    const uint32_t l_n = p_a ^ p_b;
}
