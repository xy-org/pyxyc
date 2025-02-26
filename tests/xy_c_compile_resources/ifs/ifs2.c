#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t ifs2_compute(int32_t a, int32_t b, int32_t c) {
    return a + b * c;
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

int32_t ifs2_test1(bool cond) {
    int32_t tmp2 = 0;
    if (cond) {
        int32_t tmp_arg0 = ifs2_helper1();
        int32_t tmp_arg1 = ifs2_helper2();
        tmp2 = ifs2_compute(tmp_arg0, tmp_arg1, ifs2_helper3());
    }
    return tmp2;
}

int32_t ifs2_test2(bool cond) {
    int32_t tmp2 = 0;
    if (cond) {
        int32_t tmp_arg0 = ifs2_helper1();
        int32_t tmp_arg1 = ifs2_helper2();
        tmp2 = ifs2_compute(tmp_arg0, tmp_arg1, ifs2_helper3());
    } else {
        int32_t tmp_arg3 = ifs2_helper3();
        int32_t tmp_arg4 = ifs2_helper2();
        tmp2 = ifs2_compute(tmp_arg3, tmp_arg4, ifs2_helper1());
    }
    return tmp2;
}

int32_t ifs2_test3(int32_t num) {
    int32_t tmp3 = 0;
    if (num > 0) {
        int32_t tmp_arg1 = ifs2_helper1();
        int32_t tmp_arg2 = ifs2_helper2();
        tmp3 = ifs2_compute(tmp_arg1, tmp_arg2, ifs2_helper3());
    } else if (num < 0) {
        int32_t tmp_arg5 = ifs2_helper1();
        int32_t tmp_arg6 = ifs2_helper1();
        tmp3 = ifs2_compute(tmp_arg5, tmp_arg6, ifs2_helper1());
    } else {
        int32_t tmp_arg7 = ifs2_helper3();
        int32_t tmp_arg8 = ifs2_helper2();
        tmp3 = ifs2_compute(tmp_arg7, tmp_arg8, ifs2_helper1());
    }
    return tmp3;
}
