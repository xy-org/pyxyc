#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

uint8_t bitShifts_test__Bits8__Int(uint8_t p_bits, int32_t p_shift) {
    const uint8_t l_a = (uint8_t)(p_bits << (p_shift & 0x7));
    const uint8_t l_b = (uint8_t)(p_bits >> (p_shift & 0x7));
    const uint8_t l_c = (uint8_t)((int8_t)p_bits >> (p_shift & 0x7));
    return l_a | l_b | l_c;
}

uint16_t bitShifts_test__Bits16__Int(uint16_t p_bits, int32_t p_shift) {
    const uint16_t l_a = (uint16_t)(p_bits << (p_shift & 0xf));
    const uint16_t l_b = (uint16_t)(p_bits >> (p_shift & 0xf));
    const uint16_t l_c = (uint16_t)((int16_t)p_bits >> (p_shift & 0xf));
    return l_a | l_b | l_c;
}

uint32_t bitShifts_test__Bits32__Int(uint32_t p_bits, int32_t p_shift) {
    const uint32_t l_a = p_bits << (p_shift & 0x1f);
    const uint32_t l_b = p_bits >> (p_shift & 0x1f);
    const uint32_t l_c = (uint32_t)((int32_t)p_bits >> (p_shift & 0x1f));
    return l_a | l_b | l_c;
}

uint64_t bitShifts_test__Bits64__Int(uint64_t p_bits, int32_t p_shift) {
    const uint64_t l_a = p_bits << (p_shift & 0x3f);
    const uint64_t l_b = p_bits >> (p_shift & 0x3f);
    const uint64_t l_c = (uint64_t)((int64_t)p_bits >> (p_shift & 0x3f));
    return l_a | l_b | l_c;
}
