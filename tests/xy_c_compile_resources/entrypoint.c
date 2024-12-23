#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t entrypoint_main(void) {
    return 0;
}

int main(int argc, char** argv) {
    int res = entrypoint_main();
    return res;
}
