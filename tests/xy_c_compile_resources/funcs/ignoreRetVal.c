#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t ignoreRetVal_fun(int32_t p_a, int32_t p_b) {
    return p_a * p_b;
}

void ignoreRetVal_voidFunc(void) {
}

void ignoreRetVal_test(int32_t p_a, int32_t p_b) {
    ignoreRetVal_fun(p_a, p_b);
    ignoreRetVal_fun(p_a, p_b);
    ignoreRetVal_voidFunc();
    ignoreRetVal_voidFunc();
}
