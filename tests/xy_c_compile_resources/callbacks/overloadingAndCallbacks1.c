#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef int32_t (*xy_fp__Int__Int)(int32_t) ;

void overloadingAndCallbacks1_f__1(int32_t p_a) {
}

void overloadingAndCallbacks1_f__2(xy_fp__Int__Int p_cb) {
}

void overloadingAndCallbacks1_test(int32_t p_a, xy_fp__Int__Int p_cb) {
    overloadingAndCallbacks1_f__1(10);
    overloadingAndCallbacks1_f__2(p_cb);
}
