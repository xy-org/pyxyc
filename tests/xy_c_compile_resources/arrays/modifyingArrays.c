#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void modifyingArrays_test(float* p_arr) {
    const float l_brr[3] = {1.0f, 2.0f, 3.0f};
    for (int32_t i = 0; i < 3; ++i) {
        float tmp_0_arg = p_arr[i];
        p_arr[i] = tmp_0_arg + l_brr[i];
    }
}
