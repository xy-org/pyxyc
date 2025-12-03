#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct compoundOperators_Str compoundOperators_Str;
typedef struct compoundOperators__EMPTY_STRUCT_ compoundOperators_SizeField;

struct compoundOperators_Str {
    void* m_addr;
    uint64_t m_sizeFlags;
};
struct compoundOperators__EMPTY_STRUCT_ {
    char __empty_structs_are_not_allowed_in_c__;
};

void compoundOperators_test(compoundOperators_Str* p_s, uint64_t p_param) {
    const uint64_t l_size = p_s->m_sizeFlags >> 1;
    p_s->m_sizeFlags = (uint64_t)p_param << 1 | (p_s->m_sizeFlags & (uint64_t)1);
    uint64_t tmp_0_arg = (uint64_t)(p_s->m_sizeFlags >> 1);
    p_s->m_sizeFlags = (uint64_t)(tmp_0_arg + 10) << 1 | (p_s->m_sizeFlags & (uint64_t)1);
}
