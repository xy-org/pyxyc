#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

uint64_t bitFloats_fpToBits(double p_double, float p_float) {
    const uint64_t l_a = *(uint64_t*)&p_double;
    const uint32_t l_b = *(uint32_t*)&p_float;
    const uint64_t l_c = (union { double _from; uint64_t _as; }){2.0 * p_double}._as;
    return l_a | ((uint64_t)l_b & l_c);
}

double bitFloats_bitsToFp(uint64_t p_b64, uint32_t p_b32) {
    const double l_a = *(double*)&p_b64;
    const float l_b = *(float*)&p_b32;
    const float l_c = (union { uint32_t _from; float _as; }){~p_b32}._as;
    const double l_d = (union { uint64_t _from; double _as; }){~p_b64}._as;
    return l_a + (double)l_b * (double)l_c * l_d;
}
