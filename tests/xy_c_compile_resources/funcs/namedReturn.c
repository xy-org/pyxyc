#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t namedReturn_test1(void) {
    int32_t l_ret = 0;
    l_ret = 10;
    return l_ret;
}

int32_t namedReturn_test2(int32_t p_a, float* __ret) {
    *__ret = (float)p_a * 2.0f;
    if (p_a > 20) {
        *__ret = 1.0f;
        return 0;
    } else if (p_a > 10) {
        return 0;
    }
    return 1;
}
