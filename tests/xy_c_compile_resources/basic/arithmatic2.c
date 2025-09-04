#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void arithmatic2_test(int32_t p_int, float p_float, double p_double, bool p_bool) {
    const int32_t l_a = p_int - p_int;
    const int32_t l_b = p_int - p_bool;
    const double l_c = p_double + p_double;
    const double l_d = p_double + p_bool;
    const float l_e = p_float - p_float;
    const float l_f = p_float + p_bool;
    const float l_g = p_bool / p_float;
    const double l_h = p_bool * p_double;
    const double l_i = p_int * p_bool;
}
