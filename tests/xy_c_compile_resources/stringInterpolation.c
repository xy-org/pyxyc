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

void stringInterpolation_append__with__StrBuilder__Str(stringInterpolation_StrBuilder* builder, stringInterpolation_Str str) {
}

void stringInterpolation_append__with__StrBuilder__float(stringInterpolation_StrBuilder* builder, float f) {
}

void stringInterpolation_append__with__StrBuilder__Ptr__Size(stringInterpolation_StrBuilder* builder, void* addr, size_t size) {
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
    stringInterpolation_append__with__StrBuilder__Ptr__Size(&tmp_fstr0, "string", 6);
    const stringInterpolation_Str str1 = stringInterpolation_to(&tmp_fstr0);
    stringInterpolation_StrBuilder tmp_fstr1 = stringInterpolation_fstr("str1={str1}", 11);
    stringInterpolation_append__with__StrBuilder__Ptr__Size(&tmp_fstr1, "str1=", 5);
    stringInterpolation_append__with__StrBuilder__Str(&tmp_fstr1, str1);
    const stringInterpolation_Str str2 = stringInterpolation_to(&tmp_fstr1);
}