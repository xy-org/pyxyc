#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>

float richErrors_mydiv(float p_a, float p_b) {
    return p_a / p_b;
}

float richErrors_test(float p_a, float p_b) {
    if (!(p_b != 0)) {
        fprintf(stderr, "\ntests/xy_c_compile_resources/errors/richErrors.xy:%d ", 2);
        fprintf(stderr, "Guard failed when calling richErrors.mydiv!\n");
        fprintf(stderr, "| %s\n", ">> b != 0");
        fprintf(stderr, "Arguments to Function are:\n");
        fprintf(stderr, "    %s=%f\n", "a", p_a);
        fprintf(stderr, "    %s=%f\n", "b", p_b);
        exit(200);
    }
    if (!(p_a > p_b)) {
        fprintf(stderr, "\ntests/xy_c_compile_resources/errors/richErrors.xy:%d ", 3);
        fprintf(stderr, "Guard failed when calling richErrors.mydiv!\n");
        fprintf(stderr, "| %s\n", ">> a > b");
        fprintf(stderr, "Arguments to Function are:\n");
        fprintf(stderr, "    %s=%f\n", "a", p_a);
        fprintf(stderr, "    %s=%f\n", "b", p_b);
        exit(200);
    }
    return p_a * richErrors_mydiv(p_a, p_b) - p_b;
}
