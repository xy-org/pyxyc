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
    int32_t tmp_2 = 0;
    if (ifs3_compute(tmp_0_arg, tmp_1_arg, ifs3_helper3()) > 0) {
        tmp_2 = 1;
    } else {
        tmp_2 = 0;
    }
    return tmp_2;
}

int32_t ifs3_test2(void) {
    int32_t tmp_0_arg = ifs3_helper1();
    int32_t tmp_1_arg = ifs3_helper2();
    int32_t tmp_2 = 0;
    if (ifs3_compute(tmp_0_arg, tmp_1_arg, ifs3_helper3()) > 0) {
        tmp_2 = 0;
    } else {
        int32_t tmp_3_arg = ifs3_helper3();
        int32_t tmp_4_arg = ifs3_helper2();
        if (ifs3_compute(tmp_3_arg, tmp_4_arg, ifs3_helper1()) < 0) {
            tmp_2 = 1;
        } else {
            tmp_2 = 2;
        }
    }
    return tmp_2;
}

int32_t ifs3_test3(void) {
    int32_t tmp_0_arg = ifs3_helper1();
    int32_t tmp_1_arg = ifs3_helper2();
    int32_t tmp_2 = 0;
    if (ifs3_compute(tmp_0_arg, tmp_1_arg, ifs3_helper3()) > 0) {
        tmp_2 = 0;
    } else {
        int32_t tmp_3_arg = ifs3_helper3();
        int32_t tmp_4_arg = ifs3_helper2();
        if (ifs3_compute(tmp_3_arg, tmp_4_arg, ifs3_helper1()) == 0) {
            int32_t tmp_5_arg = ifs3_helper3();
            int32_t tmp_6_arg = ifs3_helper2();
            tmp_2 = ifs3_compute(tmp_5_arg, tmp_6_arg, ifs3_helper1());
        } else {
            tmp_2 = 2;
        }
    }
    return tmp_2;
}

void ifs3_test4(void) {
    int32_t tmp_0_arg = ifs3_helper1();
    int32_t tmp_1_arg = ifs3_helper2();
    int32_t tmp_4 = 0;
    if (ifs3_compute(tmp_0_arg, tmp_1_arg, ifs3_helper3()) > 0) {
        int32_t tmp_2_arg = ifs3_helper3();
        int32_t tmp_3_arg = ifs3_helper2();
        tmp_4 = ifs3_compute(tmp_2_arg, tmp_3_arg, ifs3_helper1());
    }
}
