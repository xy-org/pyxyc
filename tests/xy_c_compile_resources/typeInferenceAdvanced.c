#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct typeInferenceAdvanced_Pair typeInferenceAdvanced_Pair;

struct typeInferenceAdvanced_Pair {
    int32_t a;
    int32_t b;
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
    int32_t a = typeInferenceAdvanced_rng();
    int32_t b = typeInferenceAdvanced_rng() + 10;
    float c = typeInferenceAdvanced_transform(typeInferenceAdvanced_myadd(a, b));
    typeInferenceAdvanced_Pair d = typeInferenceAdvanced_ctorPair();
    double e = 1 + 1.1718;
    float ef = 2.1718f;
    double pi = 1 + 1.0 + 1.14f;
}
