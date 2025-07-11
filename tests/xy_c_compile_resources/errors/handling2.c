#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct handling2_Error handling2_Error;

struct handling2_Error {
    int32_t m_code;
};

handling2_Error handling2_errorProne(int32_t p_num, int32_t* _res0) {
    if (p_num > 10000) {
        return (handling2_Error){p_num};
    }
    *_res0 = p_num * 2;
    return (handling2_Error){0};
}

int32_t handling2_test1(int32_t p_x) {
    handling2_Error tmp_0_catch = (handling2_Error){0};
    int32_t tmp_1_res = 0;
    tmp_0_catch = handling2_errorProne(p_x + 1, &tmp_1_res);
    const handling2_Error l_err = tmp_0_catch;
    return l_err.m_code;
}

int32_t handling2_mix(int32_t p_a, int32_t p_b) {
    return p_a * p_b + p_a / p_b;
}

int32_t handling2_test2(int32_t p_x) {
    handling2_Error tmp_0_catch = (handling2_Error){0};
    int32_t tmp_1_res = 0;
    tmp_0_catch = handling2_errorProne(p_x + 1, &tmp_1_res);
    if (tmp_0_catch.m_code != 0) {
        goto L_0_CONTINUE_catch;
    }
    int32_t tmp_2_res = 0;
    tmp_0_catch = handling2_errorProne(p_x * 10, &tmp_2_res);
    if (tmp_0_catch.m_code != 0) {
        goto L_0_CONTINUE_catch;
    }
    handling2_mix(tmp_1_res, tmp_2_res);
L_0_CONTINUE_catch:
    ;
    
    ;
    const handling2_Error l_err = tmp_0_catch;
    return l_err.m_code;
}
