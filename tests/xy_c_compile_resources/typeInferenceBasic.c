#include <stdint.h>
#include <stddef.h>

typedef struct typeInferenceBasic_Pair typeInferenceBasic_Pair;

struct typeInferenceBasic_Pair {
    int32_t a;
    int32_t b;
};

void typeInferenceBasic_func(void) {
    int32_t a = 0;
    int32_t b = 0x10;
    double c = 5.5;
    float d = 3.14f;
    float e = .333f;
    typeInferenceBasic_Pair p = (typeInferenceBasic_Pair){a, b};
}
