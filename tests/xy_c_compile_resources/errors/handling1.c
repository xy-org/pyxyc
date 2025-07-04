#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct handling1_Error handling1_Error;

struct handling1_Error {
    int32_t m_code;
};

void handling1_unhandled(handling1_Error p_err) {
}

handling1_Error handling1_errorProne(void) {
    return (handling1_Error){5};
}

handling1_Error handling1_doWork(void) {
    const handling1_Error tmp_0_err = handling1_errorProne();
    if (tmp_0_err.m_code != 0) {
        return tmp_0_err;
    }
    return (handling1_Error){0};
}

void handling1_test1(void) {
    const handling1_Error tmp_0_err = handling1_doWork();
    if (tmp_0_err.m_code != 0) {
        handling1_unhandled(tmp_0_err);
        abort();
    }
}

void handling1_test2(void) {
    handling1_unhandled((handling1_Error){10});
    abort();
}
