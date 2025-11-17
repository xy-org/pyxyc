#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void modifyingArrays_test(float* p_arr) {
    const float l_brr[3] = {1.0f, 2.0f, 3.0f};
    for (int32_t i = 0; i < 3; ++i) {
        p_arr[i] += l_brr[i];
    }
}
