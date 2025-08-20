#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void instantiateCtypes_test(void) {
    const ptrdiff_t l_a = {100};
    const point_t l_b = {.x = 10, .y = 20};
    const ptrdiff_t l_d = {200};
    const struct iovec l_e = {.iov_base = 0, .iov_len = 0};
}
