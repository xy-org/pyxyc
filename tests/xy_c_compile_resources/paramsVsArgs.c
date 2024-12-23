#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t paramsVsArgs_func1(int32_t a, int32_t b, int32_t c) {
    return a * b * c;
}

int32_t paramsVsArgs_func2(int32_t c) {
    return c;
}
