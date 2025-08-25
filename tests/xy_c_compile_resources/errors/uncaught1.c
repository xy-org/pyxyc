#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct uncaught1_Error uncaught1_Error;

struct uncaught1_Error {
    int32_t m_code;
};

uncaught1_Error uncaught1_errorProne(int32_t p_a, int32_t* _res0) {
    if (p_a < 0) {
        return (uncaught1_Error){10};
    }
    *_res0 = 0;
    return (uncaught1_Error){0};
}

void uncaught1_test(int32_t p_var) {
    int32_t tmp_0_res = 0;
    const uncaught1_Error tmp_1_err = uncaught1_errorProne(p_var - 1, &tmp_0_res);
    if (tmp_1_err.m_code != 0) {
        fprintf(stderr, "\n");
        fprintf(stderr, "%s=Error{code=%d}", "Error", tmp_1_err.m_code);
        fprintf(stderr, "\ntests/xy_c_compile_resources/errors/uncaught1.xy:%d ", 15);
        fprintf(stderr, "When calling uncaught1.errorProne!\n");
        fprintf(stderr, "| %s\n", "    errorProne(var - 1);");
        fprintf(stderr, "Arguments to Function are:\n");
        fprintf(stderr, "    %s=%d\n", "a", p_var - 1);
        exit(200);
    }
}
