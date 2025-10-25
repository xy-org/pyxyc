#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct stringInterpolation_Str stringInterpolation_Str;
typedef struct stringInterpolation_StrBuilder stringInterpolation_StrBuilder;

struct stringInterpolation_Str {
    void* m_addr;
    uint64_t m_size;
};
struct stringInterpolation_StrBuilder {
    void* m_addr;
    uint64_t m_size;
    uint64_t m_cap;
};

stringInterpolation_Str stringInterpolation_str(void* p_addr, uint64_t p_size) {
    return (stringInterpolation_Str){p_addr, p_size};
}

void stringInterpolation_append__StrBuilder__Str(stringInterpolation_StrBuilder* p_builder, stringInterpolation_Str p_str) {
}

void stringInterpolation_append__StrBuilder__Float__Int(stringInterpolation_StrBuilder* p_builder, float p_f, int32_t p_precision) {
}

void stringInterpolation_append__StrBuilder__Ptr__Ulong(stringInterpolation_StrBuilder* p_builder, void* p_addr, uint64_t p_size) {
}

stringInterpolation_Str stringInterpolation_to(stringInterpolation_StrBuilder* p_builder) {
    const stringInterpolation_Str l_res = {p_builder->m_addr, p_builder->m_size};
    return l_res;
}

stringInterpolation_StrBuilder stringInterpolation_fstr(void* p_addr, uint64_t p_size) {
    return (stringInterpolation_StrBuilder){0};
}

void stringInterpolation_createStrings(void) {
    const float l_pi = 3.1415f;
    stringInterpolation_StrBuilder tmp_0_fstr = stringInterpolation_fstr((int8_t*)"string", 6);
    stringInterpolation_append__StrBuilder__Ptr__Ulong(&tmp_0_fstr, (int8_t*)"string", 6);
    const stringInterpolation_Str l_str1 = stringInterpolation_to(&tmp_0_fstr);
    stringInterpolation_StrBuilder tmp_1_fstr = stringInterpolation_fstr((int8_t*)"str1={str1}", 11);
    stringInterpolation_append__StrBuilder__Ptr__Ulong(&tmp_1_fstr, (int8_t*)"str1=", 5);
    stringInterpolation_append__StrBuilder__Str(&tmp_1_fstr, l_str1);
    const stringInterpolation_Str l_str2 = stringInterpolation_to(&tmp_1_fstr);
    stringInterpolation_StrBuilder tmp_2_fstr = stringInterpolation_fstr((int8_t*)"{=str1}", 7);
    stringInterpolation_append__StrBuilder__Ptr__Ulong(&tmp_2_fstr, (int8_t*)"str1=", 5);
    stringInterpolation_append__StrBuilder__Str(&tmp_2_fstr, l_str1);
    const stringInterpolation_Str l_str3 = stringInterpolation_to(&tmp_2_fstr);
    stringInterpolation_StrBuilder tmp_3_fstr = stringInterpolation_fstr((int8_t*)"{pi}", 4);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_3_fstr, l_pi, 6);
    const stringInterpolation_Str l_str4 = stringInterpolation_to(&tmp_3_fstr);
    stringInterpolation_StrBuilder tmp_4_fstr = stringInterpolation_fstr((int8_t*)"{pi * 2}", 8);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_4_fstr, l_pi * 2, 6);
    const stringInterpolation_Str l_str5 = stringInterpolation_to(&tmp_4_fstr);
    stringInterpolation_StrBuilder tmp_5_fstr = stringInterpolation_fstr((int8_t*)"{pi, 2}", 7);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_5_fstr, l_pi, 2);
    const stringInterpolation_Str l_str6 = stringInterpolation_to(&tmp_5_fstr);
    stringInterpolation_StrBuilder tmp_6_fstr = stringInterpolation_fstr((int8_t*)"{pi, precision=2}", 17);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_6_fstr, l_pi, 2);
    const stringInterpolation_Str l_str7 = stringInterpolation_to(&tmp_6_fstr);
    stringInterpolation_StrBuilder tmp_7_fstr = stringInterpolation_fstr((int8_t*)"{=pi, precision=2}", 18);
    stringInterpolation_append__StrBuilder__Ptr__Ulong(&tmp_7_fstr, (int8_t*)"pi=", 3);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_7_fstr, l_pi, 2);
    const stringInterpolation_Str l_str8 = stringInterpolation_to(&tmp_7_fstr);
    stringInterpolation_StrBuilder tmp_8_fstr = stringInterpolation_fstr((int8_t*)"Test{f};\n", 9);
    stringInterpolation_append__StrBuilder__Ptr__Ulong(&tmp_8_fstr, (int8_t*)"Test{f};\n", 9);
    const stringInterpolation_Str l_str9 = stringInterpolation_to(&tmp_8_fstr);
}
