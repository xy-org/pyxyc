#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct stringInterpolation_Str stringInterpolation_Str;
typedef struct stringInterpolation_StrBuilder stringInterpolation_StrBuilder;

struct stringInterpolation_Str {
    void* xy_addr;
    size_t xy_size;
};
struct stringInterpolation_StrBuilder {
    void* xy_addr;
    size_t xy_size;
    size_t xy_cap;
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
    const stringInterpolation_Str res = (stringInterpolation_Str){builder->xy_addr, builder->xy_size};
    return res;
}

stringInterpolation_StrBuilder stringInterpolation_fstr(void* addr, size_t size) {
    return (stringInterpolation_StrBuilder){};
}

void stringInterpolation_createStrings(void) {
    const float pi = 3.1415f;
    stringInterpolation_StrBuilder __tmp_str0 = stringInterpolation_fstr("string", 6);
    stringInterpolation_append__with__StrBuilder__Ptr__Size(&__tmp_str0, "string", 6);
    const stringInterpolation_Str str1 = stringInterpolation_to(&__tmp_str0);
    stringInterpolation_StrBuilder __tmp_str1 = stringInterpolation_fstr("str1={str1}", 11);
    stringInterpolation_append__with__StrBuilder__Ptr__Size(&__tmp_str1, "str1=", 5);
    stringInterpolation_append__with__StrBuilder__Str(&__tmp_str1, str1);
    const stringInterpolation_Str str2 = stringInterpolation_to(&__tmp_str1);
}
