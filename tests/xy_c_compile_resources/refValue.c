#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct refValue_Data refValue_Data;

struct refValue_Data {
    char __empty_structs_are_not_allowed_in_c__;
};

float refValue_get(refValue_Data d, int32_t i) {
    return (float)(i * 2);
}

int32_t refValue_func1(refValue_Data d, int32_t i) {
    return i;
}

void refValue_test(void) {
    const int32_t a = 10;
    const int32_t* b = &a;
    const int32_t* c = &a;
    const refValue_Data d = (refValue_Data){0};
    const float e = refValue_get(d, refValue_func1(d, 10));
    const int32_t f = refValue_func1(d, 10);
}
