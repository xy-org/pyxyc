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

stringInterpolation_Str stringInterpolation_str(void* addr, size_t size) {
    return (stringInterpolation_Str){addr, size};
}

void stringInterpolation_append__StrBuilder__Str(stringInterpolation_StrBuilder* builder, stringInterpolation_Str str) {
}

void stringInterpolation_append__StrBuilder__Float__Int(stringInterpolation_StrBuilder* builder, float f, int32_t precision) {
}

void stringInterpolation_append__StrBuilder__Ptr__Size(stringInterpolation_StrBuilder* builder, void* addr, size_t size) {
}

stringInterpolation_Str stringInterpolation_to(stringInterpolation_StrBuilder* builder) {
    const stringInterpolation_Str res = (stringInterpolation_Str){builder->m_addr, builder->m_size};
    return res;
}

stringInterpolation_StrBuilder stringInterpolation_fstr(void* addr, size_t size) {
    return (stringInterpolation_StrBuilder){0};
}

void stringInterpolation_createStrings(void) {
    const float pi = 3.1415f;
    stringInterpolation_StrBuilder tmp_fstr0 = stringInterpolation_fstr("string", 6);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr0, "string", 6);
    const stringInterpolation_Str str1 = stringInterpolation_to(&tmp_fstr0);
    stringInterpolation_StrBuilder tmp_fstr1 = stringInterpolation_fstr("str1={str1}", 11);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr1, "str1=", 5);
    stringInterpolation_append__StrBuilder__Str(&tmp_fstr1, str1);
    const stringInterpolation_Str str2 = stringInterpolation_to(&tmp_fstr1);
    stringInterpolation_StrBuilder tmp_fstr2 = stringInterpolation_fstr("{=str1}", 7);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr2, "str1=", 5);
    stringInterpolation_append__StrBuilder__Str(&tmp_fstr2, str1);
    const stringInterpolation_Str str3 = stringInterpolation_to(&tmp_fstr2);
    stringInterpolation_StrBuilder tmp_fstr3 = stringInterpolation_fstr("{pi}", 4);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr3, pi, 6);
    const stringInterpolation_Str str4 = stringInterpolation_to(&tmp_fstr3);
    stringInterpolation_StrBuilder tmp_fstr4 = stringInterpolation_fstr("{pi * 2}", 8);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr4, pi * 2, 6);
    const stringInterpolation_Str str5 = stringInterpolation_to(&tmp_fstr4);
    stringInterpolation_StrBuilder tmp_fstr5 = stringInterpolation_fstr("{pi, 2}", 7);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr5, pi, 2);
    const stringInterpolation_Str str6 = stringInterpolation_to(&tmp_fstr5);
    stringInterpolation_StrBuilder tmp_fstr6 = stringInterpolation_fstr("{pi, precision=2}", 17);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr6, pi, 2);
    const stringInterpolation_Str str7 = stringInterpolation_to(&tmp_fstr6);
    stringInterpolation_StrBuilder tmp_fstr7 = stringInterpolation_fstr("{=pi, precision=2}", 18);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr7, "pi=", 3);
    stringInterpolation_append__StrBuilder__Float__Int(&tmp_fstr7, pi, 2);
    const stringInterpolation_Str str8 = stringInterpolation_to(&tmp_fstr7);
    stringInterpolation_StrBuilder tmp_fstr8 = stringInterpolation_fstr("Test{f};\n", 9);
    stringInterpolation_append__StrBuilder__Ptr__Size(&tmp_fstr8, "Test{f};\n", 9);
    const stringInterpolation_Str str9 = stringInterpolation_to(&tmp_fstr8);
}
