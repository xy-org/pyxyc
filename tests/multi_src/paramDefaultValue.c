#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t paramDefaultValue_module1_calcDefaultValue(int32_t p_num) {
    return p_num * 2;
}

int32_t paramDefaultValue_module1_func(int32_t p_a, int32_t p_b) {
    return p_a + p_b;
}

void paramDefaultValue_module1_test(void) {
    paramDefaultValue_module1_func(5, paramDefaultValue_module1_calcDefaultValue(5));
    paramDefaultValue_module1_func(5, 10);
}

int32_t paramDefaultValue_module2_calcDefaultValue(int32_t p_num) {
    return p_num * 10;
}

int32_t paramDefaultValue_module2_myfunc(int32_t p_a, int32_t p_b) {
    return p_a + p_b;
}

void paramDefaultValue_test(void) {
    const int32_t l_a = 5;
    paramDefaultValue_module1_func(l_a, paramDefaultValue_module1_calcDefaultValue(l_a));
    paramDefaultValue_module1_func(l_a, 10);
    paramDefaultValue_module1_func(l_a * 10, paramDefaultValue_module1_calcDefaultValue(l_a * 10));
    paramDefaultValue_module2_myfunc(l_a, paramDefaultValue_module2_calcDefaultValue(l_a));
    paramDefaultValue_module2_myfunc(l_a, 10);
}
