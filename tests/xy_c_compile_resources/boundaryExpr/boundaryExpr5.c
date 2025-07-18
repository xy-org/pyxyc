#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct boundaryExpr5_Str boundaryExpr5_Str;
typedef struct boundaryExpr5_Log boundaryExpr5_Log;

struct boundaryExpr5_Str {
    int8_t* m_data;
    size_t m_size;
};
struct boundaryExpr5_Log {
    int32_t m_level;
};

void boundaryExpr5_dtor(boundaryExpr5_Str p_s) {
}

void boundaryExpr5_write(boundaryExpr5_Str p_msg) {
}

void boundaryExpr5_test(void) {
    if ((boundaryExpr5_Log){0}.m_level <= 0) {
        boundaryExpr5_Str tmp_1_arg = (boundaryExpr5_Str){(int8_t*)"message", 7};
        boundaryExpr5_write(tmp_1_arg);
        boundaryExpr5_dtor(tmp_1_arg);
    }
}
