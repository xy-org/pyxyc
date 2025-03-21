#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t ifs_statementLike(int32_t p_x, int32_t p_y) {
    if (p_x < p_y) {
        return p_x * p_y * 3;
    } else {
        return p_y * 2;
    }
}

int32_t ifs_expressionLike(int32_t p_x, int32_t p_y) {
    int32_t tmp0 = 0;
    if (p_x < p_y) {
        tmp0 = p_x * p_y * 3;
    } else {
        tmp0 = p_y * 2;
    }
    return tmp0;
}

int32_t ifs_namedIf(int32_t p_x, int32_t p_y) {
    int32_t tmp_res0 = 0;
    if (p_x < p_y) {
        tmp_res0 = p_x * p_y * 3;
    } else {
        tmp_res0 = p_y * 2;
    }
    const int32_t l_res = tmp_res0;
    return l_res;
}

int32_t ifs_elifs(int32_t p_x, int32_t p_y) {
    int32_t tmp_res0 = 0;
    if (p_x < p_y) {
        tmp_res0 = 0;
        ifs_namedIf(p_x, p_y);
    } else if (p_x < p_y) {
        tmp_res0 = 1;
    } else {
        tmp_res0 = 2;
    }
    return tmp_res0;
}

int32_t ifs_elifs2(int32_t p_x, int32_t p_y) {
    int32_t tmp_res0 = 0;
    if (p_x < p_y) {
        tmp_res0 = 0;
    } else if (p_x < p_y) {
        tmp_res0 = 1;
    } else {
        tmp_res0 = 2;
    }
    return tmp_res0;
}

int32_t ifs_chainedIfs(int32_t p_x, int32_t p_y) {
    int32_t tmp0 = 0;
    if (p_x > p_y) {
        tmp0 = 1;
    } else if (p_x < p_y) {
        tmp0 = -1;
    } else {
        tmp0 = 0;
    }
    const int32_t l_a = tmp0;
    return l_a;
}
