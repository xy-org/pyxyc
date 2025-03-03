#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void moveOperators1_assert(bool cond);

void moveOperators1_test(void) {
    int32_t a = 10;
    int32_t b = 0;
    int32_t tmp_arg0 = a;
    a = 0;
    b = tmp_arg0;
    int32_t tmp_arg1 = b;
    b = 0;
    const int32_t c = tmp_arg1;
    moveOperators1_assert(a == 0);
    moveOperators1_assert(b == 0);
    moveOperators1_assert(c == 10);
}

void moveOperators1_assert(bool cond) {
}
