#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t funcOverloadingSimple_func__with__int(int32_t a) {
    return 0;
}

double funcOverloadingSimple_func__with__double(double b) {
    return 1.0;
}

int32_t funcOverloadingSimple_main(void) {
    const int32_t a = funcOverloadingSimple_func__with__int(0);
    const double b = funcOverloadingSimple_func__with__double(0.0);
    return 0;
}
