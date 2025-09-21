#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct cmpTypes_Struct1 cmpTypes_Struct1;
typedef struct cmpTypes_Struct2 cmpTypes_Struct2;
typedef struct cmpTypes_Tag1 cmpTypes_Tag1;
typedef struct cmpTypes_Tag2 cmpTypes_Tag2;

struct cmpTypes_Struct1 {
    int32_t m_val;
};
struct cmpTypes_Struct2 {
    int32_t m_val;
};
struct cmpTypes_Tag1 {
    int32_t m_val;
};
struct cmpTypes_Tag2 {
    int32_t m_val;
};

void cmpTypes_test(void) {
    const int32_t l_a = 0;
    const int32_t l_b = 0;
    const int32_t l_c = -1;
    const int32_t l_d = -1;
    const int32_t l_e = 1;
    const int32_t l_f = -1;
    const int32_t l_g = -1;
    const int32_t l_h = 0;
    const int32_t l_i = -1;
    const int32_t l_j = 1;
}
