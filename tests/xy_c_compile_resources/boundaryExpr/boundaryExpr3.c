#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct boundaryExpr3_Logger boundaryExpr3_Logger;
typedef struct boundaryExpr3_Msg boundaryExpr3_Msg;

struct boundaryExpr3_Logger {
    bool m_enabled;
};
struct boundaryExpr3_Msg {
    char __empty_structs_are_not_allowed_in_c__;
};

void boundaryExpr3_info(boundaryExpr3_Logger p_log, bool p_logged) {
}

bool boundaryExpr3_doLog(boundaryExpr3_Logger p_log, boundaryExpr3_Msg p_msg) {
    return true;
}

boundaryExpr3_Msg boundaryExpr3_longComputation(void) {
    return (boundaryExpr3_Msg){0};
}

void boundaryExpr3_test(void) {
    const boundaryExpr3_Logger l_log = {0};
    bool tmp_1 = 0;
    if (l_log.m_enabled) {
        tmp_1 = boundaryExpr3_doLog(l_log, boundaryExpr3_longComputation());
    } else {
        tmp_1 = false;
    }
    boundaryExpr3_info(l_log, tmp_1);
}
