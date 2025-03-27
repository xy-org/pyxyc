#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct callbacks2_Test callbacks2_Test;
typedef void (*xy_fp__void)() ;

void callbacks2_test3(void);

struct callbacks2_Test {
    char __empty_structs_are_not_allowed_in_c__;
};

void callbacks2_test1(void) {
}

void callbacks2_test2(void) {
}

void callbacks2_invokeTests(void) {
    const xy_fp__void l_tests[3] = {callbacks2_test1, callbacks2_test2, callbacks2_test3};
    for (size_t tmp_0_iter = 0; tmp_0_iter < 3; ++tmp_0_iter) {
        l_tests[tmp_0_iter]();
    }
}

void callbacks2_test3(void) {
}
