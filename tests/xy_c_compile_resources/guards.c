#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct guards_ErrorCode guards_ErrorCode;

struct guards_ErrorCode {
    int32_t m_code;
};

int32_t guards_guards1(int32_t a, int32_t b) {
    return 0;
}

int32_t guards_guards2(int32_t a) {
    return 0;
}

int32_t guards_guards3(void) {
    return 0;
}

bool guards_to(guards_ErrorCode ec) {
    return ec.m_code != 0;
}

guards_ErrorCode guards_guards4(int32_t a, int32_t b, int32_t* __c) {
    *__c = 0;
    return (guards_ErrorCode){0};
}

int32_t guards_test(int32_t a, int32_t b) {
    int32_t res = 0;
    if (!(a > b)) {
        abort();
    }
    int32_t tmp_arg0 = guards_guards1(a, b);
    res += tmp_arg0;
    size_t tmp_arg1 = sizeof(a);
    if (!(tmp_arg1 > sizeof(b))) {
        abort();
    }
    int32_t tmp_arg2 = guards_guards2(a);
    res += tmp_arg2;
    res += guards_guards3();
    if (!(a < res)) {
        abort();
    }
    int32_t tmp_res3 = 0;
    const guards_ErrorCode tmp_err4 = guards_guards4(a, res, &tmp_res3);
    if (guards_to(tmp_err4)) {
        abort();
    }
    if (!(res > tmp_res3)) {
        abort();
    }
    res += tmp_res3;
    if (!(a < b)) {
        abort();
    }
    int32_t tmp_res5 = 0;
    const guards_ErrorCode tmp_err6 = guards_guards4(a, b, &tmp_res5);
    if (guards_to(tmp_err6)) {
        abort();
    }
    if (!(b > tmp_res5)) {
        abort();
    }
    size_t tmp_arg7 = sizeof(tmp_res5);
    if (!(tmp_arg7 > sizeof(b))) {
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
    res += tmp_res10;
    return res;
}
