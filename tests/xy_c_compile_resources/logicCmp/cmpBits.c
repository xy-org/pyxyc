#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void cmpBits_test(uint32_t p_a, uint32_t p_b) {
    const bool l_c = p_a == p_b;
    const bool l_d = p_a != p_b;
    const uint32_t l_e = ~p_a;
    const uint32_t l_f = ~~p_a;
    const uint32_t l_k = p_a & p_b;
    const uint32_t l_l = p_a | p_b;
    const uint32_t l_m = p_a ^ p_b;
}
