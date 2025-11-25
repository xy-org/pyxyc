#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void relativeImports_module1_func1(void) {
}

void relativeImports_module2_func2(void) {
    relativeImports_module1_func1();
}

void relativeImports_test(void) {
    relativeImports_module2_func2();
}
