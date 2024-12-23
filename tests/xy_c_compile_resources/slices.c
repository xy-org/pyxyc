#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <time.h>

typedef struct slices_AllSlice slices_AllSlice;
typedef struct slices_IntSlice slices_IntSlice;
typedef struct slices_Date slices_Date;
typedef struct slices_DateSlice slices_DateSlice;

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

slices_AllSlice slices_slice__with(void) {
    return (slices_AllSlice){0};
}

int32_t slices_max__with__int(void) {
    return INT32_MAX;
}

slices_IntSlice slices_slice__with__int__int__int(int32_t start, int32_t end, int32_t step) {
    return (slices_IntSlice){start, end, step};
}

slices_IntSlice slices_slice__with__int__int(int32_t end, int32_t step) {
    return (slices_IntSlice){0, end, step};
}

slices_IntSlice slices_slice__with__int(int32_t step) {
    return (slices_IntSlice){0, slices_max__with__int(), step};
}

void slices_testIntSlices(void) {
    const slices_AllSlice a = slices_slice__with();
    const slices_IntSlice b = slices_slice__with__int__int__int(1, slices_max__with__int(), 1);
    const int32_t x = 10;
    const int32_t y = 1000;
    const slices_IntSlice c = slices_slice__with__int__int__int(0, x, 1);
    const slices_IntSlice d = slices_slice__with__int__int__int(1, x, y);
    const slices_IntSlice e = slices_slice__with__int(-1);
    const slices_IntSlice f = slices_slice__with__int__int(x, 1);
    const slices_IntSlice g = slices_slice__with__int__int(x, y);
    const slices_IntSlice i = slices_slice__with__int__int__int(x, slices_max__with__int(), y);
    const slices_IntSlice j = slices_slice__with__int__int__int(x, y, 1);
    const slices_IntSlice k = slices_slice__with__int__int__int(x, y, 1);
}

int64_t slices_max__with__long(void) {
    return INT64_MAX;
}

slices_Date slices_max__with__Date(void) {
    return (slices_Date){slices_max__with__long()};
}

slices_DateSlice slices_slice__with__Date__Date__Date(slices_Date start, slices_Date end, slices_Date step) {
    return (slices_DateSlice){start, end, step};
}

slices_DateSlice slices_slice__with__Date__Date(slices_Date end, slices_Date step) {
    return (slices_DateSlice){(slices_Date){0}, end, step};
}

slices_DateSlice slices_slice__with__Date(slices_Date step) {
    return (slices_DateSlice){(slices_Date){0}, slices_max__with__Date(), step};
}

slices_Date slices_today(void) {
    return (slices_Date){time(NULL)};
}

slices_Date slices_tomorrow(void) {
    return (slices_Date){slices_today().m_unixtime + 24 * 60 * 60};
}

void slices_testDataSlices(void) {
    const slices_Date today = slices_today();
    const slices_Date tomorrow = slices_tomorrow();
    const slices_DateSlice a = slices_slice__with__Date__Date__Date(today, tomorrow, (slices_Date){1});
    const slices_DateSlice b = slices_slice__with__Date__Date__Date(tomorrow, today, (slices_Date){-1});
    const slices_DateSlice d = slices_slice__with__Date__Date(tomorrow, (slices_Date){1});
}
