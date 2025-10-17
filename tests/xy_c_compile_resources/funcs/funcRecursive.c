#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t funcRecursive_func2(int32_t p_b);
int32_t funcRecursive_func4(int32_t p_a, int32_t p_b);

int32_t funcRecursive_func1(int32_t p_a) {
    return funcRecursive_func2(p_a);
}

int32_t funcRecursive_func2(int32_t p_b) {
    return funcRecursive_func2(p_b);
}

int32_t funcRecursive_func3(int32_t p_c) {
    int32_t tmp_0_arg = funcRecursive_func1(p_c);
    int32_t tmp_1_arg = tmp_0_arg + funcRecursive_func2(-p_c) + p_c;
    return tmp_1_arg - funcRecursive_func4(p_c, -p_c);
}

int32_t funcRecursive_func4(int32_t p_a, int32_t p_b) {
    return p_a + p_b;
}
