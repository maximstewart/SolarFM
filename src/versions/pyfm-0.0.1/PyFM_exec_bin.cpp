#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
using namespace std;

int main() {
    chdir("/opt/Pytop/");
    system("python3 PyTop.py");
return 0;
}
