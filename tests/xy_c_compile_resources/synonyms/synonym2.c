#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct synonym2_Str synonym2_Str;
typedef struct synonym2__EMPTY_STRUCT_ synonym2_Managed;
typedef struct synonym2__EMPTY_STRUCT_ synonym2_Static;
typedef struct synonym2_Iter synonym2_Iter;

struct synonym2_Str {
    int8_t* m_addr;
    uint64_t m_size;
};
struct synonym2__EMPTY_STRUCT_ {
    char __empty_structs_are_not_allowed_in_c__;
};
struct synonym2_Iter {
    synonym2_Str m_s;
};

int32_t synonym2_call__2(synonym2_Str p_s) {
    return 1;
}

int32_t synonym2_call__3(synonym2_Str p_s) {
    return 2;
}

int32_t synonym2_test(synonym2_Iter p_iter) {
    return synonym2_call__2(p_iter.m_s);
}
