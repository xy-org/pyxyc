#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct macroErrorAndDtor_module1_Fib macroErrorAndDtor_module1_Fib;
typedef struct macroErrorAndDtor_module1_Error macroErrorAndDtor_module1_Error;

struct macroErrorAndDtor_module1_Fib {
    int32_t m_a;
    int32_t m_b;
};
struct macroErrorAndDtor_module1_Error {
    int32_t m_num;
};

void macroErrorAndDtor_module1_dtor(macroErrorAndDtor_module1_Fib p_f) {
}

macroErrorAndDtor_module1_Error macroErrorAndDtor_module1_mkFib(macroErrorAndDtor_module1_Fib* _res0) {
    *_res0 = (macroErrorAndDtor_module1_Fib){0, 1};
    return (macroErrorAndDtor_module1_Error){0};
}

void macroErrorAndDtor_module1_next(macroErrorAndDtor_module1_Fib* p_fib) {
    *p_fib = (macroErrorAndDtor_module1_Fib){p_fib->m_a + p_fib->m_b, p_fib->m_a};
}

void macroErrorAndDtor_test(void) {
    macroErrorAndDtor_module1_Fib tmp_0_res = (macroErrorAndDtor_module1_Fib){0, 1};
    const macroErrorAndDtor_module1_Error tmp_1_err = macroErrorAndDtor_module1_mkFib(&tmp_0_res);
    if (tmp_1_err.m_num != 0) {
        abort();
    }
    {
        macroErrorAndDtor_module1_Fib tmp_3_iter = tmp_0_res;
        for (; true; macroErrorAndDtor_module1_next(&tmp_3_iter)) {
        }
        macroErrorAndDtor_module1_dtor(tmp_3_iter);
    }
}
