#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct refValue_Data refValue_Data;

struct refValue_Data {
    void* m_mem;
};

float refValue_get(refValue_Data p_d, int32_t p_i) {
    return (float)(p_i * 2);
}

int32_t refValue_func1(refValue_Data p_d, int32_t p_i) {
    return p_i;
}

void refValue_test(void) {
    int32_t l_a = 10;
    int32_t* const l_b = &l_a;
    int32_t* const l_c = &l_a;
    const refValue_Data l_d = {0};
    int32_t tmp_0_arg = refValue_func1(l_d, 10);
    const float l_e = refValue_get(l_d, tmp_0_arg);
    int32_t tmp_1_arg = refValue_func1(l_d, 10);
    const int32_t l_f = tmp_1_arg;
}
