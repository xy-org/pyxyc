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
    res += guards_guards1(a, b);
    size_t tmp_arg0 = sizeof(a);
    if (!(tmp_arg0 > sizeof(b))) {
        abort();
    }
    res += guards_guards2(a);
    res += guards_guards3();
    if (!(a < res)) {
        abort();
    }
    int32_t tmp_res1 = 0;
    const guards_ErrorCode tmp_err2 = guards_guards4(a, res, &tmp_res1);
    if (guards_to(tmp_err2)) {
        abort();
    }
    if (!(res > tmp_res1)) {
        abort();
    }
    res += tmp_res1;
    if (!(a < b)) {
        abort();
    }
    int32_t tmp_res3 = 0;
    const guards_ErrorCode tmp_err4 = guards_guards4(a, b, &tmp_res3);
    if (guards_to(tmp_err4)) {
        abort();
    }
    if (!(b > tmp_res3)) {
        abort();
    }
    size_t tmp_arg5 = sizeof(tmp_res3);
    if (!(tmp_arg5 > sizeof(b))) {
        abort();
    }
    int32_t tmp_arg6 = guards_guards2(tmp_res3);
    int32_t tmp_arg7 = guards_guards3();
    if (!(tmp_arg6 < tmp_arg7)) {
        abort();
    }
    int32_t tmp_res8 = 0;
    const guards_ErrorCode tmp_err9 = guards_guards4(tmp_arg6, tmp_arg7, &tmp_res8);
    if (guards_to(tmp_err9)) {
        abort();
    }
    if (!(tmp_arg7 > tmp_res8)) {
        abort();
    }
    res += tmp_res8;
    return res;
}
