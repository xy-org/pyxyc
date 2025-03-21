#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct typeInferenceBasic_Pair typeInferenceBasic_Pair;

struct typeInferenceBasic_Pair {
    int32_t m_a;
    int32_t m_b;
};

void typeInferenceBasic_func(void) {
    const int32_t l_a = 0;
    const int32_t l_b = 0x10;
    const float l_c = 5.5f;
    const float l_d = 3.14f;
    const float l_e = .333f;
    const double l_w = 2.1718;
    const double l_x = 0;
    const double l_y = .0;
    const uint64_t l_l = 1;
    const int16_t l_s = 10;
    const size_t l_z = 1024;
    const bool l_t = true;
    const bool l_f = false;
    const typeInferenceBasic_Pair l_p = {l_a, l_b};
}

void typeInferenceBasic_implicitVoid(void) {
    typeInferenceBasic_func();
}
