#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void toBits_test__Byte(int8_t p_a) {
    const uint8_t l_bits = p_a;
}

void toBits_test__Ubyte(uint8_t p_a) {
    const uint8_t l_bits = p_a;
}

void toBits_test__Short(int16_t p_a) {
    const uint16_t l_bits = p_a;
}

void toBits_test__Ushort(uint16_t p_a) {
    const uint16_t l_bits = p_a;
}

void toBits_test__Int(int32_t p_a) {
    const uint32_t l_bits = p_a;
}

void toBits_test__Uint(uint32_t p_a) {
    const uint32_t l_bits = p_a;
}

void toBits_test__Long(int64_t p_a) {
    const uint64_t l_bits = p_a;
}

void toBits_test__Ulong(uint64_t p_a) {
    const uint64_t l_bits = p_a;
}

void toBits_test__Float(float p_a) {
    const uint32_t l_bits = *(uint32_t*)&p_a;
}

void toBits_test__Double(double p_a) {
    const uint64_t l_bits = *(uint64_t*)&p_a;
}
