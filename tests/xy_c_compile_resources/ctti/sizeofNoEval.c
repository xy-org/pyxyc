#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t sizeofNoEval_fun(int32_t* p_a) {
    (*p_a)++;
    return *p_a;
}

void sizeofNoEval_test(void) {
    int32_t l_var = 0;
    sizeof(int32_t);
}
