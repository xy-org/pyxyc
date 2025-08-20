#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct fieldExternalTypeInit_Data fieldExternalTypeInit_Data;

struct fieldExternalTypeInit_Data {
    ptrdiff_t m_ext;
    int32_t m_a;
};

void fieldExternalTypeInit_test(void) {
    const fieldExternalTypeInit_Data l_data = {(ptrdiff_t){0}, 10};
}
