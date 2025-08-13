#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

bool mixingAndOr_pred1(int32_t p_a) {
    return p_a > 0;
}

bool mixingAndOr_pred2(int32_t p_a) {
    return p_a < -10;
}

bool mixingAndOr_pred3(int32_t p_a, int32_t p_b) {
    return p_a >= p_b;
}

void mixingAndOr_test1(int32_t p_a, int32_t p_b) {
    bool l_cond = mixingAndOr_pred1(p_a);
    l_cond = l_cond || mixingAndOr_pred2(p_b);
    l_cond = l_cond && mixingAndOr_pred3(p_a, p_b);
}

bool mixingAndOr_test2(int32_t p_a, int32_t p_b) {
    return (p_a >= 10 && p_a < 20) || (p_b >= p_a && p_b < 10);
}
