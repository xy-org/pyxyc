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
    int32_t tmp_0_arg = guards_guards1(p_a, p_b);
    l_res += tmp_0_arg;
    size_t tmp_1_arg = sizeof(p_a);
    if (!(tmp_1_arg > sizeof(p_b))) {
        abort();
    }
    int32_t tmp_2_arg = guards_guards2(p_a);
    l_res += tmp_2_arg;
    l_res += guards_guards3();
    if (!(p_a < l_res)) {
        abort();
    }
    int32_t tmp_3_res = 0;
    const guards_ErrorCode tmp_4_err = guards_guards4(p_a, l_res, &tmp_3_res);
    if (guards_to(tmp_4_err)) {
        abort();
    }
    if (!(l_res > tmp_3_res)) {
        abort();
    }
    l_res += tmp_3_res;
    if (!(p_a < p_b)) {
        abort();
    }
    int32_t tmp_5_res = 0;
    const guards_ErrorCode tmp_6_err = guards_guards4(p_a, p_b, &tmp_5_res);
    if (guards_to(tmp_6_err)) {
        abort();
    }
    if (!(p_b > tmp_5_res)) {
        abort();
    }
    size_t tmp_7_arg = sizeof(tmp_5_res);
    if (!(tmp_7_arg > sizeof(p_b))) {
        abort();
    }
    int32_t tmp_8_arg = guards_guards2(tmp_5_res);
    int32_t tmp_9_arg = guards_guards3();
    if (!(tmp_8_arg < tmp_9_arg)) {
        abort();
    }
    int32_t tmp_10_res = 0;
    const guards_ErrorCode tmp_11_err = guards_guards4(tmp_8_arg, tmp_9_arg, &tmp_10_res);
    if (guards_to(tmp_11_err)) {
        abort();
    }
    if (!(tmp_9_arg > tmp_10_res)) {
        abort();
    }
    l_res += tmp_10_res;
    return l_res;
}
