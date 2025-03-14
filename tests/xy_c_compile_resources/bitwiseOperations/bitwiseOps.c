#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct bitwiseOps_Bits bitwiseOps_Bits;

struct bitwiseOps_Bits {
    char __empty_structs_are_not_allowed_in_c__;
};

bool bitwiseOps_get__Bits64__Int(uint64_t b, int32_t i) {
    return (b & (uint64_t)1 << i) != 0;
}

int32_t bitwiseOps_set__Bits64__Int__Bool(uint64_t* b, int32_t i, bool val) {
    *b = *b | (uint64_t)val << i;
    return i;
}

uint64_t bitwiseOps_testBitGetSet(int32_t i) {
    uint64_t b = 0;
    bitwiseOps_set__Bits64__Int__Bool(&b, 0, true);
    bool tmp_arg0 = bitwiseOps_get__Bits64__Int(b, i);
    bitwiseOps_set__Bits64__Int__Bool(&b, 1, tmp_arg0);
    bool tmp_arg1 = bitwiseOps_get__Bits64__Int(b, 0);
    bool tmp_arg2 = tmp_arg1 || bitwiseOps_get__Bits64__Int(b, 12);
    bitwiseOps_set__Bits64__Int__Bool(&b, 10, tmp_arg2);
    return b;
}

bitwiseOps_Bits bitwiseOps_bits(int64_t a) {
    return (bitwiseOps_Bits){0};
}

uint64_t bitwiseOps_get__Long__Bits(int64_t a) {
    return (uint64_t)a;
}

void bitwiseOps_set__Long__Bits__Int__Bool(int64_t* num, int32_t i, bool val) {
    uint64_t bits = bitwiseOps_get__Long__Bits(*num);
    bitwiseOps_set__Bits64__Int__Bool(&bits, i, val);
    *num = (int64_t)bits;
}

void bitwiseOps_testMixing(void) {
    int64_t a = 766624694ll;
    int64_t b = 38098ll;
    bitwiseOps_Bits tmp_arg0 = bitwiseOps_bits(a);
    bitwiseOps_set__Long__Bits__Int__Bool(&a, 60, true);
    bitwiseOps_Bits tmp_arg1 = bitwiseOps_bits(b);
    bitwiseOps_set__Long__Bits__Int__Bool(&b, 1, true);
    bitwiseOps_Bits tmp_arg2 = bitwiseOps_bits(b);
    bitwiseOps_set__Long__Bits__Int__Bool(&b, 2, true);
    uint64_t tmp_arg3 = bitwiseOps_get__Long__Bits(b);
    bitwiseOps_Bits tmp_arg4 = bitwiseOps_bits(a);
    bitwiseOps_set__Long__Bits__Int__Bool(&a, 10, bitwiseOps_get__Bits64__Int(tmp_arg3, 10));
    uint64_t tmp_arg5 = bitwiseOps_get__Long__Bits(a);
    bitwiseOps_Bits tmp_arg6 = bitwiseOps_bits(a);
    bitwiseOps_set__Long__Bits__Int__Bool(&a, 11, !bitwiseOps_get__Bits64__Int(tmp_arg5, 11));
    uint64_t tmp_arg7 = bitwiseOps_get__Long__Bits(a);
    const uint64_t c = tmp_arg7 | bitwiseOps_get__Long__Bits(b);
    uint64_t tmp_arg8 = bitwiseOps_get__Long__Bits(a);
    const uint64_t d = tmp_arg8 & bitwiseOps_get__Long__Bits(b);
    const uint64_t f = bitwiseOps_get__Long__Bits(a) ^ bitwiseOps_get__Long__Bits(b);
    const uint64_t g = bitwiseOps_get__Long__Bits((int64_t)d) >> 5;
}
