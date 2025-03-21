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
    int32_t tmp_arg0 = guards_guards1(p_a, p_b);
    l_res += tmp_arg0;
    size_t tmp_arg1 = sizeof(p_a);
    if (!(tmp_arg1 > sizeof(p_b))) {
        abort();
    }
    int32_t tmp_arg2 = guards_guards2(p_a);
    l_res += tmp_arg2;
    l_res += guards_guards3();
    if (!(p_a < l_res)) {
        abort();
    }
    int32_t tmp_res3 = 0;
    const guards_ErrorCode tmp_err4 = guards_guards4(p_a, l_res, &tmp_res3);
    if (guards_to(tmp_err4)) {
        abort();
    }
    if (!(l_res > tmp_res3)) {
        abort();
    }
    l_res += tmp_res3;
    if (!(p_a < p_b)) {
        abort();
    }
    int32_t tmp_res5 = 0;
    const guards_ErrorCode tmp_err6 = guards_guards4(p_a, p_b, &tmp_res5);
    if (guards_to(tmp_err6)) {
        abort();
    }
    if (!(p_b > tmp_res5)) {
        abort();
    }
    size_t tmp_arg7 = sizeof(tmp_res5);
    if (!(tmp_arg7 > sizeof(p_b))) {
        abort();
    }
    int32_t tmp_arg8 = guards_guards2(tmp_res5);
    int32_t tmp_arg9 = guards_guards3();
    if (!(tmp_arg8 < tmp_arg9)) {
        abort();
    }
    int32_t tmp_res10 = 0;
    const guards_ErrorCode tmp_err11 = guards_guards4(tmp_arg8, tmp_arg9, &tmp_res10);
    if (guards_to(tmp_err11)) {
        abort();
    }
    if (!(tmp_arg9 > tmp_res10)) {
        abort();
    }
    l_res += tmp_res10;
    return l_res;
}
