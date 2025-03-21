#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void cmpBools_test(bool p_a, bool p_b) {
    const bool l_c = p_a == p_b;
    const bool l_d = p_a != p_b;
    const bool l_e = !p_a;
    const bool l_f = !!p_a;
    const bool l_g = p_a > p_b;
    const bool l_h = p_a >= p_b;
    const bool l_i = p_a < p_b;
    const bool l_j = p_a <= p_b;
    const bool l_k = p_a && p_b;
    const bool l_l = p_a || p_b;
    const bool l_m = p_a - p_b;
}
