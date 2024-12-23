#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t boundaryExpr2_sum(int32_t x, int32_t y) {
    return x + y;
}

int32_t boundaryExpr2_quadruple(int32_t* num) {
    *num *= 4;
    return *num;
}

void boundaryExpr2_print(int32_t num) {
}

void boundaryExpr2_main(void) {
    int32_t a = 1;
    boundaryExpr2_print(boundaryExpr2_sum(a, a));
    boundaryExpr2_print(boundaryExpr2_sum(a * 2, a * 2));
    int32_t tmp_arg0 = boundaryExpr2_quadruple(&a);
    boundaryExpr2_print(boundaryExpr2_sum(tmp_arg0, boundaryExpr2_quadruple(&a)));
    int32_t tmp_arg1 = boundaryExpr2_quadruple(&a);
    boundaryExpr2_print(boundaryExpr2_sum(tmp_arg1, 10));
}
