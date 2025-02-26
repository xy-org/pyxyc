#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t pseudoParams_func1__Int__Int(int32_t x) {
    return x;
}

int32_t pseudoParams_func1__Int__Bool(int32_t x, bool y) {
    int32_t tmp0 = 0;
    if (y) {
        tmp0 = x;
    } else {
        tmp0 = x + 2;
    }
    return tmp0;
}

int32_t pseudoParams_func2__Int__Int(int32_t x) {
    return x * 2;
}

int32_t pseudoParams_func2__Int__Double(int32_t x, double y) {
    int32_t tmp1 = 0;
    if (y > 0) {
        tmp1 = x;
    } else {
        tmp1 = x * 2;
    }
    return tmp1;
}

void pseudoParams_test(void) {
    pseudoParams_func1__Int__Int(5);
    pseudoParams_func1__Int__Bool(5, true);
    pseudoParams_func2__Int__Int(5);
    pseudoParams_func2__Int__Int(5);
    pseudoParams_func2__Int__Double(5, 5.0);
}
