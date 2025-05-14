#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t paramTypeEnum_func__Int__Int(int32_t p_a, int32_t p_b) {
    return p_a + p_b;
}

float paramTypeEnum_func__Float__Float(float p_a, float p_b) {
    return p_a + p_b;
}

int8_t paramTypeEnum_func__Byte__Byte(int8_t p_a, int8_t p_b) {
    return p_a + p_b;
}

int64_t paramTypeEnum_test(void) {
    const int32_t l_a = paramTypeEnum_func__Int__Int(5, 10);
    const float l_b = paramTypeEnum_func__Float__Float(3.14f, 9.8f);
    const int8_t l_c = paramTypeEnum_func__Byte__Byte((int8_t)127, (int8_t)-1);
}
