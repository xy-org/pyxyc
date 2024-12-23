#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t entrypoint_main(void) {
    return 0;
}

int main(int argc, char** argv) {
    const int res = entrypoint_main();
    return res;
}
