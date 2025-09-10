#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t exprBlocks4_test(int32_t p_x, int32_t p_y) {
    int32_t tmp_0_a = 0;
    {
        if (!(p_x > 0)) {
            abort();
        }
        tmp_0_a = 2 * p_x;
        if (!(tmp_0_a > 0)) {
            abort();
        }
    }
    int32_t tmp_1_a = 0;
    {
        tmp_1_a = p_x - 10;
    }
    const int32_t l_a = tmp_0_a + tmp_1_a;
    return l_a;
}
