#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

bool bitShiftCmp_testCmp1__Bits8(uint8_t p_bits) {
    return (uint8_t)(p_bits >> 3) == (uint8_t)(p_bits << 5);
}

bool bitShiftCmp_testCmp1__Bits16(uint16_t p_bits) {
    return (uint16_t)(p_bits >> 3) == (uint16_t)(p_bits << 5);
}

bool bitShiftCmp_testCmp1__Bits32(uint32_t p_bits) {
    return p_bits >> 3 == p_bits << 5;
}

bool bitShiftCmp_testCmp1__Bits64(uint64_t p_bits) {
    return p_bits >> 3 == p_bits << 5;
}

bool bitShiftCmp_testCmp2__Bits8(uint8_t p_bits) {
    return (uint8_t)((int8_t)p_bits >> 3) == (uint8_t)(p_bits << 5);
}

bool bitShiftCmp_testCmp2__Bits16(uint16_t p_bits) {
    return (uint16_t)((int16_t)p_bits >> 3) == (uint16_t)(p_bits << 5);
}

bool bitShiftCmp_testCmp2__Bits32(uint32_t p_bits) {
    return (uint32_t)((int32_t)p_bits >> 3) == p_bits << 5;
}

bool bitShiftCmp_testCmp2__Bits64(uint64_t p_bits) {
    return (uint64_t)((int64_t)p_bits >> 3) == p_bits << 5;
}

bool bitShiftCmp_testCmpNot__Bits8__Bits8(uint8_t p_a, uint8_t p_b) {
    return (uint8_t)~p_a == p_b;
}

bool bitShiftCmp_testCmpNot__Bits16__Bits16(uint16_t p_a, uint16_t p_b) {
    return (uint16_t)~p_a == p_b;
}

bool bitShiftCmp_testCmpNot__Bits32__Bits32(uint32_t p_a, uint32_t p_b) {
    return ~p_a == p_b;
}

bool bitShiftCmp_testCmpNot__Bits64__Bits64(uint64_t p_a, uint64_t p_b) {
    return ~p_a == p_b;
}
