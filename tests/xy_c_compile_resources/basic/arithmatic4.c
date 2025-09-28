#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <math.h>

int32_t arithmatic4_test__Int__Int(int32_t p_x, int32_t p_y) {
    const int32_t l_a = pow((double)p_x, (double)2);
    const int32_t l_b = pow((double)p_y, (double)p_x);
    return (int32_t)pow((double)l_a, (double)l_b);
}

float arithmatic4_test__Float__Float(float p_x, float p_y) {
    const float l_a = powf(p_x, p_y);
    const float l_b = powf(p_x, 1.0f / p_y);
    return l_a + l_b;
}
