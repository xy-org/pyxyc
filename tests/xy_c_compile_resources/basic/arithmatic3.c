#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int64_t arithmatic3_test1__1(int64_t p_x, int64_t p_y) {
    const int64_t l_a = p_x * p_y;
    if (!(p_y != 0)) {
        abort();
    }
    const int64_t l_b = p_x / p_y;
    return (__int128_t)l_a * (__int128_t)l_b >> 64;
}

uint64_t arithmatic3_test1__2(uint64_t p_x, uint64_t p_y) {
    const uint64_t l_a = p_x * p_y;
    if (!(p_y != 0)) {
        abort();
    }
    const uint64_t l_b = p_x / p_y;
    return (__uint128_t)l_a * (__uint128_t)l_b >> 64;
}
