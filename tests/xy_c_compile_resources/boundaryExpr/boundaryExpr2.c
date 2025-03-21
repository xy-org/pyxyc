#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t boundaryExpr2_quadruple(int32_t* p_num) {
    *p_num *= 4;
    return *p_num;
}

void boundaryExpr2_print(int32_t p_num) {
}

void boundaryExpr2_main(void) {
    int32_t l_a = 1;
    boundaryExpr2_print(l_a + l_a);
    boundaryExpr2_print(l_a * 2 + l_a * 2);
    int32_t tmp_arg0 = boundaryExpr2_quadruple(&l_a);
    int32_t tmp_arg1 = tmp_arg0 + boundaryExpr2_quadruple(&l_a);
    boundaryExpr2_print(tmp_arg1);
    int32_t tmp_arg2 = boundaryExpr2_quadruple(&l_a);
    boundaryExpr2_print(tmp_arg2 + 10);
}
