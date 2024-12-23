#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t submodules_sub_callme(void) {
    return 0;
}

int32_t submodules_main(void) {
    return submodules_sub_callme();
}

int main(int argc, char** argv) {
    const int res = submodules_main();
    return res;
}
