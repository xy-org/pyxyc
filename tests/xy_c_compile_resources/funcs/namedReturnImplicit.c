#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void namedReturnImplicit_func(int32_t* p_a);

int32_t namedReturnImplicit_test(int32_t* p_a) {
    int32_t l_num = 0;
    l_num = 2 * *p_a;
    namedReturnImplicit_func(p_a);
    return l_num;
}

void namedReturnImplicit_func(int32_t* p_a) {
    *p_a += 2;
}
