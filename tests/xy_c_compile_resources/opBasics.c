#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void opBasics_test1(int32_t p_x, int32_t p_y) {
    const int32_t l_a = p_x + p_y;
    const int32_t l_b = p_x - p_y;
    const int32_t l_c = p_x * p_y;
    if (!(p_y != 0)) {
        abort();
    }
    const int32_t l_d = p_x / p_y;
    if (!(p_y != 0)) {
        abort();
    }
    const int32_t l_e = p_x % p_y;
}

void opBasics_test2(int8_t p_x, int8_t p_y) {
    const int8_t l_a = p_x + p_y;
    const int8_t l_b = p_x - p_y;
    const int8_t l_c = p_x * p_y;
    if (!(p_y != 0)) {
        abort();
    }
    const int8_t l_d = p_x / p_y;
    if (!(p_y != 0)) {
        abort();
    }
    const int8_t l_e = p_x % p_y;
}

void opBasics_test3(uint16_t p_x, uint16_t p_y) {
    const uint16_t l_a = p_x + p_y;
    const uint16_t l_b = p_x - p_y;
    const uint16_t l_c = p_x * p_y;
    if (!(p_y != 0)) {
        abort();
    }
    const uint16_t l_d = p_x / p_y;
    if (!(p_y != 0)) {
        abort();
    }
    const uint16_t l_e = p_x % p_y;
}

void opBasics_test4(float p_x, float p_y) {
    const float l_a = p_x + p_y;
    const float l_b = p_x - p_y;
    const float l_c = p_x * p_y;
    const float l_d = p_x / p_y;
}
