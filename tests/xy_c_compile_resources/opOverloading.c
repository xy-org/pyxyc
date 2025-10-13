#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct opOverloading_MyInt opOverloading_MyInt;
typedef struct opOverloading_Pair opOverloading_Pair;

opOverloading_MyInt opOverloading_sub(opOverloading_MyInt p_a, opOverloading_MyInt p_b);

struct opOverloading_MyInt {
    int32_t m_num;
};
struct opOverloading_Pair {
    opOverloading_MyInt m_a;
    opOverloading_MyInt m_b;
};

bool opOverloading_cmpGt__MyInt__MyInt(opOverloading_MyInt p_a, opOverloading_MyInt p_b) {
    return opOverloading_sub(p_a, p_b).m_num > 0;
}

bool opOverloading_cmpLe(opOverloading_MyInt p_a, opOverloading_MyInt p_b) {
    return p_a.m_num <= p_b.m_num;
}

opOverloading_MyInt opOverloading_add(opOverloading_MyInt p_a, opOverloading_MyInt p_b) {
    return (opOverloading_MyInt){p_a.m_num + p_b.m_num};
}

opOverloading_MyInt opOverloading_sub(opOverloading_MyInt p_a, opOverloading_MyInt p_b) {
    return (opOverloading_MyInt){p_a.m_num - p_b.m_num};
}

opOverloading_MyInt opOverloading_mul(opOverloading_MyInt p_a, opOverloading_MyInt p_b) {
    return (opOverloading_MyInt){p_a.m_num * p_b.m_num};
}

opOverloading_MyInt opOverloading_div(opOverloading_MyInt p_a, opOverloading_MyInt p_b) {
    if (!(p_b.m_num != 0)) {
        abort();
    }
    return (opOverloading_MyInt){p_a.m_num / p_b.m_num};
}

int32_t opOverloading_cmpMyInts(void) {
    const opOverloading_MyInt l_a = {0};
    const opOverloading_MyInt l_b = {1};
    if (opOverloading_cmpGt__MyInt__MyInt(l_a, l_b)) {
        return 1;
    }
    if (opOverloading_cmpGt__MyInt__MyInt(opOverloading_mul(l_a, (opOverloading_MyInt){0}), (opOverloading_MyInt){1})) {
        return 2;
    }
    if (opOverloading_cmpLe(opOverloading_div(l_a, (opOverloading_MyInt){1}), l_b)) {
        return 3;
    }
    return 0;
}

int32_t opOverloading_cmp(opOverloading_MyInt p_p1, int32_t p_n) {
    return p_p1.m_num - p_n;
}

bool opOverloading_cmpGt__Pair__Pair(opOverloading_Pair p_p1, opOverloading_Pair p_p2) {
    return opOverloading_cmpGt__MyInt__MyInt(p_p1.m_a, p_p2.m_a);
}

int32_t opOverloading_cmpPairs(void) {
    const opOverloading_Pair l_p1 = {(opOverloading_MyInt){0}, (opOverloading_MyInt){1}};
    const opOverloading_Pair l_p2 = {(opOverloading_MyInt){2}, (opOverloading_MyInt){3}};
    if (opOverloading_cmpGt__Pair__Pair(l_p1, l_p2)) {
        return 1;
    }
    return 0;
}
