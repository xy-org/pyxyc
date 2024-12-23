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

void fieldsof_print(fieldsof_FieldDesc d) {
}

void fieldsof_printFields(fieldsof_FieldDesc* fieldsPtr, size_t fieldsLen) {
    for (size_t i = 0; i < fieldsLen; ++i) {
        fieldsof_print(fieldsPtr[i]);
    }
}

void fieldsof_test1(void) {
    const fieldsof_MyStruct s = (fieldsof_MyStruct){0};
    const fieldsof_FieldDesc descs[3] = {(fieldsof_FieldDesc){sizeof(s.m_a)}, (fieldsof_FieldDesc){sizeof(s.m_b)}, (fieldsof_FieldDesc){sizeof(s.m_c)}};
}

void fieldsof_test2(void) {
    const fieldsof_MyStruct s = (fieldsof_MyStruct){0};
    fieldsof_FieldDesc tmp_arg0[3] = {(fieldsof_FieldDesc){sizeof(s.m_a)}, (fieldsof_FieldDesc){sizeof(s.m_b)}, (fieldsof_FieldDesc){sizeof(s.m_c)}};
    for (size_t tmp_iter1 = 0; tmp_iter1 < 3; ++tmp_iter1) {
    }
}

void fieldsof_test3(void) {
    const fieldsof_MyStruct s = (fieldsof_MyStruct){0};
    fieldsof_FieldDesc tmp_arg0[3] = {(fieldsof_FieldDesc){sizeof(s.m_a)}, (fieldsof_FieldDesc){sizeof(s.m_b)}, (fieldsof_FieldDesc){sizeof(s.m_c)}};
    fieldsof_printFields(tmp_arg0, 3);
}
