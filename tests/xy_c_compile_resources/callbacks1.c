#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct callbacks1_Callback callbacks1_Callback;
typedef int32_t (*xy_fp__Int__Int)(int32_t) ;
typedef int32_t (*xy_fp__Int__Double__Int)(int32_t, double) ;

int32_t callbacks1_abs(int32_t a);
int32_t callbacks1_cb(int32_t a);
int32_t callbacks1_funnyFun(int32_t a, double b);

struct callbacks1_Callback {
    char __empty_structs_are_not_allowed_in_c__;
};

int32_t callbacks1_test(void) {
    const xy_fp__Int__Int cb1 = callbacks1_abs;
    const xy_fp__Int__Int cb2 = callbacks1_cb;
    xy_fp__Int__Double__Int cb3;
    cb3 = callbacks1_funnyFun;
    const xy_fp__Int__Double__Int cb4 = cb3;
    return cb1(cb2(cb3(-5, 5.6)));
}

int32_t callbacks1_abs(int32_t a) {
    int32_t tmp1 = 0;
    if (a < 0) {
        tmp1 = -a;
    } else {
        tmp1 = a;
    }
    return tmp1;
}

int32_t callbacks1_cb(int32_t a) {
    return a;
}

int32_t callbacks1_funnyFun(int32_t a, double b) {
    int32_t tmp0 = 0;
    if (b < 2 * a) {
        tmp0 = a;
    } else {
        tmp0 = -a;
    }
    return tmp0;
}
