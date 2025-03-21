#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void moveOperators1_assert(bool p_cond);

void moveOperators1_test(void) {
    int32_t l_a = 10;
    int32_t l_b = 0;
    int32_t tmp_arg0 = l_a;
    l_a = 0;
    l_b = tmp_arg0;
    int32_t tmp_arg1 = l_b;
    l_b = 0;
    const int32_t l_c = tmp_arg1;
    moveOperators1_assert(l_a == 0);
    moveOperators1_assert(l_b == 0);
    moveOperators1_assert(l_c == 10);
}

void moveOperators1_assert(bool p_cond) {
}
