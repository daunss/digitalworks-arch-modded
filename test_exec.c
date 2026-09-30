
#include <windows.h>
#include <stdio.h>
int main() {
    HINSTANCE h = ShellExecuteA(NULL, NULL, "digitalworks", "--undo", NULL, SW_SHOWNORMAL);
    printf("ShellExecute returned: %ld
", (long)h);
    return 0;
}
