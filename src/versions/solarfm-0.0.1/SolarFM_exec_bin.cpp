#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
using namespace std;

int main() {
    chdir("/opt/");
    system("python solarfm.zip");
return 0;
}
