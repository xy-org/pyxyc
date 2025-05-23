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

int64_t typeInferenceAdvanced_myadd(int32_t p_a, int32_t p_b) {
    return 0;
}

typeInferenceAdvanced_Pair typeInferenceAdvanced_ctorPair(void) {
    return (typeInferenceAdvanced_Pair){0, 1};
}

float typeInferenceAdvanced_transform(int64_t p_num) {
    return 0;
}

void typeInferenceAdvanced_func(void) {
    const int32_t l_a = typeInferenceAdvanced_rng();
    const int32_t l_b = typeInferenceAdvanced_rng() + 10;
    const float l_c = typeInferenceAdvanced_transform(typeInferenceAdvanced_myadd(l_a, l_b));
    const typeInferenceAdvanced_Pair l_d = typeInferenceAdvanced_ctorPair();
    const double l_e = 1 + 1.1718;
    const float l_efp = 2.1718f;
    const double l_pi = 1 + 1.0 + 1.14;
}
