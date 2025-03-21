#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct stringInterpolation_Str stringInterpolation_Str;
typedef struct stringInterpolation_StrBuilder stringInterpolation_StrBuilder;

struct stringInterpolation_Str {
    void* m_addr;
    size_t m_size;
};
struct stringInterpolation_StrBuilder {
    void* m_addr;
    size_t m_size;
    size_t m_cap;
};

stringInterpolation_Str stringInterpolation_str(void* p_addr, size_t p_size) {
    return (stringInterpolation_Str){p_addr, p_size};
}

void stringInterpolation_append__StrBuilder__Str(stringInterpolation_StrBuilder* p_builder, stringInterpolation_Str p_str) {
}

void stringInterpolation_append__StrBuilder__Float__Int(stringInterpolation_StrBuilder* p_builder, float p_f, int32_t p_precision) {
}

void stringInterpolation_append__StrBuilder__Ptr__Size(stringInterpolation_StrBuilder* p_builder, void* p_addr, size_t p_size) {
}

stringInterpolation_Str stringInterpolation_to(stringInterpolation_StrBuilder* p_builder) {
    const stringInterpolation_Str l_res = {p_builder->m_addr, p_builder->m_size};
    return l_res;
}

stringInterpolation_StrBuilder stringInterpolation_fstr(void* p_addr, size_t p_size) {
    return (stringInterpolation_StrBuilder){0};
}

void stringInterpolation_createStrings(void) {
    const float l_pi = 3.1415f;
    stringInterpolation_StrBuilder tmp_fstr0 = stringInterpolation_fstr("string", 6);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr0, "string", 6);
    const stringInterpolation_Str l_str1 = stringInterpolation_to(&tmp_fstr0);
    stringInterpolation_StrBuilder tmp_fstr1 = stringInterpolation_fstr("str1={str1}", 11);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr1, "str1=", 5);
    stringInterpolation_append__StrBuilder__Str(&tmp_fstr1, l_str1);
    const stringInterpolation_Str l_str2 = stringInterpolation_to(&tmp_fstr1);
    stringInterpolation_StrBuilder tmp_fstr2 = stringInterpolation_fstr("{=str1}", 7);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr2, "str1=", 5);
    stringInterpolation_append__StrBuilder__Str(&tmp_fstr2, l_str1);
    const stringInterpolation_Str l_str3 = stringInterpolation_to(&tmp_fstr2);
    stringInterpolation_StrBuilder tmp_fstr3 = stringInterpolation_fstr("{pi}", 4);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr3, l_pi, 6);
    const stringInterpolation_Str l_str4 = stringInterpolation_to(&tmp_fstr3);
    stringInterpolation_StrBuilder tmp_fstr4 = stringInterpolation_fstr("{pi * 2}", 8);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr4, l_pi * 2, 6);
    const stringInterpolation_Str l_str5 = stringInterpolation_to(&tmp_fstr4);
    stringInterpolation_StrBuilder tmp_fstr5 = stringInterpolation_fstr("{pi, 2}", 7);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr5, l_pi, 2);
    const stringInterpolation_Str l_str6 = stringInterpolation_to(&tmp_fstr5);
    stringInterpolation_StrBuilder tmp_fstr6 = stringInterpolation_fstr("{pi, precision=2}", 17);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr6, l_pi, 2);
    const stringInterpolation_Str l_str7 = stringInterpolation_to(&tmp_fstr6);
    stringInterpolation_StrBuilder tmp_fstr7 = stringInterpolation_fstr("{=pi, precision=2}", 18);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr7, "pi=", 3);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr7, l_pi, 2);
    const stringInterpolation_Str l_str8 = stringInterpolation_to(&tmp_fstr7);
    stringInterpolation_StrBuilder tmp_fstr8 = stringInterpolation_fstr("Test{f};\n", 9);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr8, "Test{f};\n", 9);
    const stringInterpolation_Str l_str9 = stringInterpolation_to(&tmp_fstr8);
}
