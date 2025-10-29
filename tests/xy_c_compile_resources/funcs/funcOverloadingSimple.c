#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t funcOverloadingSimple_fun__Int(int32_t p_a) {
    return 0;
}

double funcOverloadingSimple_fun__Double(double p_b) {
    return 1.0;
}

int32_t funcOverloadingSimple_main(void) {
    const int32_t l_a = funcOverloadingSimple_fun__Int(0);
    const double l_b = funcOverloadingSimple_fun__Double(0.0);
    return 0;
}
