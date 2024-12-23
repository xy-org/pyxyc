#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t funcRecursive_func2(int32_t b);
int32_t funcRecursive_func4(int32_t a, int32_t b);

int32_t funcRecursive_func1(int32_t a) {
    return funcRecursive_func2(a);
}

int32_t funcRecursive_func2(int32_t b) {
    return funcRecursive_func2(b);
}

int32_t funcRecursive_func3(int32_t c) {
    return funcRecursive_func1(c) + funcRecursive_func2(-c) + c - funcRecursive_func4(c, -c);
}

int32_t funcRecursive_func4(int32_t a, int32_t b) {
    return a + b;
}
