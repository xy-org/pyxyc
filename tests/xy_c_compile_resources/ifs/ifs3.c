#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t ifs3_compute(int32_t p_a, int32_t p_b, int32_t p_c) {
    return p_a + p_b * p_c;
}

int32_t ifs3_helper1(void) {
    return 1;
}

int32_t ifs3_helper2(void) {
    return 2;
}

int32_t ifs3_helper3(void) {
    return 3;
}

int32_t ifs3_test1(void) {
    int32_t tmp_0_arg = ifs3_helper1();
    int32_t tmp_1_arg = ifs3_helper2();
    int32_t tmp_3 = 0;
    if (ifs3_compute(tmp_0_arg, tmp_1_arg, ifs3_helper3()) > 0) {
        tmp_3 = 1;
    } else {
        tmp_3 = 0;
    }
    return tmp_3;
}

int32_t ifs3_test2(void) {
    int32_t tmp_0_arg = ifs3_helper1();
    int32_t tmp_1_arg = ifs3_helper2();
    int32_t tmp_3 = 0;
    if (ifs3_compute(tmp_0_arg, tmp_1_arg, ifs3_helper3()) > 0) {
        tmp_3 = 0;
    } else {
        int32_t tmp_4_arg = ifs3_helper3();
        int32_t tmp_5_arg = ifs3_helper2();
        if (ifs3_compute(tmp_4_arg, tmp_5_arg, ifs3_helper1()) < 0) {
            tmp_3 = 1;
        } else {
            tmp_3 = 2;
        }
    }
    return tmp_3;
}

int32_t ifs3_test3(void) {
    int32_t tmp_0_arg = ifs3_helper1();
    int32_t tmp_1_arg = ifs3_helper2();
    int32_t tmp_3 = 0;
    if (ifs3_compute(tmp_0_arg, tmp_1_arg, ifs3_helper3()) > 0) {
        tmp_3 = 0;
    } else {
        int32_t tmp_4_arg = ifs3_helper3();
        int32_t tmp_5_arg = ifs3_helper2();
        if (ifs3_compute(tmp_4_arg, tmp_5_arg, ifs3_helper1()) == 0) {
            int32_t tmp_7_arg = ifs3_helper3();
            int32_t tmp_8_arg = ifs3_helper2();
            tmp_3 = ifs3_compute(tmp_7_arg, tmp_8_arg, ifs3_helper1());
        } else {
            tmp_3 = 2;
        }
    }
    return tmp_3;
}

void ifs3_test4(void) {
    int32_t tmp_0_arg = ifs3_helper1();
    int32_t tmp_1_arg = ifs3_helper2();
    int32_t tmp_5 = 0;
    if (ifs3_compute(tmp_0_arg, tmp_1_arg, ifs3_helper3()) > 0) {
        int32_t tmp_3_arg = ifs3_helper3();
        int32_t tmp_4_arg = ifs3_helper2();
        tmp_5 = ifs3_compute(tmp_3_arg, tmp_4_arg, ifs3_helper1());
    }
    tmp_5;
}
