#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct typeInferenceBasic_Pair typeInferenceBasic_Pair;

struct typeInferenceBasic_Pair {
    int32_t m_a;
    int32_t m_b;
};

void typeInferenceBasic_func(void) {
    const int32_t a = 0;
    const int32_t b = 0x10;
    const float c = 5.5f;
    const float d = 3.14f;
    const float e = .333f;
    const double w = 2.1718;
    const double x = 0;
    const double y = .0;
    const uint64_t l = 1;
    const int16_t s = 10;
    const size_t z = 1024;
    const bool t = true;
    const bool f = false;
    const typeInferenceBasic_Pair p = {a, b};
}

void typeInferenceBasic_implicitVoid(void) {
    typeInferenceBasic_func();
}
