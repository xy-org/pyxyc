#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void macros2_test(void) {
    const int32_t l_arg1 = 10;
    const int32_t l_arg2 = 20;
    const int32_t l_res = l_arg1 + 1 + 1 + l_arg2;
}
