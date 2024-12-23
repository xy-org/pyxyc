#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct errors_Error errors_Error;

struct errors_Error {
    int32_t xy_errorCode;
};

bool errors_to(errors_Error err) {
    return err.xy_errorCode != 0;
}

errors_Error errors_power(int32_t x, int32_t y, int32_t* _res0) {
    if (y < 0) {
        return (errors_Error){1};
    }
    int32_t i = 0;
    int32_t __tmp_res0 = 1;
    while (i <= y) {
        __tmp_res0 *= x;
        i++;
    }
    *_res0 = __tmp_res0;
    return (errors_Error){0};
}

errors_Error errors_errorPropagation(int32_t x, int32_t y, int32_t* _res0) {
    int32_t __tmp_res0 = 0;
    const errors_Error __tmp_err1 = errors_power(x, y, &__tmp_res0);
    if (errors_to(__tmp_err1)) {
        return __tmp_err1;
    }
    *_res0 = __tmp_res0 - 1;
    return (errors_Error){0};
}

errors_Error errors_doWork(int32_t x) {
    int32_t __tmp_res0 = 0;
    const errors_Error __tmp_err1 = errors_power(x, x, &__tmp_res0);
    if (errors_to(__tmp_err1)) {
        return __tmp_err1;
    }
    const int32_t y = __tmp_res0;
    errors_print(y);
    return (errors_Error){0};
}

void errors_print(int32_t a) {
}

errors_Error errors_doNothing(void) {
    return (errors_Error){0};
}

errors_Error errors_callReturningErrorButNoResult(int32_t a, int32_t b, int32_t* _res0) {
    const errors_Error __tmp_err0 = errors_doWork(a);
    if (errors_to(__tmp_err0)) {
        return __tmp_err0;
    }
    const errors_Error __tmp_err1 = errors_doWork(b);
    if (errors_to(__tmp_err1)) {
        return __tmp_err1;
    }
    return (errors_Error){0};
}
