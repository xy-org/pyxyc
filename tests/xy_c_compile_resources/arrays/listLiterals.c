#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct listLiterals_List listLiterals_List;

struct listLiterals_List {
    void* m_mem;
};

listLiterals_List listLiterals_copy(listLiterals_List* p_l) {
    return (listLiterals_List){0};
}

void listLiterals_append(listLiterals_List* p_l, int32_t p_num) {
}

void listLiterals_dtor(listLiterals_List* p_l) {
}

void listLiterals_test(void) {
    listLiterals_List tmp_0_comp = (listLiterals_List){0};
    listLiterals_append(&tmp_0_comp, 1);
    listLiterals_append(&tmp_0_comp, 2);
    listLiterals_append(&tmp_0_comp, 3);
    listLiterals_List l_list1 = tmp_0_comp;
    listLiterals_List tmp_1_comp = listLiterals_copy(&l_list1);
    listLiterals_append(&tmp_1_comp, 3);
    listLiterals_append(&tmp_1_comp, 2);
    listLiterals_append(&tmp_1_comp, 1);
    listLiterals_List l_list2 = tmp_1_comp;
    listLiterals_dtor(&l_list2);
    listLiterals_dtor(&l_list1);
}
