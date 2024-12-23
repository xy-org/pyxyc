#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct for1_Fib for1_Fib;

struct for1_Fib {
    int32_t m_a;
    int32_t m_b;
};

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

for1_Fib for1_fibonacci(void) {
    return (for1_Fib){0, 1};
}

bool for1_valid(for1_Fib fib) {
    return true;
}

for1_Fib for1_next(for1_Fib fib) {
    return (for1_Fib){fib.m_a + fib.m_b, fib.m_a};
}

int32_t for1_deref(for1_Fib fib) {
    return fib.m_a;
}

int32_t for1_mulFibs(int32_t lim) {
    int32_t res = 1;
    {
        int32_t tmp_iter0 = 0;
        for1_Fib tmp_iter1 = for1_fibonacci();
        for (; tmp_iter0 < lim && for1_valid(tmp_iter1); ++tmp_iter0, tmp_iter1 = for1_next(tmp_iter1)) {
            const int32_t fib = for1_deref(tmp_iter1);
            res *= fib;
        }
    }
    return res;
}
