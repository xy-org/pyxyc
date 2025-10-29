#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct typeValueDuality2_A typeValueDuality2_A;
typedef struct typeValueDuality2_B typeValueDuality2_B;

struct typeValueDuality2_A {
    int32_t m_val;
};
struct typeValueDuality2_B {
    int64_t m_val;
};

void typeValueDuality2_dtor__A(typeValueDuality2_A p_a) {
}

void typeValueDuality2_dtor__B(typeValueDuality2_B p_b) {
}

typeValueDuality2_B typeValueDuality2_to(typeValueDuality2_A p_a) {
    return (typeValueDuality2_B){0};
}

void typeValueDuality2_test(void) {
    typeValueDuality2_A l_a = {0};
    typeValueDuality2_B tmp_0_arg = (typeValueDuality2_B){0};
    typeValueDuality2_B l_b = typeValueDuality2_to(l_a);
    typeValueDuality2_dtor__B(l_b);
    typeValueDuality2_dtor__A(l_a);
}
