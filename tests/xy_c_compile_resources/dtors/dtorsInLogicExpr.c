#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

typedef struct dtorsInLogicExpr_Str dtorsInLogicExpr_Str;

struct dtorsInLogicExpr_Str {
    void* m_addr;
};

void dtorsInLogicExpr_dtor(dtorsInLogicExpr_Str p_s) {
    free(p_s.m_addr);
}

dtorsInLogicExpr_Str dtorsInLogicExpr_createStr1(void) {
    return (dtorsInLogicExpr_Str){0};
}

dtorsInLogicExpr_Str dtorsInLogicExpr_createStr2(void) {
    return (dtorsInLogicExpr_Str){0};
}

dtorsInLogicExpr_Str dtorsInLogicExpr_copy(dtorsInLogicExpr_Str p_s) {
    return (dtorsInLogicExpr_Str){0};
}

bool dtorsInLogicExpr_startswith(dtorsInLogicExpr_Str p_str, dtorsInLogicExpr_Str p_prefix) {
    return strcmp(p_str.m_addr, p_prefix.m_addr);
}

bool dtorsInLogicExpr_test(dtorsInLogicExpr_Str p_s1, dtorsInLogicExpr_Str p_s2) {
    dtorsInLogicExpr_Str tmp_0_arg = dtorsInLogicExpr_createStr1();
    dtorsInLogicExpr_Str tmp_1_arg = dtorsInLogicExpr_copy(tmp_0_arg);
    bool tmp_2_arg = dtorsInLogicExpr_startswith(tmp_1_arg, p_s1);
    bool tmp_8_shortcircuit = tmp_2_arg;
    if (!tmp_8_shortcircuit) {
        dtorsInLogicExpr_Str tmp_6_arg = dtorsInLogicExpr_createStr2();
        dtorsInLogicExpr_Str tmp_7_arg = dtorsInLogicExpr_copy(tmp_6_arg);
        tmp_8_shortcircuit = dtorsInLogicExpr_startswith(tmp_7_arg, p_s2);
        dtorsInLogicExpr_dtor(tmp_7_arg);
        tmp_7_arg = (dtorsInLogicExpr_Str){0};
        dtorsInLogicExpr_dtor(tmp_6_arg);
        tmp_6_arg = (dtorsInLogicExpr_Str){0};
    }
    bool tmp_9_res = tmp_8_shortcircuit;
    dtorsInLogicExpr_dtor(tmp_1_arg);
    dtorsInLogicExpr_dtor(tmp_0_arg);
    return tmp_9_res;
}
