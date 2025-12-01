#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct inferenceGet_Ecs inferenceGet_Ecs;
typedef struct inferenceGet_Idx inferenceGet_Idx;
typedef struct inferenceGet_Comp1 inferenceGet_Comp1;
typedef struct inferenceGet_Comp2 inferenceGet_Comp2;

struct inferenceGet_Ecs {
    void* m_mem;
};
struct inferenceGet_Idx {
    int32_t m_id;
};
struct inferenceGet_Comp1 {
    float m_field1;
};
struct inferenceGet_Comp2 {
    double m_field2;
};

void* inferenceGet_get__2(inferenceGet_Ecs p_ecs, int32_t p_num) {
    return 0;
}

void inferenceGet_test(inferenceGet_Idx p_idx) {
    inferenceGet_Ecs l_ecs = {0};
    inferenceGet_Comp1* tmp_0_arg = (inferenceGet_Comp1*)inferenceGet_get__2(l_ecs, p_idx.m_id);
    const inferenceGet_Comp1 l_v1 = *tmp_0_arg;
}
