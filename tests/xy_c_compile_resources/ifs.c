#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t ifs_statementLike(int32_t x, int32_t y) {
    if (x < y) {
        return x * y * 3;
    } else {
        return y * 2;
    }
}

int32_t ifs_expressionLike(int32_t x, int32_t y) {
    int32_t __tmp0;
    if (x < y) {
        __tmp0 = x * y * 3;
    } else {
        __tmp0 = y * 2;
    }
    return __tmp0;
}

int32_t ifs_namedIf(int32_t x, int32_t y) {
    int32_t __tmp_res0;
    if (x < y) {
        __tmp_res0 = x * y * 3;
    } else {
        __tmp_res0 = y * 2;
    }
    const int32_t res = __tmp_res0;
    return res;
}

int32_t ifs_chainedIfs(int32_t x, int32_t y) {
    int32_t __tmp0;
    if (x > y) {
        __tmp0 = 1;
    } else if (x < y) {
        __tmp0 = -1;
    } else {
        __tmp0 = 0;
    }
    const int32_t a = __tmp0;
    return a;
}
