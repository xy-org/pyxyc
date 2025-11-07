#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct indicesToFields1_SoA indicesToFields1_SoA;
typedef struct indicesToFields1_Data indicesToFields1_Data;

struct indicesToFields1_SoA {
    void* m_mem;
};
struct indicesToFields1_Data {
    int32_t m_a;
    uint64_t m_b;
};

void* indicesToFields1_get__SoA__Int__Field__Ulong__Ulong(indicesToFields1_SoA p_soa, int32_t p_idx, uint64_t p_size, uint64_t p_offset) {
    return 0;
}

int32_t indicesToFields1_test1(void) {
    indicesToFields1_SoA l_soa = {0};
    uint64_t tmp_0_arg = sizeof(int32_t);
    int32_t* tmp_1_arg = (int32_t*)indicesToFields1_get__SoA__Int__Field__Ulong__Ulong(l_soa, 10, tmp_0_arg, offsetof(indicesToFields1_Data, m_a));
    const int32_t l_a = *tmp_1_arg;
    uint64_t tmp_2_arg = sizeof(uint64_t);
    uint64_t* tmp_3_arg = (uint64_t*)indicesToFields1_get__SoA__Int__Field__Ulong__Ulong(l_soa, 12, tmp_2_arg, offsetof(indicesToFields1_Data, m_b));
    const int32_t l_b = *tmp_3_arg;
    return l_a + l_b;
}

int32_t indicesToFields1_test2(void) {
    indicesToFields1_Data l_data = {0};
    const int32_t l_a = l_data.m_a;
    const int32_t l_b = l_data.m_b;
    return l_a + l_b;
}
