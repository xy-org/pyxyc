#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

double inlinecBlock_test(int32_t p_a, double p_b) {
    double l_c = 0;
    printf("a=%d b=%f\n", p_a, p_b);
    l_c = p_b + p_a;;
    return l_c;
}
