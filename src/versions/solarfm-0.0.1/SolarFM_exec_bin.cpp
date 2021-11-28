#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
using namespace std;

int main() {
    chdir("/opt/SolarFM/");
    system("python .");
return 0;
}
