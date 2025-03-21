#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct errors_Error errors_Error;
typedef struct errors_Error2 errors_Error2;

void errors_print(int32_t p_a);

struct errors_Error {
    int32_t m_errorCode;
};
struct errors_Error2 {
    int32_t m_errorCode;
    int32_t m_a;
    int32_t m_b;
};

errors_Error errors_power(int32_t p_x, int32_t p_y, int32_t* _res0) {
    if (p_y < 0) {
        return (errors_Error){1};
    }
    int32_t l_i = 0;
    int32_t tmp_res1 = 1;
    while (l_i <= p_y) {
        tmp_res1 *= p_x;
        l_i++;
    }
    *_res0 = tmp_res1;
    return (errors_Error){0};
}

errors_Error errors_errorPropagation(int32_t p_x, int32_t p_y, int32_t* _res0) {
    int32_t tmp_res0 = 0;
    const errors_Error tmp_err1 = errors_power(p_x, p_y, &tmp_res0);
    if (tmp_err1.m_errorCode != 0) {
        return tmp_err1;
    }
    *_res0 = tmp_res0 - 1;
    return (errors_Error){0};
}

errors_Error errors_doWork(int32_t p_x) {
    int32_t tmp_res0 = 0;
    const errors_Error tmp_err1 = errors_power(p_x, p_x, &tmp_res0);
    if (tmp_err1.m_errorCode != 0) {
        return tmp_err1;
    }
    const int32_t l_y = tmp_res0;
    errors_print(l_y);
    return (errors_Error){0};
}

void errors_print(int32_t p_a) {
}

errors_Error errors_doNothing(void) {
    return (errors_Error){0};
}

errors_Error errors_callReturningErrorButNoResult(int32_t p_a, int32_t p_b, int32_t* _res0) {
    const errors_Error tmp_err0 = errors_doWork(p_a);
    if (tmp_err0.m_errorCode != 0) {
        return tmp_err0;
    }
    const errors_Error tmp_err2 = errors_doWork(p_b);
    if (tmp_err2.m_errorCode != 0) {
        return tmp_err2;
    }
    return (errors_Error){0};
}

int32_t errors_errorInFuncThatDoesNotIssueAndError(int32_t p_x, int32_t p_y) {
    if (p_x < p_y) {
        abort();
    }
    return p_x * p_y;
}

errors_Error2 errors_errorInFuncThatIssuesDifferentKindOfError(int32_t p_x, int32_t p_y, int32_t* _res0) {
    if (p_x > 2 * p_y) {
        abort();
    }
    if (p_x >= p_y) {
        return (errors_Error2){2, p_x, p_y};
    }
    *_res0 = p_x + p_y;
    return (errors_Error2){0};
}
