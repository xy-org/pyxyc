#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void toBits_test__1(int8_t p_a) {
    const uint8_t l_bits = p_a;
}

void toBits_test__2(uint8_t p_a) {
    const uint8_t l_bits = p_a;
}

void toBits_test__3(int16_t p_a) {
    const uint16_t l_bits = p_a;
}

void toBits_test__4(uint16_t p_a) {
    const uint16_t l_bits = p_a;
}

void toBits_test__5(int32_t p_a) {
    const uint32_t l_bits = p_a;
}

void toBits_test__6(uint32_t p_a) {
    const uint32_t l_bits = p_a;
}

void toBits_test__7(int64_t p_a) {
    const uint64_t l_bits = p_a;
}

void toBits_test__8(uint64_t p_a) {
    const uint64_t l_bits = p_a;
}

void toBits_test__9(float p_a) {
    const uint32_t l_bits = *(uint32_t*)&p_a;
}

void toBits_test__10(double p_a) {
    const uint64_t l_bits = *(uint64_t*)&p_a;
}
