#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct funcs_A funcs_A;

struct funcs_A {
    int32_t xy_num;
};

funcs_A funcs_double(funcs_A a) {
    return (funcs_A){a.xy_num * 2};
}

void funcs_doubleInout(funcs_A* a) {
    a->xy_num *= 2;
}
