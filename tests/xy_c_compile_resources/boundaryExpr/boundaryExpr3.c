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

void boundaryExpr3_info(boundaryExpr3_Logger log, bool logged) {
}

bool boundaryExpr3_doLog(boundaryExpr3_Logger log, boundaryExpr3_Msg msg) {
    return true;
}

boundaryExpr3_Msg boundaryExpr3_longComputation(void) {
    return (boundaryExpr3_Msg){0};
}

void boundaryExpr3_test(void) {
    const boundaryExpr3_Logger log = {0};
    bool tmp1 = 0;
    if (log.m_enabled) {
        tmp1 = boundaryExpr3_doLog(log, boundaryExpr3_longComputation());
    } else {
        tmp1 = false;
    }
    boundaryExpr3_info(log, tmp1);
}
