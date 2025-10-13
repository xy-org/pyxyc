#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t checkedDivision_f1(int32_t p_x) {
    return p_x * 2;
}

int32_t checkedDivision_f2(int32_t p_x) {
    return p_x - 10;
}

int32_t checkedDivision_test(int32_t p_x, int32_t p_y) {
    int32_t tmp_0_arg = checkedDivision_f1(p_x);
    int32_t tmp_1_arg = checkedDivision_f2(p_y);
    if (!(tmp_1_arg != 0)) {
        abort();
    }
    return tmp_0_arg / tmp_1_arg;
}
