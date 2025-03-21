#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t boundaryExpr1_sumWithTag(int32_t p_x, int32_t p_y) {
    return p_x + p_y;
}

void boundaryExpr1_print(int32_t p_num) {
}

void boundaryExpr1_main(void) {
    const int32_t l_a = 1;
    boundaryExpr1_print(boundaryExpr1_sumWithTag(l_a, 10));
}
