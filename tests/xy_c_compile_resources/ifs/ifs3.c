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
    int32_t tmp_arg0 = ifs3_helper1();
    int32_t tmp_arg1 = ifs3_helper2();
    int32_t tmp3 = 0;
    if (ifs3_compute(tmp_arg0, tmp_arg1, ifs3_helper3()) > 0) {
        tmp3 = 1;
    } else {
        tmp3 = 0;
    }
    return tmp3;
}

int32_t ifs3_test2(void) {
    int32_t tmp_arg0 = ifs3_helper1();
    int32_t tmp_arg1 = ifs3_helper2();
    int32_t tmp3 = 0;
    if (ifs3_compute(tmp_arg0, tmp_arg1, ifs3_helper3()) > 0) {
        tmp3 = 0;
    } else {
        int32_t tmp_arg4 = ifs3_helper3();
        int32_t tmp_arg5 = ifs3_helper2();
        if (ifs3_compute(tmp_arg4, tmp_arg5, ifs3_helper1()) < 0) {
            tmp3 = 1;
        } else {
            tmp3 = 2;
        }
    }
    return tmp3;
}

int32_t ifs3_test3(void) {
    int32_t tmp_arg0 = ifs3_helper1();
    int32_t tmp_arg1 = ifs3_helper2();
    int32_t tmp3 = 0;
    if (ifs3_compute(tmp_arg0, tmp_arg1, ifs3_helper3()) > 0) {
        tmp3 = 0;
    } else {
        int32_t tmp_arg4 = ifs3_helper3();
        int32_t tmp_arg5 = ifs3_helper2();
        if (ifs3_compute(tmp_arg4, tmp_arg5, ifs3_helper1()) == 0) {
            int32_t tmp_arg7 = ifs3_helper3();
            int32_t tmp_arg8 = ifs3_helper2();
            tmp3 = ifs3_compute(tmp_arg7, tmp_arg8, ifs3_helper1());
        } else {
            tmp3 = 2;
        }
    }
    return tmp3;
}

void ifs3_test4(void) {
    int32_t tmp_arg0 = ifs3_helper1();
    int32_t tmp_arg1 = ifs3_helper2();
    int32_t tmp5 = 0;
    if (ifs3_compute(tmp_arg0, tmp_arg1, ifs3_helper3()) > 0) {
        int32_t tmp_arg3 = ifs3_helper3();
        int32_t tmp_arg4 = ifs3_helper2();
        tmp5 = ifs3_compute(tmp_arg3, tmp_arg4, ifs3_helper1());
    }
    tmp5;
}
