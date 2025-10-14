#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct for7_Array for7_Array;

struct for7_Array {
    void* m_ptr;
};

void for7_append(for7_Array* p_arr, void* p_elemPtr, size_t p_elemSize) {
}

void for7_test(void) {
    for7_Array l_arr = {0};
    for (size_t i = 0; i < (size_t)10; ++i) {
        int32_t tmp_0_addrof = 0;
        for7_append(&l_arr, &tmp_0_addrof, sizeof(int32_t));
    }
}
