#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef int32_t enumsAndFlags_Status;

#define enumsAndFlags_Status__pending 0
#define enumsAndFlags_Status__canceled 1
#define enumsAndFlags_Status__processed 2

void enumsAndFlags_printStatus(enumsAndFlags_Status st) {
    if (st == enumsAndFlags_Status__pending) {
    } else if (st == enumsAndFlags_Status__canceled) {
    } else if (st == enumsAndFlags_Status__processed) {
    }
}

void enumsAndFlags_testEnums(int32_t a) {
    const enumsAndFlags_Status orderStatus = enumsAndFlags_Status__pending;
    enumsAndFlags_printStatus(orderStatus);
    enumsAndFlags_printStatus(enumsAndFlags_Status__processed);
    enumsAndFlags_Status st = enumsAndFlags_Status__canceled;
    if (a > 0) {
        st = enumsAndFlags_Status__processed;
    }
    enumsAndFlags_printStatus(st);
}
