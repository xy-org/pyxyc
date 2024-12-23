#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct guards_ErrorCode guards_ErrorCode;

struct guards_ErrorCode {
    int32_t m_code;
};

int32_t guards_guards1(int32_t a, int32_t b) {
    return 0;
}

int32_t guards_guards2(int32_t a) {
    return 0;
}

bool guards_to(guards_ErrorCode ec) {
    return ec.m_code != 0;
}

guards_ErrorCode guards_guards4(int32_t a, int32_t b, int32_t* __c) {
    *__c = 0;
    return (guards_ErrorCode){0};
}

int32_t guards_test(int32_t a, int32_t b) {
    int32_t res = 0;
    if (!(a > b)) {
        abort();
    }
    res += guards_guards1(a, b);
    size_t tmp_arg0 = sizeof(a);
    if (!(tmp_arg0 > sizeof(b))) {
        abort();
    }
    res += guards_guards2(a);
    return res;
}
