#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct errorInBody_Error errorInBody_Error;

struct errorInBody_Error {
    int32_t m_status;
};

errorInBody_Error errorInBody_fail(void) {
    return (errorInBody_Error){10};
}

void errorInBody_test1(bool p_b) {
    if (p_b) {
        const errorInBody_Error tmp_0_err = errorInBody_fail();
        if (tmp_0_err.m_status != 0) {
            abort();
        }
    }
}

void errorInBody_test2(bool p_b) {
    if (p_b) {
        const errorInBody_Error tmp_0_err = errorInBody_fail();
        if (tmp_0_err.m_status != 0) {
            abort();
        }
    }
}
