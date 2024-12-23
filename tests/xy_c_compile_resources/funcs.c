#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct funcs_A funcs_A;

struct funcs_A {
    int32_t xy_num;
};

funcs_A funcs_double(funcs_A a) {
    return (funcs_A){a.xy_num * 2};
}

void funcs_doubleInout(funcs_A* a) {
    a->xy_num *= 2;
}

funcs_A funcs_callDoubles(funcs_A* a) {
    *a = funcs_double(*a);
    funcs_doubleInout(a);
    return *a;
}

int32_t funcs_test(void) {
    funcs_A a = (funcs_A){5};
    funcs_double(a);
    funcs_doubleInout(&a);
    return funcs_callDoubles(&a).xy_num;
}
