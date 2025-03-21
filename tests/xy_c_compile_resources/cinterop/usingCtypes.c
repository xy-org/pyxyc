#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <time.h>

void usingCtypes_func(void);

clock_t usingCtypes_timeFunc(void) {
    const clock_t l_start = clock();
    usingCtypes_func();
    const clock_t l_finish = clock();
    return (l_finish - l_start) / c.CLOCKS_PER_SEC;
}

void usingCtypes_func(void) {
}
