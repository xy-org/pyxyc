#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct stringCtor_Utf8 stringCtor_Utf8;
typedef struct stringCtor_Str stringCtor_Str;
typedef struct stringCtor_Ascii stringCtor_Ascii;

struct stringCtor_Utf8 {
    char __empty_structs_are_not_allowed_in_c__;
};
struct stringCtor_Str {
    void* m_addr;
    size_t m_size;
};
struct stringCtor_Ascii {
    char __empty_structs_are_not_allowed_in_c__;
};

stringCtor_Str stringCtor_str(void* p_addr, size_t p_size) {
    return (stringCtor_Str){p_addr, p_size};
}

void stringCtor_createStrings(void) {
    const stringCtor_Str l_str = stringCtor_str("", 0);
    const stringCtor_Str l_str1 = stringCtor_str("abc", 3);
    const stringCtor_Str l_str2 = stringCtor_str("def", 3);
}

size_t stringCtor_strLen(stringCtor_Str p_str) {
    return p_str.m_size;
}
