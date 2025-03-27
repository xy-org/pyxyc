#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct listLiterals_List listLiterals_List;

struct listLiterals_List {
    char __empty_structs_are_not_allowed_in_c__;
};

void listLiterals_push(listLiterals_List* p_l, int32_t p_num) {
}

void listLiterals_dtor(listLiterals_List* p_l) {
}

void listLiterals_test(void) {
    listLiterals_List tmp_0_arr_comp = (listLiterals_List){0};
    listLiterals_push(&tmp_0_arr_comp, 1);
    listLiterals_push(&tmp_0_arr_comp, 2);
    listLiterals_push(&tmp_0_arr_comp, 3);
    const listLiterals_List l_list1 = tmp_0_arr_comp;
    listLiterals_List tmp_1_arg = l_list1;
    listLiterals_push(&tmp_1_arg, 3);
    listLiterals_push(&tmp_1_arg, 2);
    listLiterals_push(&tmp_1_arg, 1);
    const listLiterals_List l_list2 = tmp_1_arg;
    listLiterals_dtor(&l_list2);
    listLiterals_dtor(&l_list1);
}
