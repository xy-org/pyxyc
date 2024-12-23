#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t pseudoParams_func1__with__int__int(int32_t x) {
    return x;
}

int32_t pseudoParams_func1__with__int__bool(int32_t x, bool y) {
    int32_t __tmp0 = 0;
    if (y) {
        __tmp0 = x;
    } else {
        __tmp0 = x + 2;
    }
    return __tmp0;
}

int32_t pseudoParams_func2__with__int__int(int32_t x) {
    return x * 2;
}

int32_t pseudoParams_func2__with__int__double(int32_t x, double y) {
    int32_t __tmp0 = 0;
    if (y > 0) {
        __tmp0 = x;
    } else {
        __tmp0 = x * 2;
    }
    return __tmp0;
}

void pseudoParams_test(void) {
    pseudoParams_func1__with__int__int(5);
    pseudoParams_func1__with__int__bool(5, true);
    pseudoParams_func2__with__int__int(5);
    pseudoParams_func2__with__int__int(5);
    pseudoParams_func2__with__int__double(5, 5.0);
}
