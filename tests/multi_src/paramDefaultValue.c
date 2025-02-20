#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t paramDefaultValue_module1_calcDefaultValue(int32_t num) {
    return num * 2;
}

int32_t paramDefaultValue_module1_func(int32_t a, int32_t b) {
    return a + b;
}

void paramDefaultValue_module1_test(void) {
    paramDefaultValue_module1_func(5, paramDefaultValue_module1_calcDefaultValue(5));
    paramDefaultValue_module1_func(5, 10);
}

int32_t paramDefaultValue_module2_calcDefaultValue(int32_t num) {
    return num * 10;
}

int32_t paramDefaultValue_module2_myfunc(int32_t a, int32_t b) {
    return a + b;
}

void paramDefaultValue_test(void) {
    const int32_t a = 5;
    paramDefaultValue_module1_func(a, paramDefaultValue_module1_calcDefaultValue(a));
    paramDefaultValue_module1_func(a, 10);
    paramDefaultValue_module1_func(a * 10, paramDefaultValue_module1_calcDefaultValue(a * 10));
    paramDefaultValue_module2_myfunc(a, paramDefaultValue_module2_calcDefaultValue(a));
    paramDefaultValue_module2_myfunc(a, 10);
}
