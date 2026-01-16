#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct indexStructInit_Map indexStructInit_Map;

struct indexStructInit_Map {
    void* m_ptr;
};

int32_t indexStructInit_get(indexStructInit_Map* p_map, int32_t p_key) {
    return 0;
}

void indexStructInit_set(indexStructInit_Map* p_map, int32_t p_key, int32_t p_val) {
}

void indexStructInit_test(void) {
    indexStructInit_Map tmp_0 = (indexStructInit_Map){0};
    indexStructInit_set(&tmp_0, 1, 0);
    indexStructInit_set(&tmp_0, 10, 1);
    indexStructInit_set(&tmp_0, 100, 2);
    indexStructInit_Map l_log10 = tmp_0;
}
