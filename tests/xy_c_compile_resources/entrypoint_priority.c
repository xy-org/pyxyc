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
    entrypoint_priority_moreImportant();
    return 0;
}
