#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t exitWithError_main(void) {
    return 2;
}

int main(int argc, char** argv) {
    const int32_t tmp_0_err = exitWithError_main();
    if ((bool)tmp_0_err) {
        return tmp_0_err;
    }
    return 0;
}
