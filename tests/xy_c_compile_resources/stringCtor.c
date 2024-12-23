#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct stringCtor_Str stringCtor_Str;
typedef struct stringCtor_Utf8 stringCtor_Utf8;
typedef struct stringCtor_Ascii stringCtor_Ascii;

struct stringCtor_Str {
    void* addr;
    size_t size;
};
struct stringCtor_Utf8 {
};
struct stringCtor_Ascii {
};

stringCtor_Str stringCtor_str(void* addr, size_t size) {
    return (stringCtor_Str){addr, size};
}

void stringCtor_createStrings(void) {
    stringCtor_Str str = stringCtor_str("", 0);
    stringCtor_Str str1 = stringCtor_str("abc", 3);
    stringCtor_Str str2 = stringCtor_str("def", 3);
}

size_t stringCtor_strLen(stringCtor_Str str) {
    return str.size;
}
