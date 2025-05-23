#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct fieldsof_MyStruct fieldsof_MyStruct;
typedef struct fieldsof_SubStruct fieldsof_SubStruct;
typedef struct fieldsof_FieldDesc fieldsof_FieldDesc;

struct fieldsof_SubStruct {
    fieldsof_MyStruct* m_d;
};
struct fieldsof_MyStruct {
    int32_t m_a;
    float m_b;
    fieldsof_SubStruct m_c;
};
struct fieldsof_FieldDesc {
    size_t m_size;
};

void fieldsof_print(fieldsof_FieldDesc p_d) {
}

void fieldsof_printFields(fieldsof_FieldDesc* p_fieldsPtr, size_t p_fieldsLen) {
    for (size_t i = 0; i < p_fieldsLen; ++i) {
        fieldsof_print(p_fieldsPtr[i]);
    }
}

void fieldsof_test1(void) {
    const fieldsof_MyStruct l_s = {0};
    const fieldsof_FieldDesc l_descs[3] = {(fieldsof_FieldDesc){sizeof(l_s.m_a)}, (fieldsof_FieldDesc){sizeof(l_s.m_b)}, (fieldsof_FieldDesc){sizeof(l_s.m_c)}};
}

void fieldsof_test2(void) {
    const fieldsof_MyStruct l_s = {0};
    fieldsof_FieldDesc tmp_0_arg[3] = {(fieldsof_FieldDesc){sizeof(l_s.m_a)}, (fieldsof_FieldDesc){sizeof(l_s.m_b)}, (fieldsof_FieldDesc){sizeof(l_s.m_c)}};
    for (size_t tmp_1_iter = 0; tmp_1_iter < 3; ++tmp_1_iter) {
    }
}

void fieldsof_test3(void) {
    const fieldsof_MyStruct l_s = {0};
    fieldsof_FieldDesc tmp_0_arg[3] = {(fieldsof_FieldDesc){sizeof(l_s.m_a)}, (fieldsof_FieldDesc){sizeof(l_s.m_b)}, (fieldsof_FieldDesc){sizeof(l_s.m_c)}};
    fieldsof_printFields(tmp_0_arg, (size_t)3);
}
