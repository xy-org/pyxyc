#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void cmpNumConsts_test(void) {
    const bool l_a = (int8_t)0xFA == 0xFA;
    const bool l_b = (int8_t)0xFB == (int16_t)0xFB;
    const bool l_c = (int16_t)0xFAFC == 0xFAFC;
    const bool l_d = 0xFAu == (uint8_t)0xFA;
    const bool l_e = (uint8_t)0xFA == (uint16_t)0xFAB;
    const bool l_f = (uint32_t)-1 == 0xFFFFFFFFu;
}
