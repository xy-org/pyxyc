#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct callbacks1_Callback callbacks1_Callback;
typedef int32_t (*xy_fp__Int__Int)(int32_t) ;
typedef int32_t (*xy_fp__Int__Double__Int)(int32_t, double) ;

int32_t callbacks1_abs(int32_t p_a);
int32_t callbacks1_cb(int32_t p_a);
int32_t callbacks1_funnyFun(int32_t p_a, double p_b);

struct callbacks1_Callback {
    char __empty_structs_are_not_allowed_in_c__;
};

int32_t callbacks1_test(void) {
    const xy_fp__Int__Int l_cb1 = callbacks1_abs;
    const xy_fp__Int__Int l_cb2 = callbacks1_cb;
    xy_fp__Int__Double__Int l_cb3;
    l_cb3 = callbacks1_funnyFun;
    const xy_fp__Int__Double__Int l_cb4 = l_cb3;
    return l_cb1(l_cb2(l_cb3(-5, 5.6)));
}

int32_t callbacks1_abs(int32_t p_a) {
    int32_t tmp1 = 0;
    if (p_a < 0) {
        tmp1 = -p_a;
    } else {
        tmp1 = p_a;
    }
    return tmp1;
}

int32_t callbacks1_cb(int32_t p_a) {
    return p_a;
}

int32_t callbacks1_funnyFun(int32_t p_a, double p_b) {
    int32_t tmp0 = 0;
    if (p_b < 2 * p_a) {
        tmp0 = p_a;
    } else {
        tmp0 = -p_a;
    }
    return tmp0;
}
