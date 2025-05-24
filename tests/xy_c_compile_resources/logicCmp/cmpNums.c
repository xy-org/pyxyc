#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void cmpNums_test__Ushort__Ushort(uint16_t p_a, uint16_t p_b) {
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

void cmpNums_test__Int__Int(int32_t p_a, int32_t p_b) {
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

void cmpNums_test__Float__Float(float p_a, float p_b) {
    const bool l_c = p_a == p_b;
    const bool l_d = p_a != p_b;
    const bool l_g = p_a > p_b;
    const bool l_h = p_a >= p_b;
    const bool l_i = p_a < p_b;
    const bool l_j = p_a <= p_b;
    const int32_t l_k = p_a > p_b ? 1 : p_a == p_b ? 0 : -1;
}

void cmpNums_test__Double__Double(double p_a, double p_b) {
    const bool l_c = p_a == p_b;
    const bool l_d = p_a != p_b;
    const bool l_g = p_a > p_b;
    const bool l_h = p_a >= p_b;
    const bool l_i = p_a < p_b;
    const bool l_j = p_a <= p_b;
    const int32_t l_k = p_a > p_b ? 1 : p_a == p_b ? 0 : -1;
}
