#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void package1_module1_work1(void);
void package1_module1_work2(void);

void package1_module1_test(void) {
    package1_module1_work1();
    package1_module1_work2();
}

void package1_module1_work1(void) {
}

void package1_module1_work2(void) {
}

void package1_test(void) {
    package1_module1_work1();
}
