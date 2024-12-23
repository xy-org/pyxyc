#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct opOverloading_MyInt opOverloading_MyInt;
typedef struct opOverloading_Pair opOverloading_Pair;

struct opOverloading_MyInt {
    int32_t m_num;
};
struct opOverloading_Pair {
    opOverloading_MyInt m_a;
    opOverloading_MyInt m_b;
};

int32_t opOverloading_cmp__with__MyInt__MyInt(opOverloading_MyInt a, opOverloading_MyInt b) {
    return opOverloading_sub(a, b).m_num;
}

opOverloading_MyInt opOverloading_add(opOverloading_MyInt a, opOverloading_MyInt b) {
    return (opOverloading_MyInt){a.m_num + b.m_num};
}

opOverloading_MyInt opOverloading_sub(opOverloading_MyInt a, opOverloading_MyInt b) {
    return (opOverloading_MyInt){a.m_num - b.m_num};
}

opOverloading_MyInt opOverloading_mul(opOverloading_MyInt a, opOverloading_MyInt b) {
    return (opOverloading_MyInt){a.m_num * b.m_num};
}

opOverloading_MyInt opOverloading_div(opOverloading_MyInt a, opOverloading_MyInt b) {
    return (opOverloading_MyInt){a.m_num / b.m_num};
}

int32_t opOverloading_cmpMyInts(void) {
    const opOverloading_MyInt a = (opOverloading_MyInt){0};
    const opOverloading_MyInt b = (opOverloading_MyInt){1};
    if (opOverloading_cmp__with__MyInt__MyInt(a, b) > 0) {
        return 1;
    }
    if (opOverloading_cmp__with__MyInt__MyInt(opOverloading_mul(a, (opOverloading_MyInt){0}), (opOverloading_MyInt){1}) > 0) {
        return 2;
    }
    if (opOverloading_cmp__with__MyInt__MyInt(opOverloading_div(a, (opOverloading_MyInt){1}), b) <= 0) {
        return 3;
    }
    return 0;
}

int32_t opOverloading_cmp__with__MyInt__int(opOverloading_MyInt p1, int32_t n) {
    return p1.m_num - n;
}

opOverloading_MyInt opOverloading_cmp__with__Pair__Pair(opOverloading_Pair p1, opOverloading_Pair p2) {
    return opOverloading_sub(p1.m_a, p2.m_a);
}

int32_t opOverloading_cmpPairs(void) {
    const opOverloading_Pair p1 = (opOverloading_Pair){0, 1};
    const opOverloading_Pair p2 = (opOverloading_Pair){2, 3};
    if (opOverloading_cmp__with__MyInt__int(opOverloading_cmp__with__Pair__Pair(p1, p2), 0) > 0) {
        return 1;
    }
    return 0;
}
