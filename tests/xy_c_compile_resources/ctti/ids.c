#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct ids_Type1 ids_Type1;
typedef struct ids_Type2 ids_Type2;

#define XY_IDS_TYPE1_ID 0u
#define XY_IDS_TYPE2_ID 1u

struct ids_Type1 {
    int32_t m_val;
};
struct ids_Type2 {
    float m_val;
};

void ids_test(void) {
    const uint32_t l_a = XY_IDS_TYPE1_ID;
    const uint32_t l_b = XY_IDS_TYPE2_ID;
}
