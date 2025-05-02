#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <time.h>

typedef struct slices__EMPTY_STRUCT_ slices_AllSlice;
typedef struct slices_IntSlice slices_IntSlice;
typedef struct slices_Date slices_Date;
typedef struct slices_DateSlice slices_DateSlice;

int32_t slices_max__Int(void);
int64_t slices_max__Long(void);

struct slices__EMPTY_STRUCT_ {
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
    const slices_AllSlice l_a = {0};
    int32_t tmp_0_arg = slices_max__Int();
    const slices_IntSlice l_b = {1, tmp_0_arg, 1};
    const int32_t l_x = 10;
    const int32_t l_y = 1000;
    const slices_IntSlice l_c = {0, l_x, 1};
    const slices_IntSlice l_d = {1, l_x, l_y};
    const slices_IntSlice l_e = {0, slices_max__Int(), -1};
    const slices_IntSlice l_f = {0, l_x, 1};
    const slices_IntSlice l_g = {0, l_x, l_y};
    int32_t tmp_1_arg = slices_max__Int();
    const slices_IntSlice l_i = {l_x, tmp_1_arg, l_y};
    const slices_IntSlice l_j = {l_x, l_y, 1};
    const slices_IntSlice l_k = {l_x, l_y, 1};
}

int64_t slices_max__Long(void) {
    return INT64_MAX;
}

void slices_testDataSlices(void) {
    const slices_Date l_today = {time(NULL)};
    const slices_Date l_tomorrow = {(slices_Date){time(NULL)}.m_unixtime + 24 * 60 * 60};
    const slices_DateSlice l_a = {l_today, l_tomorrow, (slices_Date){1}};
    const slices_DateSlice l_b = {l_tomorrow, l_today, (slices_Date){-1}};
    const slices_DateSlice l_d = {(slices_Date){0}, l_tomorrow, (slices_Date){1}};
}
