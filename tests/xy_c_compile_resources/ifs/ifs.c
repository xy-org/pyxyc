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
    int32_t tmp0 = 0;
    if (x < y) {
        tmp0 = x * y * 3;
    } else {
        tmp0 = y * 2;
    }
    return tmp0;
}

int32_t ifs_namedIf(int32_t x, int32_t y) {
    int32_t tmp_res0 = 0;
    if (x < y) {
        tmp_res0 = x * y * 3;
    } else {
        tmp_res0 = y * 2;
    }
    const int32_t res = tmp_res0;
    return res;
}

int32_t ifs_elifs(int32_t x, int32_t y) {
    int32_t tmp_res0 = 0;
    if (x < y) {
        tmp_res0 = 0;
        ifs_namedIf(x, y);
    } else if (x < y) {
        tmp_res0 = 1;
    } else {
        tmp_res0 = 2;
    }
    return tmp_res0;
}

int32_t ifs_elifs2(int32_t x, int32_t y) {
    int32_t tmp_res0 = 0;
    if (x < y) {
        tmp_res0 = 0;
    } else if (x < y) {
        tmp_res0 = 1;
    } else {
        tmp_res0 = 2;
    }
    return tmp_res0;
}

int32_t ifs_chainedIfs(int32_t x, int32_t y) {
    int32_t tmp0 = 0;
    if (x > y) {
        tmp0 = 1;
    } else if (x < y) {
        tmp0 = -1;
    } else {
        tmp0 = 0;
    }
    const int32_t a = tmp0;
    return a;
}
