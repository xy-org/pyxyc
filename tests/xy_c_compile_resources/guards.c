#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct guards_ErrorCode guards_ErrorCode;

struct guards_ErrorCode {
    int32_t m_code;
};

int32_t guards_guards1(int32_t p_a, int32_t p_b) {
    return 0;
}

int32_t guards_guards2(int32_t p_a) {
    return 0;
}

int32_t guards_guards3(void) {
    return 0;
}

bool guards_to(guards_ErrorCode p_ec) {
    return p_ec.m_code != 0;
}

guards_ErrorCode guards_guards4(int32_t p_a, int32_t p_b, int32_t* __c) {
    *__c = 0;
    return (guards_ErrorCode){0};
}

int32_t guards_test(int32_t p_a, int32_t p_b) {
    int32_t l_res = 0;
    if (!(p_a > p_b)) {
        abort();
    }
    l_res += guards_guards1(p_a, p_b);
    size_t tmp_0_arg = sizeof(p_a);
    if (!(tmp_0_arg > sizeof(p_b))) {
        abort();
    }
    l_res += guards_guards2(p_a);
    l_res += guards_guards3();
    if (!(p_a < l_res)) {
        abort();
    }
    int32_t tmp_1_res = 0;
    const guards_ErrorCode tmp_2_err = guards_guards4(p_a, l_res, &tmp_1_res);
    if (guards_to(tmp_2_err)) {
        abort();
    }
    if (!(l_res > tmp_1_res)) {
        abort();
    }
    l_res += tmp_1_res;
    if (!(p_a < p_b)) {
        abort();
    }
    int32_t tmp_3_res = 0;
    const guards_ErrorCode tmp_4_err = guards_guards4(p_a, p_b, &tmp_3_res);
    if (guards_to(tmp_4_err)) {
        abort();
    }
    if (!(p_b > tmp_3_res)) {
        abort();
    }
    size_t tmp_5_arg = sizeof(tmp_3_res);
    if (!(tmp_5_arg > sizeof(p_b))) {
        abort();
    }
    int32_t tmp_6_arg = guards_guards2(tmp_3_res);
    int32_t tmp_7_arg = guards_guards3();
    if (!(tmp_6_arg < tmp_7_arg)) {
        abort();
    }
    int32_t tmp_8_res = 0;
    const guards_ErrorCode tmp_9_err = guards_guards4(tmp_6_arg, tmp_7_arg, &tmp_8_res);
    if (guards_to(tmp_9_err)) {
        abort();
    }
    if (!(tmp_7_arg > tmp_8_res)) {
        abort();
    }
    l_res += tmp_8_res;
    return l_res;
}
