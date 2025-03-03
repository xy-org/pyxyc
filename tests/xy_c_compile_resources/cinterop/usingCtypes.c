#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <time.h>

void usingCtypes_func(void);

clock_t usingCtypes_timeFunc(void) {
    const clock_t start = clock();
    usingCtypes_func();
    const clock_t finish = clock();
    return (finish - start) / c.CLOCKS_PER_SEC;
}

void usingCtypes_func(void) {
}
