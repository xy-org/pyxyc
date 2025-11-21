#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

bool bitShiftCmp_testCmp1__1(uint8_t p_bits) {
    return (uint8_t)(p_bits >> 3) == (uint8_t)(p_bits << 5);
}

bool bitShiftCmp_testCmp1__2(uint16_t p_bits) {
    return (uint16_t)(p_bits >> 3) == (uint16_t)(p_bits << 5);
}

bool bitShiftCmp_testCmp1__3(uint32_t p_bits) {
    return p_bits >> 3 == p_bits << 5;
}

bool bitShiftCmp_testCmp1__4(uint64_t p_bits) {
    return p_bits >> 3 == p_bits << 5;
}

bool bitShiftCmp_testCmp2__1(uint8_t p_bits) {
    return (uint8_t)((int8_t)p_bits >> 3) == (uint8_t)(p_bits << 5);
}

bool bitShiftCmp_testCmp2__2(uint16_t p_bits) {
    return (uint16_t)((int16_t)p_bits >> 3) == (uint16_t)(p_bits << 5);
}

bool bitShiftCmp_testCmp2__3(uint32_t p_bits) {
    return (uint32_t)((int32_t)p_bits >> 3) == p_bits << 5;
}

bool bitShiftCmp_testCmp2__4(uint64_t p_bits) {
    return (uint64_t)((int64_t)p_bits >> 3) == p_bits << 5;
}

bool bitShiftCmp_testCmpNot__1(uint8_t p_a, uint8_t p_b) {
    return (uint8_t)~p_a == p_b;
}

bool bitShiftCmp_testCmpNot__2(uint16_t p_a, uint16_t p_b) {
    return (uint16_t)~p_a == p_b;
}

bool bitShiftCmp_testCmpNot__3(uint32_t p_a, uint32_t p_b) {
    return ~p_a == p_b;
}

bool bitShiftCmp_testCmpNot__4(uint64_t p_a, uint64_t p_b) {
    return ~p_a == p_b;
}
