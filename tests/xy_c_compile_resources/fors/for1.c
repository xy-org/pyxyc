#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void for1_busywait(void) {
    for (uint32_t i = 0;; ++i) {
        if (i == 10000) {
            break;
        }
    }
}

void for1_busywait2(void) {
    for (int32_t tmp_0_iter = 0; tmp_0_iter < 10000; ++tmp_0_iter) {
    }
}

int32_t for1_sumUpTo(int32_t p_start, int32_t p_end) {
    int32_t l_res = 0;
    for (int32_t i = p_start; i < p_end; ++i) {
        l_res += i;
    }
    return l_res;
}

int32_t for1_multUpTo(int32_t p_start, int32_t p_end, int32_t p_step) {
    int32_t l_res = 0;
    for (int32_t i = p_start; i < p_end; i += p_step) {
        l_res *= for1_sumUpTo(p_start, i);
    }
    return l_res;
}

int32_t for1_doubleLoop(int32_t p_limX, int32_t p_limY) {
    int32_t l_res = 1;
    for (int32_t i = 0; i < p_limX; ++i) {
        for (int32_t j = 0; j < p_limY; ++j) {
            l_res *= i + j;
        }
    }
    return l_res;
}

int32_t for1_zipLoop(int32_t p_limX, int32_t p_limY) {
    int32_t l_res = 1;
    {
        int32_t i = 0;
        int32_t j = 0;
        for (; i < p_limX && j < p_limY; ++i, ++j) {
            l_res *= i + j;
        }
    }
    return l_res;
}
