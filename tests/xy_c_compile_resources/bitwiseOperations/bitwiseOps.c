#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct bitwiseOps_Bits bitwiseOps_Bits;

struct bitwiseOps_Bits {
    char __empty_structs_are_not_allowed_in_c__;
};

bool bitwiseOps_get__Bits64__Int(uint64_t p_b, int32_t p_i) {
    return (int64_t)(p_b & (uint64_t)1 << p_i) != 0;
}

int32_t bitwiseOps_set__Bits64__Int__Bool(uint64_t* p_b, int32_t p_i, bool p_val) {
    *p_b = *p_b | (uint64_t)p_val << p_i;
    return p_i;
}

uint64_t bitwiseOps_testBitGetSet(int32_t p_i) {
    uint64_t l_b = 0;
    bitwiseOps_set__Bits64__Int__Bool(&l_b, 0, true);
    bool tmp_arg0 = bitwiseOps_get__Bits64__Int(l_b, p_i);
    bitwiseOps_set__Bits64__Int__Bool(&l_b, 1, tmp_arg0);
    bool tmp_arg1 = bitwiseOps_get__Bits64__Int(l_b, 0);
    bool tmp_arg3 = tmp_arg1 || bitwiseOps_get__Bits64__Int(l_b, 12);
    bitwiseOps_set__Bits64__Int__Bool(&l_b, 10, tmp_arg3);
    return l_b;
}

bitwiseOps_Bits bitwiseOps_bits(int64_t p_a) {
    return (bitwiseOps_Bits){0};
}

uint64_t bitwiseOps_get__Long__Bits(int64_t p_a) {
    return (uint64_t)p_a;
}

void bitwiseOps_set__Long__Bits__Int__Bool(int64_t* p_num, int32_t p_i, bool p_val) {
    uint64_t l_bits = bitwiseOps_get__Long__Bits(*p_num);
    bitwiseOps_set__Bits64__Int__Bool(&l_bits, p_i, p_val);
    *p_num = (int64_t)l_bits;
}

void bitwiseOps_testMixing(void) {
    int64_t l_a = 766624694ll;
    int64_t l_b = 38098ll;
    bitwiseOps_Bits tmp_arg0 = bitwiseOps_bits(l_a);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_a, 60, true);
    bitwiseOps_Bits tmp_arg1 = bitwiseOps_bits(l_b);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_b, 1, true);
    bitwiseOps_Bits tmp_arg2 = bitwiseOps_bits(l_b);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_b, 2, true);
    uint64_t tmp_arg3 = bitwiseOps_get__Long__Bits(l_b);
    bitwiseOps_Bits tmp_arg4 = bitwiseOps_bits(l_a);
    bool tmp_arg5 = bitwiseOps_get__Bits64__Int(tmp_arg3, 10);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_a, 10, tmp_arg5);
    uint64_t tmp_arg6 = bitwiseOps_get__Long__Bits(l_a);
    bool tmp_arg7 = bitwiseOps_get__Bits64__Int(tmp_arg6, 11);
    bitwiseOps_Bits tmp_arg8 = bitwiseOps_bits(l_a);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_a, 11, !tmp_arg7);
    uint64_t tmp_arg9 = bitwiseOps_get__Long__Bits(l_a);
    const uint64_t l_c = tmp_arg9 | bitwiseOps_get__Long__Bits(l_b);
    uint64_t tmp_arg10 = bitwiseOps_get__Long__Bits(l_a);
    uint64_t tmp_arg11 = tmp_arg10 & bitwiseOps_get__Long__Bits(l_b);
    const int64_t l_d = (int64_t)tmp_arg11;
    uint64_t tmp_arg12 = bitwiseOps_get__Long__Bits(l_a);
    uint64_t tmp_arg13 = tmp_arg12 ^ bitwiseOps_get__Long__Bits(l_b);
    const int64_t l_e = (int64_t)tmp_arg13;
    uint64_t tmp_arg14 = bitwiseOps_get__Long__Bits(l_a);
    uint64_t tmp_arg15 = tmp_arg14 ^ bitwiseOps_get__Long__Bits(l_b);
    const int64_t l_f = (int64_t)tmp_arg15;
    const int64_t l_g = (int64_t)(bitwiseOps_get__Long__Bits(l_d) >> 5);
}
