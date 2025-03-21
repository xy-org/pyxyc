#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct multipleMacros_module1_Struct multipleMacros_module1_Struct;

struct multipleMacros_module1_Struct {
    int32_t m_a;
    float m_b;
};

bool multipleMacros_test(void) {
    multipleMacros_module1_Struct l_my = {0};
    return l_my.m_a < l_my.m_a;
}
