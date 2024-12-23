#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct typeInferenceBasic_Pair typeInferenceBasic_Pair;

struct typeInferenceBasic_Pair {
    int32_t a;
    int32_t b;
};

void typeInferenceBasic_func(void) {
    const int32_t a = 0;
    const int32_t b = 0x10;
    const double c = 5.5;
    const float d = 3.14f;
    const float e = .333f;
    const bool t = true;
    const bool f = false;
    const typeInferenceBasic_Pair p = (typeInferenceBasic_Pair){a, b};
}
