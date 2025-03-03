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
    for (int32_t tmp_iter0 = 0; tmp_iter0 < 10000; ++tmp_iter0) {
    }
}

int32_t for1_sumUpTo(int32_t start, int32_t end) {
    int32_t res = 0;
    for (int32_t i = start; i < end; ++i) {
        res += i;
    }
    return res;
}

int32_t for1_multUpTo(int32_t start, int32_t end, int32_t step) {
    int32_t res = 0;
    for (int32_t i = start; i < end; i += step) {
        res *= for1_sumUpTo(start, i);
    }
    return res;
}

int32_t for1_doubleLoop(int32_t limX, int32_t limY) {
    int32_t res = 1;
    for (int32_t i = 0; i < limX; ++i) {
        for (int32_t j = 0; j < limY; ++j) {
            res *= i + j;
        }
    }
    return res;
}

int32_t for1_zipLoop(int32_t limX, int32_t limY) {
    int32_t res = 1;
    {
        int32_t i = 0;
        int32_t j = 0;
        for (; i < limX && j < limY; ++i, ++j) {
            res *= i + j;
        }
    }
    return res;
}
