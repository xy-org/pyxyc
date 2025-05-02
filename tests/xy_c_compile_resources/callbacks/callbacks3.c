#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct callbacks3__EMPTY_STRUCT_ callbacks3_Test1;
typedef struct callbacks3__EMPTY_STRUCT_ callbacks3_Test2;
typedef struct callbacks3__EMPTY_STRUCT_ callbacks3_Test3;
typedef void (*xy_fp__void)(void) ;

void callbacks3_test3(void);
void callbacks3_runTests(xy_fp__void* p_tPtr, size_t p_tLen);
void callbacks3_special(void);
void callbacks3_runSpecial(xy_fp__void p_x);

struct callbacks3__EMPTY_STRUCT_ {
    char __empty_structs_are_not_allowed_in_c__;
};

void callbacks3_test1(void) {
}

void callbacks3_test2(void) {
}

void callbacks3_invokeTests(void) {
    xy_fp__void l_tests[2] = {callbacks3_test1, callbacks3_test3};
    callbacks3_runTests(l_tests, 2);
    xy_fp__void l_moreTests[1] = {callbacks3_test2};
    callbacks3_runTests(l_moreTests, 1);
    const xy_fp__void l_specialTest = callbacks3_special;
    callbacks3_runSpecial(l_specialTest);
}

void callbacks3_special(void) {
}

void callbacks3_test3(void) {
}

void callbacks3_runTests(xy_fp__void* p_tPtr, size_t p_tLen) {
}

void callbacks3_runSpecial(xy_fp__void p_x) {
    p_x();
}
