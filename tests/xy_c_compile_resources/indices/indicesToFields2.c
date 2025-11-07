#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct indicesToFields2_SoA indicesToFields2_SoA;
typedef struct indicesToFields2_Data indicesToFields2_Data;

struct indicesToFields2_SoA {
    void* m_mem;
};
struct indicesToFields2_Data {
    int32_t m_a;
    uint64_t m_b;
};

void indicesToFields2_set(indicesToFields2_SoA p_soa, int32_t p_idx, uint64_t p_size, uint64_t p_offset, void* p_valPtr) {
}

void indicesToFields2_test1(indicesToFields2_SoA* p_soa) {
    uint64_t tmp_0_arg = sizeof(int32_t);
    uint64_t tmp_1_arg = offsetof(indicesToFields2_Data, m_a);
    int32_t tmp_2_addrof = 10;
    indicesToFields2_set(*p_soa, 10, tmp_0_arg, tmp_1_arg, &tmp_2_addrof);
    uint64_t tmp_3_arg = sizeof(uint64_t);
    uint64_t tmp_4_arg = offsetof(indicesToFields2_Data, m_b);
    uint64_t tmp_5_addrof = 10ull;
    indicesToFields2_set(*p_soa, 12, tmp_3_arg, tmp_4_arg, &tmp_5_addrof);
}

void indicesToFields2_test2(indicesToFields2_Data* p_data) {
    p_data->m_a = 10;
    p_data->m_b = 10ull;
}
