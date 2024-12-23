#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <time.h>

typedef struct slices_AllSlice slices_AllSlice;
typedef struct slices_IntSlice slices_IntSlice;
typedef struct slices_Date slices_Date;
typedef struct slices_DateSlice slices_DateSlice;

int32_t slices_max__int(void);
slices_Date slices_max__Date(void);

struct slices_AllSlice {
    char __empty_structs_are_not_allowed_in_c__;
};
struct slices_IntSlice {
    int32_t m_start;
    int32_t m_end;
    int32_t m_step;
};
struct slices_Date {
    int64_t m_unixtime;
};
struct slices_DateSlice {
    slices_Date m_start;
    slices_Date m_end;
    slices_Date m_step;
};

int32_t slices_max__int(void) {
    return INT32_MAX;
}

void slices_testIntSlices(void) {
    const slices_AllSlice a = (slices_AllSlice){0};
    int32_t tmp_arg0 = slices_max__int();
    const slices_IntSlice b = (slices_IntSlice){1, tmp_arg0, 1};
    const int32_t x = 10;
    const int32_t y = 1000;
    const slices_IntSlice c = (slices_IntSlice){0, x, 1};
    const slices_IntSlice d = (slices_IntSlice){1, x, y};
    const slices_IntSlice e = (slices_IntSlice){0, slices_max__int(), -1};
    const slices_IntSlice f = (slices_IntSlice){0, x, 1};
    const slices_IntSlice g = (slices_IntSlice){0, x, y};
    int32_t tmp_arg1 = slices_max__int();
    const slices_IntSlice i = (slices_IntSlice){x, tmp_arg1, y};
    const slices_IntSlice j = (slices_IntSlice){x, y, 1};
    const slices_IntSlice k = (slices_IntSlice){x, y, 1};
}

int64_t slices_max__long(void) {
    return INT64_MAX;
}

void slices_testDataSlices(void) {
    const slices_Date today = (slices_Date){time(NULL)};
    const slices_Date tomorrow = (slices_Date){(slices_Date){time(NULL)}.m_unixtime + 24 * 60 * 60};
    const slices_DateSlice a = (slices_DateSlice){today, tomorrow, (slices_Date){1}};
    const slices_DateSlice b = (slices_DateSlice){tomorrow, today, (slices_Date){-1}};
    const slices_DateSlice d = (slices_DateSlice){(slices_Date){0}, tomorrow, (slices_Date){1}};
}
