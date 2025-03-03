#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct callbacks3_Test1 callbacks3_Test1;
typedef struct callbacks3_Test2 callbacks3_Test2;
typedef struct callbacks3_Test3 callbacks3_Test3;
typedef void (*xy_fp__void)() ;

void callbacks3_test3(void);
void callbacks3_runTests(xy_fp__void* tPtr, size_t tLen);
void callbacks3_special(void);
void callbacks3_runSpecial(xy_fp__void x);

struct callbacks3_Test1 {
    char __empty_structs_are_not_allowed_in_c__;
};
struct callbacks3_Test2 {
    char __empty_structs_are_not_allowed_in_c__;
};
struct callbacks3_Test3 {
    char __empty_structs_are_not_allowed_in_c__;
};

void callbacks3_test1(void) {
}

void callbacks3_test2(void) {
}

void callbacks3_invokeTests(void) {
    xy_fp__void tests[2] = {callbacks3_test1, callbacks3_test3};
    callbacks3_runTests(tests, 2);
    xy_fp__void moreTests[1] = {callbacks3_test2};
    callbacks3_runTests(moreTests, 1);
    const xy_fp__void specialTest = callbacks3_special;
    callbacks3_runSpecial(specialTest);
}

void callbacks3_special(void) {
}

void callbacks3_test3(void) {
}

void callbacks3_runTests(xy_fp__void* tPtr, size_t tLen) {
}

void callbacks3_runSpecial(xy_fp__void x) {
    x();
}
