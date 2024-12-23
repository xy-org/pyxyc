#include <stdint.h>
#include <stddef.h>

typedef struct stringCtor_Str stringCtor_Str;

struct stringCtor_Str {
    void* addr;
    size_t size;
};


stringCtor_Str stringCtor_string(void *addr, size_t size) {
    return (stringCtor_Str){addr, size};
}

void stringCtor_createStrings(void) {
    stringCtor_Str str1 = stringCtor_string("abc", 3);
    stringCtor_Str str2 = stringCtor_string("def", 3);
}


size_t stringCtor_strLen(stringCtor_Str str) {
    return str.size;
}
