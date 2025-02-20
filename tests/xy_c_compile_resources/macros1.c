#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct macros1_Struct macros1_Struct;
typedef struct macros1_Tag1 macros1_Tag1;
typedef struct macros1_Tag2 macros1_Tag2;
typedef struct macros1_Tag3 macros1_Tag3;

int32_t macros1_impl__Struct__Tag1(macros1_Struct s);

struct macros1_Struct {
    int32_t m_field;
};
struct macros1_Tag1 {
    char __empty_structs_are_not_allowed_in_c__;
};
struct macros1_Tag2 {
    char __empty_structs_are_not_allowed_in_c__;
};
struct macros1_Tag3 {
    char __empty_structs_are_not_allowed_in_c__;
};

int32_t macros1_impl__Struct__Tag1(macros1_Struct s) {
    return 0;
}

float macros1_impl__Struct__Tag2(macros1_Struct s) {
    return 3.14f;
}

bool macros1_impl__Struct__Tag3(macros1_Struct s) {
    return true;
}

void macros1_test(void) {
    macros1_Struct a = (macros1_Struct){0};
    macros1_Struct b = (macros1_Struct){0};
    macros1_Struct c = (macros1_Struct){0};
    const int32_t x = macros1_impl__Struct__Tag1(a);
    const float y = macros1_impl__Struct__Tag2(b);
    const int32_t z = macros1_impl__Struct__Tag1(c);
    const bool w = macros1_impl__Struct__Tag3(c);
}
