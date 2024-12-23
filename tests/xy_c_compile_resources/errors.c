#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct errors_Error errors_Error;

struct errors_Error {
    int32_t errorCode;
};

errors_Error errors_power(int32_t x, int32_t y, int* __res) {
    if (y < 0) {
        return (errors_Error){1};
    }
    int32_t i = 0;
    int32_t __tmp_res0 = 0;
    while (i <= y) {
        __tmp_res0 *= x;
        i++;
    }
    *__res = __tmp_res0;
    return (errors_Error){0};
}

errors_Error errors_errorPropagation(int32_t x, int32_t y, int *__res) {
    int32_t tmp_res0;
    const errors_Error __tmp_err0 = errors_power(x, y, &tmp_res0);
    if (errors_to(__tmp_err0)) {
        return __tmp_err0;
    }
    *__res = tmp_res0 - 1;
    return (errors_Error){0};
}
