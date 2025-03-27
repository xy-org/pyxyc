#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t ifs2_compute(int32_t p_a, int32_t p_b, int32_t p_c) {
    return p_a + p_b * p_c;
}

int32_t ifs2_helper1(void) {
    return 1;
}

int32_t ifs2_helper2(void) {
    return 2;
}

int32_t ifs2_helper3(void) {
    return 3;
}

int32_t ifs2_test1(bool p_cond) {
    int32_t tmp_2 = 0;
    if (p_cond) {
        int32_t tmp_0_arg = ifs2_helper1();
        int32_t tmp_1_arg = ifs2_helper2();
        tmp_2 = ifs2_compute(tmp_0_arg, tmp_1_arg, ifs2_helper3());
    }
    return tmp_2;
}

int32_t ifs2_test2(bool p_cond) {
    int32_t tmp_2 = 0;
    if (p_cond) {
        int32_t tmp_0_arg = ifs2_helper1();
        int32_t tmp_1_arg = ifs2_helper2();
        tmp_2 = ifs2_compute(tmp_0_arg, tmp_1_arg, ifs2_helper3());
    } else {
        int32_t tmp_3_arg = ifs2_helper3();
        int32_t tmp_4_arg = ifs2_helper2();
        tmp_2 = ifs2_compute(tmp_3_arg, tmp_4_arg, ifs2_helper1());
    }
    return tmp_2;
}

int32_t ifs2_test3(int32_t p_num) {
    int32_t tmp_3 = 0;
    if (p_num > 0) {
        int32_t tmp_1_arg = ifs2_helper1();
        int32_t tmp_2_arg = ifs2_helper2();
        tmp_3 = ifs2_compute(tmp_1_arg, tmp_2_arg, ifs2_helper3());
    } else if (p_num < 0) {
        int32_t tmp_5_arg = ifs2_helper1();
        int32_t tmp_6_arg = ifs2_helper1();
        tmp_3 = ifs2_compute(tmp_5_arg, tmp_6_arg, ifs2_helper1());
    } else {
        int32_t tmp_7_arg = ifs2_helper3();
        int32_t tmp_8_arg = ifs2_helper2();
        tmp_3 = ifs2_compute(tmp_7_arg, tmp_8_arg, ifs2_helper1());
    }
    return tmp_3;
}
