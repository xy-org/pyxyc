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
    int32_t tmp_0 = 0;
    if (p_x < p_y) {
        tmp_0 = p_x * p_y * 3;
    } else {
        tmp_0 = p_y * 2;
    }
    return tmp_0;
}

int32_t ifs_namedIf(int32_t p_x, int32_t p_y) {
    int32_t tmp_0_res = 0;
    if (p_x < p_y) {
        tmp_0_res = p_x * p_y * 3;
    } else {
        tmp_0_res = p_y * 2;
    }
    const int32_t l_res = tmp_0_res;
    return l_res;
}

int32_t ifs_elifs(int32_t p_x, int32_t p_y) {
    int32_t tmp_0_res = 0;
    if (p_x < p_y) {
        tmp_0_res = 0;
        ifs_namedIf(p_x, p_y);
    } else if (p_x < p_y) {
        tmp_0_res = 1;
    } else {
        tmp_0_res = 2;
    }
    return tmp_0_res;
}

int32_t ifs_elifs2(int32_t p_x, int32_t p_y) {
    int32_t tmp_0_res = 0;
    if (p_x < p_y) {
        tmp_0_res = 0;
    } else if (p_x < p_y) {
        tmp_0_res = 1;
    } else {
        tmp_0_res = 2;
    }
    return tmp_0_res;
}

int32_t ifs_chainedIfs(int32_t p_x, int32_t p_y) {
    int32_t tmp_0 = 0;
    if (p_x > p_y) {
        tmp_0 = 1;
    } else if (p_x < p_y) {
        tmp_0 = -1;
    } else {
        tmp_0 = 0;
    }
    const int32_t l_a = tmp_0;
    return l_a;
}
