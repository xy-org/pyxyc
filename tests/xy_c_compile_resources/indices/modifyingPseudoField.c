#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct modifyingPseudoField_String modifyingPseudoField_String;
typedef struct modifyingPseudoField__EMPTY_STRUCT_ modifyingPseudoField_SizeField;

struct modifyingPseudoField_String {
    int8_t* m_addr;
    uint64_t m_packedSize;
};
struct modifyingPseudoField__EMPTY_STRUCT_ {
    char __empty_structs_are_not_allowed_in_c__;
};

void modifyingPseudoField_set(modifyingPseudoField_String* p_str, uint64_t p_new) {
    p_str->m_packedSize = (uint64_t)p_new << 1 | (p_str->m_packedSize & (uint64_t)1);
}

void modifyingPseudoField_test1(int32_t p_x, modifyingPseudoField_String p_sep) {
    modifyingPseudoField_String l_iter = {0};
    l_iter.m_addr += (uint64_t)p_x + (uint64_t)(p_sep.m_packedSize >> 1);
    uint64_t tmp_0_arg = (uint64_t)(l_iter.m_packedSize >> 1);
    modifyingPseudoField_set(&l_iter, tmp_0_arg - ((uint64_t)p_x + (uint64_t)(p_sep.m_packedSize >> 1)));
}

void modifyingPseudoField_test2(int32_t p_x, modifyingPseudoField_String p_sep) {
    modifyingPseudoField_String l_iter = {0};
    if (!((uint64_t)(p_sep.m_packedSize >> 1) != 0)) {
        abort();
    }
    uint64_t tmp_0_arg = (uint64_t)(l_iter.m_packedSize >> 1);
    modifyingPseudoField_set(&l_iter, tmp_0_arg * ((uint64_t)p_x / (uint64_t)(p_sep.m_packedSize >> 1)));
}

void modifyingPseudoField_test3(int32_t p_x, modifyingPseudoField_String p_sep) {
    modifyingPseudoField_String l_iter = {0};
    uint64_t tmp_0_arg = (uint64_t)(l_iter.m_packedSize >> 1);
    if (!((uint64_t)p_x * (uint64_t)(p_sep.m_packedSize >> 1) != 0)) {
        abort();
    }
    modifyingPseudoField_set(&l_iter, tmp_0_arg / ((uint64_t)p_x * (uint64_t)(p_sep.m_packedSize >> 1)));
}
