#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct typeValueDuality1_A typeValueDuality1_A;
typedef struct typeValueDuality1_B typeValueDuality1_B;

struct typeValueDuality1_A {
    int32_t m_val;
};
struct typeValueDuality1_B {
    int64_t m_val;
};

void typeValueDuality1_doSomething(void) {
}

void typeValueDuality1_test(void) {
    const typeValueDuality1_A l_a = {0};
    const typeValueDuality1_B l_b = {0};
    const int32_t l_n = 10;
    if (l_n == 0) {
        typeValueDuality1_doSomething();
    }
}
