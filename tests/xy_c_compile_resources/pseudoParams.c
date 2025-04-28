#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t pseudoParams_func1__Int__Int(int32_t p_x) {
    return p_x;
}

int32_t pseudoParams_func1__Int__Bool(int32_t p_x, bool p_y) {
    int32_t tmp_0 = 0;
    if (p_y) {
        tmp_0 = p_x;
    } else {
        tmp_0 = p_x + 2;
    }
    return tmp_0;
}

int32_t pseudoParams_func2__Int__Int(int32_t p_x) {
    return p_x * 2;
}

int32_t pseudoParams_func2__Int__Double(int32_t p_x, double p_y) {
    int32_t tmp_0 = 0;
    if (p_y > 0) {
        tmp_0 = p_x;
    } else {
        tmp_0 = p_x * 2;
    }
    return tmp_0;
}

void pseudoParams_test(void) {
    pseudoParams_func1__Int__Int(5);
    pseudoParams_func1__Int__Bool(5, true);
    pseudoParams_func2__Int__Int(5);
    pseudoParams_func2__Int__Int(5);
    pseudoParams_func2__Int__Double(5, 5.0);
}
