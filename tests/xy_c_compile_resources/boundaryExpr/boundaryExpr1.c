#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t boundaryExpr1_sumWithTag(int32_t x, int32_t y) {
    return x + y;
}

void boundaryExpr1_print(int32_t num) {
}

void boundaryExpr1_main(void) {
    const int32_t a = 1;
    boundaryExpr1_print(boundaryExpr1_sumWithTag(a, 10));
}
