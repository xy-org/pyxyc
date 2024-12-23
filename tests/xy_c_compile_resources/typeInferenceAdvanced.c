#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct typeInferenceAdvanced_Pair typeInferenceAdvanced_Pair;

struct typeInferenceAdvanced_Pair {
    int32_t m_a;
    int32_t m_b;
};

int32_t typeInferenceAdvanced_rng(void) {
    return 0;
}

int64_t typeInferenceAdvanced_myadd(int32_t a, int32_t b) {
    return 0;
}

typeInferenceAdvanced_Pair typeInferenceAdvanced_ctorPair(void) {
    return (typeInferenceAdvanced_Pair){0, 1};
}

float typeInferenceAdvanced_transform(int64_t num) {
    return 0;
}

void typeInferenceAdvanced_func(void) {
    const int32_t a = typeInferenceAdvanced_rng();
    const int32_t b = typeInferenceAdvanced_rng() + 10;
    const float c = typeInferenceAdvanced_transform(typeInferenceAdvanced_myadd(a, b));
    const typeInferenceAdvanced_Pair d = typeInferenceAdvanced_ctorPair();
    const double e = 1 + 1.1718;
    const float ef = 2.1718f;
    const double pi = 1 + 1.0 + 1.14f;
}
