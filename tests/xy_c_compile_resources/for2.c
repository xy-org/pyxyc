#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct for2_Fib for2_Fib;

struct for2_Fib {
    int32_t m_a;
    int32_t m_b;
};

for2_Fib for2_fibonacci(void) {
    return (for2_Fib){0, 1};
}

bool for2_valid(for2_Fib fib) {
    return true;
}

void for2_next(for2_Fib* fib) {
    *fib = (for2_Fib){fib->m_a + fib->m_b, fib->m_a};
}

int32_t for2_get(for2_Fib fib) {
    return fib.m_a;
}

int32_t for2_mulFibs(int32_t lim) {
    int32_t res = 1;
    {
        int32_t tmp_iter0 = 0;
        for2_Fib tmp_iter1 = for2_fibonacci();
        for (; tmp_iter0 < lim && for2_valid(tmp_iter1); ++tmp_iter0, for2_next(&tmp_iter1)) {
            res *= for2_get(tmp_iter1);
        }
    }
    return res;
}
