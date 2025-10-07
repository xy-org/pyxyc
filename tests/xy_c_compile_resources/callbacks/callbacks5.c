#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef void (*xy_fp__Int__void)(int32_t) ;
typedef int32_t (*xy_fp__Int__Int)(int32_t) ;
typedef int32_t (*xy_fp__Int__Int__Int)(int32_t, int32_t) ;
typedef void (*xy_fp__mut__Int__Int__void)(int32_t*, int32_t) ;
typedef int64_t (*xy_fp__mut__Int__mut__Int__Long)(int32_t*, int32_t*) ;

void callbacks5_f1(int32_t p_x) {
}

void callbacks5_f2(int32_t p_x, int32_t p_y) {
}

int32_t callbacks5_f3(int32_t p_x, int32_t p_y) {
    return p_y - p_x;
}

void callbacks5_f4(int32_t* p_x, int32_t p_y) {
    *p_x -= p_y;
}

int64_t callbacks5_f5(int32_t* p_x, int32_t* _res0) {
    (*p_x)++;
    if (*p_x > 20) {
        return 20ll;
    }
    *_res0 = *p_x + 20;
    return 0;
}

void xy_gen__callbacks5__cb0(int32_t p_param0) {
    callbacks5_f2(p_param0, p_param0 + 1);
}

int32_t xy_gen__callbacks5__cb1(int32_t p_param0) {
    return callbacks5_f3(p_param0, p_param0 * 2);
}

void callbacks5_test1(void) {
    const xy_fp__Int__void l_cb1 = callbacks5_f1;
    const xy_fp__Int__Int l_cb2 = xy_gen__callbacks5__cb0;
    l_cb1(5);
    l_cb2(10);
    const xy_fp__Int__Int__Int l_cb3 = callbacks5_f3;
    int32_t l_x = l_cb3(10, 11);
    const xy_fp__Int__Int l_cb4 = xy_gen__callbacks5__cb1;
    const int32_t l_y = l_cb4(20);
    const xy_fp__mut__Int__Int__void l_cb5 = callbacks5_f4;
    l_cb5(&l_x, 20);
    const xy_fp__mut__Int__mut__Int__Long l_cb6 = callbacks5_f5;
    int32_t tmp_0_res = 0;
    const int64_t tmp_1_err = l_cb6(&l_x, &tmp_0_res);
    if ((bool)tmp_1_err) {
        abort();
    }
    const int32_t l_z = tmp_0_res;
}
