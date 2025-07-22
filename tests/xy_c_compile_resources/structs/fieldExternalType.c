#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <termios.h>
#include <unistd.h>

typedef struct fieldExternalType_Data fieldExternalType_Data;

struct fieldExternalType_Data {
    int32_t m_num;
    struct termios m_ext;
    float m_flt;
};

void fieldExternalType_test(void) {
    const fieldExternalType_Data l_a = {0};
    const fieldExternalType_Data l_b = {0, {0}, 2.0f};
}
