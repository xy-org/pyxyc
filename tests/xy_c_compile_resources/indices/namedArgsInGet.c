#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct namedArgsInGet_Data namedArgsInGet_Data;

struct namedArgsInGet_Data {
    void* m_mem;
};

int32_t namedArgsInGet_get(namedArgsInGet_Data p_data, int32_t p_idx, int32_t p_default) {
    return p_idx + p_default;
}

void namedArgsInGet_test(void) {
    namedArgsInGet_Data l_d = {0};
    const int32_t l_a = namedArgsInGet_get(l_d, 5, 0);
    const int32_t l_b = namedArgsInGet_get(l_d, 10, -5);
}
