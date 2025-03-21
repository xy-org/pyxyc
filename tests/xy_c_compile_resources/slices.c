#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <time.h>

typedef struct slices_AllSlice slices_AllSlice;
typedef struct slices_IntSlice slices_IntSlice;
typedef struct slices_Date slices_Date;
typedef struct slices_DateSlice slices_DateSlice;

int32_t slices_max__Int(void);
int64_t slices_max__Long(void);

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

int32_t slices_max__Int(void) {
    return INT32_MAX;
}

void slices_testIntSlices(void) {
    const slices_AllSlice a = {0};
    int32_t tmp_arg0 = slices_max__Int();
    const slices_IntSlice b = {1, tmp_arg0, 1};
    const int32_t x = 10;
    const int32_t y = 1000;
    const slices_IntSlice c = {0, x, 1};
    const slices_IntSlice d = {1, x, y};
    const slices_IntSlice e = {0, slices_max__Int(), -1};
    const slices_IntSlice f = {0, x, 1};
    const slices_IntSlice g = {0, x, y};
    int32_t tmp_arg1 = slices_max__Int();
    const slices_IntSlice i = {x, tmp_arg1, y};
    const slices_IntSlice j = {x, y, 1};
    const slices_IntSlice k = {x, y, 1};
}

int64_t slices_max__Long(void) {
    return INT64_MAX;
}

void slices_testDataSlices(void) {
    const slices_Date today = {time(NULL)};
    const slices_Date tomorrow = {(slices_Date){time(NULL)}.m_unixtime + 24 * 60 * 60};
    const slices_DateSlice a = {today, tomorrow, (slices_Date){1}};
    const slices_DateSlice b = {tomorrow, today, (slices_Date){-1}};
    const slices_DateSlice d = {(slices_Date){0}, tomorrow, (slices_Date){1}};
}
