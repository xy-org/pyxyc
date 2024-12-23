#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct fors_Fib fors_Fib;

struct fors_Fib {
    int32_t m_a;
    int32_t m_b;
};

void fors_busywait(void) {
    for (uint32_t i = 0;; ++i) {
        if (i == 10000) {
            break;
        }
    }
}

void fors_busywait2(void) {
    for (int32_t tmp_iter0 = 0; tmp_iter0 < 10000; ++tmp_iter0) {
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

fors_Fib fors_fibonacci(void) {
    return (fors_Fib){0, 1};
}

bool fors_valid(fors_Fib fib) {
    return true;
}

fors_Fib fors_next(fors_Fib fib) {
    return (fors_Fib){fib.m_a + fib.m_b, fib.m_a};
}

int32_t fors_deref(fors_Fib fib) {
    return fib.m_a;
}

int32_t fors_mulFibs(int32_t lim) {
    int32_t res = 1;
    {
        int32_t tmp_iter0 = 0;
        fors_Fib tmp_iter1 = fors_fibonacci();
        for (; tmp_iter0 < lim && fors_valid(tmp_iter1); ++tmp_iter0, tmp_iter1 = fors_next(tmp_iter1)) {
            const int32_t fib = fors_deref(tmp_iter1);
            res *= fib;
        }
    }
    return res;
}
