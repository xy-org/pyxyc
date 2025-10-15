#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct donatedArgs7_Array donatedArgs7_Array;

struct donatedArgs7_Array {
    int32_t* m_ptr;
};

int32_t* donatedArgs7_get(donatedArgs7_Array p_arr, int32_t p_idx) {
    return p_arr.m_ptr + p_idx;
}

void donatedArgs7_modifyFunc(int32_t p_a) {
    p_a = 0;
}

void donatedArgs7_testFunc(void) {
    donatedArgs7_Array l_s = {0};
    int32_t* tmp_0_arg = donatedArgs7_get(l_s, 1);
    donatedArgs7_modifyFunc(*tmp_0_arg);
}

void donatedArgs7_testMacro1(void) {
    donatedArgs7_Array l_s = {0};
    int32_t* tmp_0_arg = donatedArgs7_get(l_s, 1);
    int32_t tmp_1_ref = *tmp_0_arg;
    {
        tmp_1_ref = 0;
    }
}

void donatedArgs7_testMacro2(donatedArgs7_Array p_s) {
    int32_t* tmp_0_arg = donatedArgs7_get(p_s, 3);
    int32_t tmp_1_ref = *tmp_0_arg;
    {
        tmp_1_ref = 0;
    }
}

void donatedArgs7_testMacro3(donatedArgs7_Array p_s) {
    int32_t* tmp_0_arg = donatedArgs7_get(p_s, 3);
    int32_t tmp_1_arg = *tmp_0_arg;
    {
        tmp_1_arg = 0;
    }
}
