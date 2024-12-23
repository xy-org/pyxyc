#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t paramsVsArgs_func1(int32_t a, int32_t b, int32_t c) {
    return a * b * c;
}

int32_t paramsVsArgs_func2(int32_t c) {
    return c;
}

void* paramsVsArgs_func3(void* ptr) {
    return ptr;
}

void paramsVsArgs_test(void) {
    int32_t a = paramsVsArgs_func1(0, 1, 0 + 1);
    const int32_t b = paramsVsArgs_func1(a, a, a + a);
    const int32_t c = paramsVsArgs_func2(a + b);
    const int32_t* d = paramsVsArgs_func3(&a);
    float* e = paramsVsArgs_func3(&a);
    const int32_t* f = paramsVsArgs_func3(&e);
}
