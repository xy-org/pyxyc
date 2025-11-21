#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t namedArguments_fun__1(int32_t p_a, int32_t p_b, int32_t p_c) {
    return p_a + p_b + p_c;
}

int32_t namedArguments_fun__2(int32_t p_a, int32_t p_b, int32_t p_c, int32_t p_d) {
    return p_a * p_b * p_c * p_d;
}

void namedArguments_testNamedArgs(void) {
    const int32_t l_a = namedArguments_fun__1(0, 1, 2);
    const int32_t l_b = namedArguments_fun__1(l_a, 10, 2);
    const int32_t l_c = namedArguments_fun__1(l_b, 1, 10);
    const int32_t l_d = namedArguments_fun__1(l_b, 10, l_c);
    const int32_t l_e = namedArguments_fun__1(l_a, l_b, l_c);
    const int32_t l_f = namedArguments_fun__1(l_a, l_b, l_c);
    const int32_t l_g = namedArguments_fun__1(l_a, l_b, l_c);
    const int32_t l_h = namedArguments_fun__1(l_f, l_b, l_c);
    const int32_t l_i = namedArguments_fun__2(1, 2, 3, 4);
    const float l_j = 5.0f * 1.0f;
}
