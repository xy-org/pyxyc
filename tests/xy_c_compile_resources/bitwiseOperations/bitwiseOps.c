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
    *p_b |= (uint64_t)p_val << p_i;
    return p_i;
}

uint64_t bitwiseOps_testBitGetSet(int32_t p_i) {
    uint64_t l_b = 0;
    int32_t tmp_0_arg = bitwiseOps_set__Bits64__Int__Bool(&l_b, 0, true);
    bool tmp_1_arg = bitwiseOps_get__Bits64__Int(l_b, p_i);
    int32_t tmp_2_arg = bitwiseOps_set__Bits64__Int__Bool(&l_b, 1, tmp_1_arg);
    bool tmp_3_arg = bitwiseOps_get__Bits64__Int(l_b, 0);
    bool tmp_5_arg = tmp_3_arg || bitwiseOps_get__Bits64__Int(l_b, 12);
    int32_t tmp_6_arg = bitwiseOps_set__Bits64__Int__Bool(&l_b, 10, tmp_5_arg);
    return l_b;
}

bitwiseOps_Bits bitwiseOps_bits(int64_t p_a) {
    return (bitwiseOps_Bits){0};
}

uint64_t bitwiseOps_get__Long__Bits(int64_t p_a) {
    return (uint64_t)p_a;
}

void bitwiseOps_set__Long__Bits__Int__Bool(int64_t* p_num, int32_t p_i, bool p_val) {
    bitwiseOps_Bits tmp_0_arg = bitwiseOps_bits(*p_num);
    uint64_t l_bits = bitwiseOps_get__Long__Bits(*p_num);
    int32_t tmp_1_arg = bitwiseOps_set__Bits64__Int__Bool(&l_bits, p_i, p_val);
    *p_num = (int64_t)l_bits;
}

void bitwiseOps_testMixing(void) {
    int64_t l_a = 766624694ll;
    int64_t l_b = 38098ll;
    bitwiseOps_Bits tmp_0_arg = bitwiseOps_bits(l_a);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_a, 60, true);
    bitwiseOps_Bits tmp_1_arg = bitwiseOps_bits(l_b);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_b, 1, true);
    bitwiseOps_Bits tmp_2_arg = bitwiseOps_bits(l_b);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_b, 2, true);
    bitwiseOps_Bits tmp_3_arg = bitwiseOps_bits(l_a);
    bitwiseOps_Bits tmp_4_arg = bitwiseOps_bits(l_b);
    uint64_t tmp_5_arg = bitwiseOps_get__Long__Bits(l_b);
    bool tmp_6_arg = bitwiseOps_get__Bits64__Int(tmp_5_arg, 10);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_a, 10, tmp_6_arg);
    bitwiseOps_Bits tmp_7_arg = bitwiseOps_bits(l_a);
    bitwiseOps_Bits tmp_8_arg = bitwiseOps_bits(l_a);
    uint64_t tmp_9_arg = bitwiseOps_get__Long__Bits(l_a);
    bool tmp_10_arg = bitwiseOps_get__Bits64__Int(tmp_9_arg, 11);
    bitwiseOps_set__Long__Bits__Int__Bool(&l_a, 11, !tmp_10_arg);
    bitwiseOps_Bits tmp_11_arg = bitwiseOps_bits(l_a);
    uint64_t tmp_12_arg = bitwiseOps_get__Long__Bits(l_a);
    bitwiseOps_Bits tmp_13_arg = bitwiseOps_bits(l_b);
    uint64_t tmp_14_arg = bitwiseOps_get__Long__Bits(l_b);
    const uint64_t l_c = tmp_12_arg | tmp_14_arg;
    bitwiseOps_Bits tmp_15_arg = bitwiseOps_bits(l_a);
    uint64_t tmp_16_arg = bitwiseOps_get__Long__Bits(l_a);
    bitwiseOps_Bits tmp_17_arg = bitwiseOps_bits(l_b);
    uint64_t tmp_18_arg = bitwiseOps_get__Long__Bits(l_b);
    const int64_t l_d = (int64_t)(tmp_16_arg & tmp_18_arg);
    bitwiseOps_Bits tmp_19_arg = bitwiseOps_bits(l_a);
    uint64_t tmp_20_arg = bitwiseOps_get__Long__Bits(l_a);
    bitwiseOps_Bits tmp_21_arg = bitwiseOps_bits(l_b);
    uint64_t tmp_22_arg = bitwiseOps_get__Long__Bits(l_b);
    const int64_t l_e = (int64_t)(tmp_20_arg != tmp_22_arg);
    bitwiseOps_Bits tmp_23_arg = bitwiseOps_bits(l_a);
    uint64_t tmp_24_arg = bitwiseOps_get__Long__Bits(l_a);
    bitwiseOps_Bits tmp_25_arg = bitwiseOps_bits(l_b);
    uint64_t tmp_26_arg = bitwiseOps_get__Long__Bits(l_b);
    const int64_t l_f = (int64_t)(tmp_24_arg ^ tmp_26_arg);
    bitwiseOps_Bits tmp_27_arg = bitwiseOps_bits(l_d);
    uint64_t tmp_28_arg = bitwiseOps_get__Long__Bits(l_d);
    const int64_t l_g = (int64_t)(tmp_28_arg >> 5);
}
