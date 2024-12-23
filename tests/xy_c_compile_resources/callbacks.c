#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct callbacks_Callback callbacks_Callback;
typedef int32_t (*xy_fp__int__int)(int32_t) ;
typedef int32_t (*xy_fp__int__double__int)(int32_t, double) ;

int32_t callbacks_abs(int32_t a);
int32_t callbacks_cb(int32_t a);
int32_t callbacks_funnyFun(int32_t a, double b);

struct callbacks_Callback {
    char __empty_structs_are_not_allowed_in_c__;
};

int32_t callbacks_test(void) {
    const xy_fp__int__int cb1 = callbacks_abs;
    const xy_fp__int__int cb2 = callbacks_cb;
    xy_fp__int__double__int cb3;
    cb3 = callbacks_funnyFun;
    const xy_fp__int__double__int cb4 = cb3;
}

int32_t callbacks_abs(int32_t a) {
    int32_t tmp1 = 0;
    if (a < 0) {
        tmp1 = -a;
    } else {
        tmp1 = a;
    }
    return tmp1;
}

int32_t callbacks_cb(int32_t a) {
    return a;
}

int32_t callbacks_funnyFun(int32_t a, double b) {
    int32_t tmp0 = 0;
    if (b < 2 * a) {
        tmp0 = a;
    } else {
        tmp0 = -a;
    }
    return tmp0;
}
