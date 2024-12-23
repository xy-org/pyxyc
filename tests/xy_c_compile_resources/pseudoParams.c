#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t pseudoParams_func1__int__int(int32_t x) {
    return x;
}

int32_t pseudoParams_func1__int__bool(int32_t x, bool y) {
    int32_t tmp0 = 0;
    if (y) {
        tmp0 = x;
    } else {
        tmp0 = x + 2;
    }
    return tmp0;
}

int32_t pseudoParams_func2__int__int(int32_t x) {
    return x * 2;
}

int32_t pseudoParams_func2__int__double(int32_t x, double y) {
    int32_t tmp1 = 0;
    if (y > 0) {
        tmp1 = x;
    } else {
        tmp1 = x * 2;
    }
    return tmp1;
}

void pseudoParams_test(void) {
    pseudoParams_func1__int__int(5);
    pseudoParams_func1__int__bool(5, true);
    pseudoParams_func2__int__int(5);
    pseudoParams_func2__int__int(5);
    pseudoParams_func2__int__double(5, 5.0);
}
