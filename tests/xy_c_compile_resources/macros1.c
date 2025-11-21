#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct macros1__EMPTY_STRUCT_ macros1_Tag1;
typedef struct macros1_Struct macros1_Struct;
typedef struct macros1__EMPTY_STRUCT_ macros1_Tag2;
typedef struct macros1__EMPTY_STRUCT_ macros1_Tag3;

struct macros1__EMPTY_STRUCT_ {
    char __empty_structs_are_not_allowed_in_c__;
};
struct macros1_Struct {
    int32_t m_field;
};

int32_t macros1_impl__1(macros1_Struct p_s) {
    return 0;
}

float macros1_impl__2(macros1_Struct p_s) {
    return 3.14f;
}

bool macros1_impl__3(macros1_Struct p_s) {
    return true;
}

void macros1_test(void) {
    macros1_Struct l_a = {0};
    macros1_Struct l_b = {0};
    macros1_Struct l_c = {0};
    const int32_t l_x = macros1_impl__1(l_a);
    const float l_y = macros1_impl__2(l_b);
    const int32_t l_z = macros1_impl__1(l_c);
    const bool l_w = macros1_impl__3(l_c);
}
