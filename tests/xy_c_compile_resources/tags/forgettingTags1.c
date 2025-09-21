#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct forgettingTags1_Struct forgettingTags1_Struct;
typedef struct forgettingTags1__EMPTY_STRUCT_ forgettingTags1_Tag1;
typedef struct forgettingTags1__EMPTY_STRUCT_ forgettingTags1_Tag2;
typedef struct forgettingTags1__EMPTY_STRUCT_ forgettingTags1_DefaultTag;

struct forgettingTags1_Struct {
    int32_t m_val;
};
struct forgettingTags1__EMPTY_STRUCT_ {
    char __empty_structs_are_not_allowed_in_c__;
};

void forgettingTags1_call__Struct__Tag1(forgettingTags1_Struct p_s) {
}

void forgettingTags1_call__Struct__Tag2(forgettingTags1_Struct p_s) {
}

void forgettingTags1_call__Struct__DefaultTag(forgettingTags1_Struct p_s) {
}

void forgettingTags1_test(void) {
    forgettingTags1_Struct l_s1 = {0};
    forgettingTags1_Struct l_s2 = {0};
    forgettingTags1_Struct l_s3 = {0};
    forgettingTags1_call__Struct__Tag1(l_s1);
    forgettingTags1_call__Struct__Tag2(l_s2);
    forgettingTags1_call__Struct__DefaultTag(l_s3);
    forgettingTags1_call__Struct__DefaultTag(l_s1);
    forgettingTags1_call__Struct__DefaultTag(l_s2);
    forgettingTags1_call__Struct__Tag1(l_s3);
    forgettingTags1_call__Struct__Tag2(l_s3);
}
