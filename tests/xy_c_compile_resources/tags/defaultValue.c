#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct defaultValue__EMPTY_STRUCT_ defaultValue_Tag1;
typedef struct defaultValue__EMPTY_STRUCT_ defaultValue_Tag2;
typedef struct defaultValue__EMPTY_STRUCT_ defaultValue_Data;
typedef struct defaultValue__EMPTY_STRUCT_ defaultValue_MissingTag;

struct defaultValue__EMPTY_STRUCT_ {
    char __empty_structs_are_not_allowed_in_c__;
};

void defaultValue_fun__Data__Tag1(defaultValue_Data p_data) {
}

void defaultValue_fun__Data__Tag2(defaultValue_Data p_data) {
}

void defaultValue_fun__Data__MissingTag(defaultValue_Data p_data) {
}

void defaultValue_test(void) {
    defaultValue_Data l_a = {0};
    defaultValue_fun__Data__Tag2(l_a);
    defaultValue_Data l_b = {0};
    defaultValue_fun__Data__MissingTag(l_b);
}
