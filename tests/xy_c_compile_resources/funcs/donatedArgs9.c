#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct donatedArgs9_Array donatedArgs9_Array;

struct donatedArgs9_Array {
    void* m_mem;
};

void donatedArgs9_dtor(donatedArgs9_Array p_a) {
}

void donatedArgs9_append(donatedArgs9_Array p_a, void* p_elemPtr) {
}

void donatedArgs9_test(void) {
    donatedArgs9_Array l_a = {0};
    int32_t tmp_0_addrof = 0;
    donatedArgs9_append(l_a, &tmp_0_addrof);
    donatedArgs9_dtor(l_a);
}
