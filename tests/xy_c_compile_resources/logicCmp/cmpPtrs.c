#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void cmpPtrs_test(void* p_a, void* p_b) {
    const bool l_c = p_a == p_b;
    const bool l_d = p_a != p_b;
    const bool l_e = !p_a;
    const bool l_f = !!p_a;
    const bool l_g = p_a > p_b;
    const bool l_h = p_a >= p_b;
    const bool l_i = p_a < p_b;
    const bool l_j = p_a <= p_b;
    const int32_t l_k = p_a > p_b ? 1 : p_a == p_b ? 0 : -1;
}
