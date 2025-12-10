#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t entrypoint_priority_main(void) {
    return 0;
}

int32_t entrypoint_priority_moreImportant(void) {
    return 0;
}

int main(int argc, char** argv) {
    const int32_t tmp_0_err = entrypoint_priority_moreImportant();
    if ((bool)tmp_0_err) {
        return tmp_0_err;
    }
    return 0;
}
