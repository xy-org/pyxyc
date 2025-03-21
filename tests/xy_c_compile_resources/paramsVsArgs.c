#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t paramsVsArgs_func1(int32_t p_a, int32_t p_b, int32_t p_c) {
    return p_a * p_b * p_c;
}

int32_t paramsVsArgs_func2(int32_t p_c) {
    return p_c;
}

void* paramsVsArgs_func3(void* p_ptr) {
    return p_ptr;
}

void paramsVsArgs_test(void) {
    int32_t l_a = paramsVsArgs_func1(0, 1, 0 + 1);
    const int32_t l_b = paramsVsArgs_func1(l_a, l_a, l_a + l_a);
    const int32_t l_c = paramsVsArgs_func2(l_a + l_b);
    int32_t* const l_d = (int32_t*)paramsVsArgs_func3(&l_a);
    float* l_e = (float*)paramsVsArgs_func3(&l_a);
    int32_t* const l_f = (int32_t*)paramsVsArgs_func3(&l_e);
}
