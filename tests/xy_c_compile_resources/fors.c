#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void fors_busywait(void) {
    for (uint32_t i = 0;; ++i) {
        if (i == 10000) {
            break;
        }
    }
}

int32_t fors_sumUpTo(int32_t start, int32_t end) {
    int32_t res = 0;
    for (int32_t i = start; i < end; ++i) {
        res += i;
    }
    return res;
}

int32_t fors_multUpTo(int32_t start, int32_t end, int32_t step) {
    int32_t res = 0;
    for (int32_t i = start; i < end; i += step) {
        res *= fors_sumUpTo(start, i);
    }
    return res;
}

int32_t fors_doubleLoop(int32_t limX, int32_t limY) {
    int32_t res = 1;
    for (int32_t i = 0; i < limX; ++i) {
        for (int32_t j = 0; j < limY; ++j) {
            res *= i + j;
        }
    }
    return res;
}

int32_t fors_zipLoop(int32_t limX, int32_t limY) {
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
