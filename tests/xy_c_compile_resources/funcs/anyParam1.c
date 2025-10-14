#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct anyParam1_Struct anyParam1_Struct;

struct anyParam1_Struct {
    int32_t m_a;
    int32_t m_b;
};

void anyParam1_fun(int32_t p_b) {
}

void anyParam1_test(void) {
    const anyParam1_Struct l_s = {0};
    anyParam1_fun(10);
}
