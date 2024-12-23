#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef int32_t enums_Status;

#define enums_Status__pending 0
#define enums_Status__canceled 1
#define enums_Status__processed 2

void enums_printStatus(enums_Status st) {
    if (st == enums_Status__pending) {
    } else if (st == enums_Status__canceled) {
    } else if (st == enums_Status__processed) {
    }
}

void enums_testEnums(int32_t a) {
    const enums_Status orderStatus = enums_Status__pending;
    enums_printStatus(orderStatus);
    enums_printStatus(enums_Status__processed);
    enums_Status st = enums_Status__canceled;
    if (a > 0) {
        st = enums_Status__processed;
    }
    enums_printStatus(st);
}
